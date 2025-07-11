import pika, json, asyncio
from Websocket.application.websocket_usecase import WebSocketUseCase

def consume_messages(usecase: WebSocketUseCase, rabbitmq_config: dict):
    ROUTING_KEY_TF = rabbitmq_config["routing_keys"]["tf"]
    ROUTING_KEY_IMX477 = rabbitmq_config["routing_keys"]["imx"]
    RABBITMQ_HOST = rabbitmq_config["host"]
    RABBITMQ_USER = rabbitmq_config["user"]
    RABBITMQ_PASS = rabbitmq_config["pass"]

    def callback(ch, method, properties, body):
        try:
            message = json.loads(body)
            sensor_name = "TF-Luna" if method.routing_key == ROUTING_KEY_TF else "IMX477"
            asyncio.run(usecase.send_message({"sensor": sensor_name, "data": message}))
        except Exception as e:
            print("❌ Error procesando mensaje:", e)

    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST, credentials=credentials))
    channel = connection.channel()

    for key in [ROUTING_KEY_TF, ROUTING_KEY_IMX477]:
        channel.queue_declare(queue=key, durable=True)
        channel.queue_bind(exchange="amq.topic", queue=key, routing_key=key)
        channel.basic_consume(queue=key, on_message_callback=callback, auto_ack=True)

    print("📡 Escuchando RabbitMQ...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.close()
