import json
import pika
import paho.mqtt.client as mqtt

# Configuración de conexiones
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
RABBITMQ_HOST = "localhost"

def configurar_rabbitmq():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        
        # Declarar las colas como duraderas (durable=True)
        channel.queue_declare(queue="cola.gps.telemetria", durable=True)
        channel.queue_declare(queue="cola.alertas.temperatura", durable=True)
        channel.queue_declare(queue="cola.combustible.nivel", durable=True)
        
        print("Colas de RabbitMQ verificadas y creadas exitosamente.")
        return connection, channel
    except Exception as e:
        print(f"Error conectando a RabbitMQ: {e}")
        exit(1)

def al_recibir_mensaje_mqtt(client, userdata, msg):
    channel = userdata["rabbitmq_channel"]
    topic = msg.topic
    
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
    except Exception as e:
        print(f"Error al decodificar mensaje JSON: {e}")
        return

    # Propiedad para hacer que el mensaje sea persistente en RabbitMQ
    properties = pika.BasicProperties(delivery_mode=2)

    # 1. Enrutamiento GPS
    if "/gps" in topic:
        channel.basic_publish(
            exchange='',
            routing_key='cola.gps.telemetria',
            body=json.dumps(payload),
            properties=properties
        )
        print(f"[GPS Enviado] {payload['vehicle_id']} -> cola.gps.telemetria")

    # 2. Enrutamiento Temperatura (Solo alertas > 4 °C)
    elif "/temperatura" in topic:
        temp = payload.get("temperature", 0)
        if temp > 4:
            alerta = {
                "type": "TEMP_ALERT",
                "message": "Temperatura excedida"
            }
            alerta.update(payload)
            
            channel.basic_publish(
                exchange='',
                routing_key='cola.alertas.temperatura',
                body=json.dumps(alerta),
                properties=properties
            )
            print(f" [ALERTA TEMP Enviada] {payload['vehicle_id']} ({temp} °C) -> cola.alertas.temperatura")

    # 3. Enrutamiento Combustible (Solo alertas < 20%)
    elif "/combustible" in topic:
        fuel = payload.get("fuel_level", 0)
        if fuel < 20:
            alerta = {
                "type": "FUEL_LOW",
                "message": "Combustible bajo"
            }
            alerta.update(payload)
            
            channel.basic_publish(
                exchange='',
                routing_key='cola.combustible.nivel',
                body=json.dumps(alerta),
                properties=properties
            )
            print(f"[ALERTA FUEL Enviada] {payload['vehicle_id']} ({fuel}%) -> cola.combustible.nivel")

def main():
    conn_rabbit, canal_rabbit = configurar_rabbitmq()

    # Estructura de compatibilidad para paho-mqtt v2
    try:
        mqtt_client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, 
            client_id="MQTT_RabbitMQ_Bridge", 
            userdata={"rabbitmq_channel": canal_rabbit}
        )
    except AttributeError:
        mqtt_client = mqtt.Client(
            client_id="MQTT_RabbitMQ_Bridge", 
            userdata={"rabbitmq_channel": canal_rabbit}
        )

    mqtt_client.on_message = al_recibir_mensaje_mqtt

    print("Conectando al broker MQTT...")
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
    
    # Suscribirse a la jerarquía global de topics
    mqtt_client.subscribe("flota/#", qos=1)
    print("Bridge MQTT-RabbitMQ en ejecución. Escuchando 'flota/#'...")

    try:
        mqtt_client.loop_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo el Puente...")
        mqtt_client.disconnect()
        conn_rabbit.close()

if __name__ == "__main__":
    main()