import json
import pika
import paho.mqtt.client as mqtt

# CONFIGURACIÓN
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
RABBITMQ_HOST = "localhost"

def configurar_rabbitmq():
    """Establece conexión con RabbitMQ y declara las 3 colas duraderas."""
    conexion = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    canal = conexion.channel()
    
    # Declaración de colas durables
    canal.queue_declare(queue="cola.gps.telemetria", durable=True)
    canal.queue_declare(queue="cola.alertas.temperatura", durable=True)
    canal.queue_declare(queue="cola.combustible.nivel", durable=True)
    
    print("Colas RabbitMQ declaradas correctamente (durables).")
    return conexion, canal

def al_recibir_mensaje(cliente, userdata, mensaje):
    """Filtra y enruta los mensajes MQTT a las colas correspondientes en RabbitMQ."""
    topic = mensaje.topic
    payload = json.loads(mensaje.payload.decode('utf-8'))
    canal_rabbit = userdata["rabbitmq_channel"]
    
    # 1. Enrutamiento de todos los mensajes GPS
    if topic.endswith("/gps"):
        canal_rabbit.basic_publish(
            exchange='',
            routing_key='cola.gps.telemetria',
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2)  # Mensajes persistentes
        )
        print(f"[RABBITMQ] GPS de {payload.get('vehicle_id')} enviado a 'cola.gps.telemetria'")

    # 2. Enrutamiento de Alerta de Temperatura (> 4 °C)
    elif topic.endswith("/temperatura"):
        temp = payload.get("temperature", 0)
        if temp > 4:
            alerta = {
                "tipo_alerta": "TEMPERATURA_ALTA",
                "mensaje": "Temperatura superior a 4 °C",
                **payload
            }
            canal_rabbit.basic_publish(
                exchange='',
                routing_key='cola.alertas.temperatura',
                body=json.dumps(alerta),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            print(f"⚠️ [RABBITMQ] Alerta Temp ({temp} °C) enviada a 'cola.alertas.temperatura'")

    # 3. Enrutamiento de Alerta de Combustible (< 20 %)
    elif topic.endswith("/combustible"):
        fuel = payload.get("fuel_level", 100)
        if fuel < 20:
            alerta = {
                "tipo_alerta": "COMBUSTIBLE_BAJO",
                "mensaje": "Nivel de combustible inferior a 20 %",
                **payload
            }
            canal_rabbit.basic_publish(
                exchange='',
                routing_key='cola.combustible.nivel',
                body=json.dumps(alerta),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            print(f"⚠️ [RABBITMQ] Alerta Combustible ({fuel} %) enviada a 'cola.combustible.nivel'")

def principal():
    conexion_rabbit, canal_rabbit = configurar_rabbitmq()
    
    # Pasar el canal de RabbitMQ a userdata con la versión 2 de la API de callbacks
    cliente = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        userdata={"rabbitmq_channel": canal_rabbit}
    )
    cliente.on_message = al_recibir_mensaje
    
    cliente.connect(MQTT_BROKER, MQTT_PORT, 60)
    cliente.subscribe("flota/#")
    
    print("Puente MQTT-RabbitMQ activo. Escuchando 'flota/#'...")
    
    try:
        cliente.loop_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo Puente...")
        cliente.disconnect()
        conexion_rabbit.close()

if __name__ == "__main__":
    principal()