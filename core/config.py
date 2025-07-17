from dotenv import load_dotenv
import os

load_dotenv()

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")
ROUTING_KEY_TF = os.getenv("ROUTING_KEY_TF")
ROUTING_KEY_IMX477 = os.getenv("ROUTING_KEY_IMX477")
ROUTING_KEY_MPU6050 = os.getenv("ROUTING_KEY_MPU6050")

def get_rabbitmq_config():
    return {
        "host": RABBITMQ_HOST,
        "user": RABBITMQ_USER,
        "pass": RABBITMQ_PASS,
        "routing_keys": {
            "tf": ROUTING_KEY_TF,
            "imx": ROUTING_KEY_IMX477,
            "mpu": ROUTING_KEY_MPU6050
        }
    }
