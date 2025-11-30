import pika, json, asyncio, time
from Websocket.application.websocket_usecase import WebSocketUseCase

# Configuración de reconexión
MAX_RETRIES = None  # None = infinitos reintentos
INITIAL_RETRY_DELAY = 5  # segundos
MAX_RETRY_DELAY = 60  # segundos máximo entre reintentos

def consume_messages(usecase: WebSocketUseCase, rabbitmq_config: dict):
    host = rabbitmq_config["host"]
    user = rabbitmq_config["user"]
    password = rabbitmq_config["pass"]
    keys = rabbitmq_config["routing_keys"]

    bindings = [
        {"exchange": "amq.topic", "queue": "sensor.TFLuna",     "routing_key": keys["tf"],   "sensor": "TF-Luna"},
        {"exchange": "amq.topic", "queue": "sensor.IMX477",     "routing_key": keys["imx"],  "sensor": "IMX477"},
        {"exchange": "amq.topic", "queue": "sensor.inclinacion", "routing_key": keys["mpu"],  "sensor": "MPU6050"},
        {"exchange": "amq.topic", "queue": "sensor.hc", "routing_key": keys["hc"],  "sensor": "HC-SR04"}
    ]

    def callback(sensor_name):
        def inner(ch, method, properties, body):
            try:
                message = json.loads(body)
                print(f"📥 Recibido de {sensor_name}: {message}")
                asyncio.run(usecase.send_message({"sensor": sensor_name, "data": message}))
            except Exception as e:
                print(f"Error procesando mensaje de {sensor_name}:", e)
        return inner

    def connect_and_consume():
        credentials = pika.PlainCredentials(user, password)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host, credentials=credentials))
        channel = connection.channel()

        # Declarar exchange una sola vez (amq.topic es predefinido, pero por si usas otro)
        channel.exchange_declare(exchange="amq.topic", exchange_type="topic", durable=True)

        for binding in bindings:
            queue = binding["queue"]
            routing_key = binding["routing_key"]
            sensor_name = binding["sensor"]

            channel.queue_declare(queue=queue, durable=True)
            channel.queue_bind(exchange="amq.topic", queue=queue, routing_key=routing_key)
            channel.basic_consume(queue=queue, on_message_callback=callback(sensor_name), auto_ack=True)

        print("📡 Conectado a RabbitMQ. Escuchando mensajes...")
        channel.start_consuming()

    # Loop de reconexión con backoff exponencial
    retry_count = 0
    retry_delay = INITIAL_RETRY_DELAY

    while True:
        try:
            connect_and_consume()
        except pika.exceptions.AMQPConnectionError as e:
            retry_count += 1
            if MAX_RETRIES is not None and retry_count > MAX_RETRIES:
                print(f"❌ Se alcanzó el máximo de reintentos ({MAX_RETRIES}). Deteniendo consumer.")
                break
            
            print(f"⚠️ No se pudo conectar a RabbitMQ: {e}")
            print(f"🔄 Reintentando en {retry_delay} segundos... (intento #{retry_count})")
            time.sleep(retry_delay)
            
            # Backoff exponencial con límite
            retry_delay = min(retry_delay * 2, MAX_RETRY_DELAY)
        except Exception as e:
            retry_count += 1
            print(f"❌ Error inesperado en RabbitMQ consumer: {e}")
            print(f"🔄 Reintentando en {retry_delay} segundos... (intento #{retry_count})")
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, MAX_RETRY_DELAY)
        except KeyboardInterrupt:
            print("🛑 Consumer detenido manualmente.")
            break
