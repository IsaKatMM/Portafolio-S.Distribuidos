import json
import sqlite3
from datetime import datetime
import paho.mqtt.client as mqtt

BROKER = "localhost"
PUERTO = 1883
DB_NAME = "telemetria.db"

def inicializar_base_datos():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabla GPS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gps_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id TEXT,
        lat REAL,
        lng REAL,
        speed REAL,
        timestamp TEXT
    )
    """)
    
    # Tabla Temperatura
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS temp_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id TEXT,
        temperature REAL,
        unit TEXT,
        timestamp TEXT
    )
    """)
    
    # Tabla Combustible
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fuel_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id TEXT,
        fuel_level REAL,
        unit TEXT,
        timestamp TEXT
    )
    """)
    
    conn.commit()
    conn.close()
    print("Base de datos SQLite inicializada correctamente.")

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Suscriptor conectado. Suscribiendo a topics 'flota/+/...'")
        # Suscripción mediante wildcards (+)
        client.subscribe("flota/+/gps", qos=1)
        client.subscribe("flota/+/temperatura", qos=1)
        client.subscribe("flota/+/combustible", qos=1)
    else:
        print(f"Error de conexión: {rc}")

def al_recibir_mensaje(client, userdata, msg):
    topic = msg.topic
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
    except Exception as e:
        print(f"Error decodificando JSON: {e}")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if "/gps" in topic:
        cursor.execute("""
            INSERT INTO gps_data (vehicle_id, lat, lng, speed, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (payload["vehicle_id"], payload["lat"], payload["lng"], payload["speed"], payload["timestamp"]))
        
    elif "/temperatura" in topic:
        temp = payload.get("temperature", 0)
        if temp > 4:
            print(f"[ALERTA TEMPERATURA] Vehículo {payload['vehicle_id']}: {temp} °C (Supera los 4.0 °C)")
        
        cursor.execute("""
            INSERT INTO temp_data (vehicle_id, temperature, unit, timestamp)
            VALUES (?, ?, ?, ?)
        """, (payload["vehicle_id"], payload["temperature"], payload["unit"], payload["timestamp"]))
        
    elif "/combustible" in topic:
        fuel = payload.get("fuel_level", 0)
        if fuel < 20:
            print(f" [ALERTA COMBUSTIBLE] Vehículo {payload['vehicle_id']}: {fuel}% (Bajo el 20%)")
            
        cursor.execute("""
            INSERT INTO fuel_data (vehicle_id, fuel_level, unit, timestamp)
            VALUES (?, ?, ?, ?)
        """, (payload["vehicle_id"], payload["fuel_level"], payload["unit"], payload["timestamp"]))

    conn.commit()
    conn.close()

def main():
    inicializar_base_datos()
    
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="Suscriptor_SQLite")
    except AttributeError:
        client = mqtt.Client(client_id="Suscriptor_SQLite")

    client.on_connect = on_connect
    client.on_message = al_recibir_mensaje

    client.connect(BROKER, PUERTO)
    print("Suscriptor activo. Escuchando topics en bucle continuo...")
    
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo suscriptor...")
        client.disconnect()

if __name__ == "__main__":
    main()