import json
import os
import time
import random
from datetime import datetime
import paho.mqtt.client as mqtt

# CONFIGURACIÓN MQTT
BROKER = os.getenv("MQTT_BROKER", "localhost")
PORT = 1883
VEHICULOS = ["VH-001", "VH-002", "VH-003"]

def al_conectar(client, userdata, flags, rc, properties=None):
    """Callback al conectarse al broker MQTT."""
    print(f"[{datetime.now().isoformat()}] Conectado al broker Mosquitto (rc={rc})")

def simular_gps():
    """Genera coordenadas y velocidad."""
    base_lat = -2.1709
    base_lng = -79.9224
    return {
        "lat": round(base_lat + random.uniform(-0.01, 0.01), 6),
        "lng": round(base_lng + random.uniform(-0.01, 0.01), 6),
        "speed": round(random.uniform(20, 80), 1)
    }

def simular_temperatura():
    """Genera temperatura (-5 °C a 8 °C para forzar valores normales y alertas > 4°C)."""
    return {
        "temperature": round(random.uniform(-5, 8), 1),
        "unit": "celsius"
    }

def simular_combustible():
    """Genera nivel de combustible (10% a 100% para forzar alertas < 20%)."""
    return {
        "fuel_level": round(random.uniform(10, 100), 1),
        "unit": "percent"
    }

def principal():
    # Uso de CallbackAPIVersion.VERSION2 para compatibilidad con Paho MQTT v2+
    cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    cliente.on_connect = al_conectar
    
    cliente.connect(BROKER, PORT, 60)
    cliente.loop_start()
    
    print("Iniciando simulador de sensores IoT (9 mensajes por ronda)...")
    
    try:
        while True:
            for vehiculo in VEHICULOS:
                timestamp = datetime.now().isoformat()
                
                # Datos de los 3 sensores
                lecturas = {
                    "gps": simular_gps(),
                    "temperatura": simular_temperatura(),
                    "combustible": simular_combustible()
                }
                
                for sensor, datos in lecturas.items():
                    topic = f"flota/{vehiculo}/{sensor}"
                    payload = {
                        "vehicle_id": vehiculo,
                        "timestamp": timestamp,
                        **datos
                    }
                    # Publicación obligatoria con QoS = 1
                    cliente.publish(topic, json.dumps(payload), qos=1)
                
                print(f"[{timestamp}] 3 sensores publicados para {vehiculo}")
                time.sleep(1)  # Pausa entre vehículos
                
            print("--- Ronda completada (9 mensajes enviados) ---\n")
            time.sleep(5)  # Pausa entre rondas de la flota
            
    except KeyboardInterrupt:
        print("\nDeteniendo simulador...")
        cliente.loop_stop()
        cliente.disconnect()

if __name__ == "__main__":
    principal()