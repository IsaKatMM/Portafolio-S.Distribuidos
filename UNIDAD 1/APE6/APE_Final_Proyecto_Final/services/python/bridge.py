import json
import pika
import paho.mqtt.client as mqtt
import os

# CONFIGURACIÓN (Usa variables de entorno, por defecto localhost)
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = 1883
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.getenv("RABBITMQ_USERNAME", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASSWORD", "admin123")

def configurar_rabbitmq():
    credenciales = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parametros = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credenciales)
    conexion = pika.BlockingConnection(parametros)
    canal = conexion.channel()
    canal.queue_declare(queue="cola.gps.telemetria", durable=True)
    canal.queue_declare(queue="cola.alertas.temperatura", durable=True)
    canal.queue_declare(queue="cola.combustible.nivel", durable=True)
    canal.queue_declare(queue="cola.notificaciones", durable=True)
    return conexion, canal

def al_recibir_mensaje(cliente, userdata, mensaje):
    topic = mensaje.topic
    payload = json.loads(mensaje.payload.decode('utf-8'))
    canal_rabbit = userdata["rabbitmq_channel"]
    
    if topic.endswith("/gps"):
        canal_rabbit.basic_publish(exchange='', routing_key='cola.gps.telemetria', body=json.dumps(payload), properties=pika.BasicProperties(delivery_mode=2))
        print(f"[RABBITMQ] GPS enviado")

    elif topic.endswith("/temperatura"):
        temp = payload.get("temperature", 0)
        if temp > 4:
            alerta = {"tipo_alerta": "TEMPERATURA_ALTA", **payload}
            canal_rabbit.basic_publish(exchange='', routing_key='cola.alertas.temperatura', body=json.dumps(alerta), properties=pika.BasicProperties(delivery_mode=2))
            print(f"⚠️ [RABBITMQ] Alerta Temp enviada")

    elif topic.endswith("/combustible"):
        fuel = payload.get("fuel_level", 100)
        if fuel < 20:
            alerta = {"tipo_alerta": "COMBUSTIBLE_BAJO", **payload}
            canal_rabbit.basic_publish(exchange='', routing_key='cola.combustible.nivel', body=json.dumps(alerta), properties=pika.BasicProperties(delivery_mode=2))
            print(f"⚠️ [RABBITMQ] Alerta Combustible enviada")

def principal():
    conexion_rabbit, canal_rabbit = configurar_rabbitmq()
    cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, userdata={"rabbitmq_channel": canal_rabbit})
    cliente.on_message = al_recibir_mensaje
    cliente.connect(MQTT_BROKER, MQTT_PORT, 60)
    cliente.subscribe("flota/#")
    print(f"Puente activo. MQTT: {MQTT_BROKER}, Rabbit: {RABBITMQ_HOST}")
    cliente.loop_forever()

if __name__ == "__main__":
    principal()
