import json
import random
import time
from datetime import datetime
import paho.mqtt.client as mqtt

# Configuración del broker MQTT
BROKER = "localhost"
PUERTO = 1883
VEHICULOS = ["VH-001", "VH-002", "VH-003"]

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"[{datetime.now().isoformat()}] Conectado exitosamente al broker MQTT (rc={rc})")
    else:
        print(f"Error de conexión con código {rc}")

def simular_gps():
    base_lat = -2.1709
    base_lng = -79.9224
    latitud = base_lat + random.uniform(-0.01, 0.01)
    longitud = base_lng + random.uniform(-0.01, 0.01)
    velocidad = random.uniform(20, 80)
    return {
        "lat": round(latitud, 6),
        "lng": round(longitud, 6),
        "speed": round(velocidad, 1)
    }

def simular_temperatura():
    temperatura = random.uniform(-5, 8)
    return {
        "temperature": round(temperatura, 1),
        "unit": "celsius"
    }

def simular_combustible():
    combustible = random.uniform(10, 100)
    return {
        "fuel_level": round(combustible, 1),
        "unit": "percent"
    }

def main():
    # Compatibilidad con Paho-MQTT v2
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="Simulador_Sensores")
    except AttributeError:
        client = mqtt.Client(client_id="Simulador_Sensores")

    client.on_connect = on_connect
    client.connect(BROKER, PUERTO)
    client.loop_start()

    print("Iniciando simulador de sensores IoT...")
    try:
        while True:
            for vehiculo in VEHICULOS:
                timestamp = datetime.now().isoformat()
                
                # 1. GPS
                data_gps = {"vehicle_id": vehiculo, "timestamp": timestamp}
                data_gps.update(simular_gps())
                client.publish(f"flota/{vehiculo}/gps", json.dumps(data_gps), qos=1)

                # 2. Temperatura
                data_temp = {"vehicle_id": vehiculo, "timestamp": timestamp}
                data_temp.update(simular_temperatura())
                client.publish(f"flota/{vehiculo}/temperatura", json.dumps(data_temp), qos=1)

                # 3. Combustible
                data_fuel = {"vehicle_id": vehiculo, "timestamp": timestamp}
                data_fuel.update(simular_combustible())
                client.publish(f"flota/{vehiculo}/combustible", json.dumps(data_fuel), qos=1)

                print(f"[{timestamp}] Publicados 3 sensores para {vehiculo}")
                time.sleep(5)
                
    except KeyboardInterrupt:
        print("\nDeteniendo simulador...")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()