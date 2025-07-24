import pika, json, asyncio
from Websocket.application.websocket_usecase import WebSocketUseCase

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

    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host, credentials=credentials))
    channel = connection.channel()

    for binding in bindings:
        exchange = binding["exchange"]
        queue = binding["queue"]
        routing_key = binding["routing_key"]
        sensor_name = binding["sensor"]

        channel.exchange_declare(exchange=exchange, exchange_type="topic", durable=True)

        channel.queue_declare(queue=queue, durable=True)
        channel.queue_bind(exchange=exchange, queue=queue, routing_key=routing_key)

        channel.basic_consume(queue=queue, on_message_callback=callback(sensor_name), auto_ack=True)

    print("📡 Escuchando RabbitMQ...")

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.close()
