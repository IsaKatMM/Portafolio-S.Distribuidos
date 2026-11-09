import json
import sqlite3
from datetime import datetime
import paho.mqtt.client as mqtt

# CONFIGURACIÓN MQTT
BROKER = "localhost"
PORT = 1883
DB_NAME = "telemetria.db"

def inicializar_base_datos():
    """Crea la base de datos y las tablas necesarias si no existen."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabla para GPS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gps_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT,
            lat REAL,
            lng REAL,
            speed REAL,
            timestamp TEXT
        )
    ''')
    
    # Tabla para Temperatura
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS temp_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT,
            temperature REAL,
            unit TEXT,
            timestamp TEXT
        )
    ''')
    
    # Tabla para Combustible
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fuel_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT,
            fuel_level REAL,
            unit TEXT,
            timestamp TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Base de datos e índices inicializados correctamente.")

def al_recibir_mensaje(client, userdata, mensaje):
    """Callback ejecutado cada vez que llega un mensaje MQTT."""
    topic = mensaje.topic
    payload = json.loads(mensaje.payload.decode('utf-8'))
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # --- Procesar datos de GPS ---
    if "/gps" in topic:
        cursor.execute('''
            INSERT INTO gps_data (vehicle_id, lat, lng, speed, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            payload["vehicle_id"],
            payload["lat"],
            payload["lng"],
            payload["speed"],
            payload["timestamp"]
        ))
        
    # --- Procesar datos de Temperatura ---
    elif "/temperatura" in topic:
        temp = payload.get("temperature", 0)
        vehicle_id = payload.get("vehicle_id")
        
        # Evaluar regla de alerta
        if temp > 4:
            print(f"⚠️  [ALERTA TEMPERATURA] Vehículo: {vehicle_id} | Temp actual: {temp} °C (Supera los 4°C)")
            
        cursor.execute('''
            INSERT INTO temp_data (vehicle_id, temperature, unit, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (
            vehicle_id,
            temp,
            payload.get("unit", "celsius"),
            payload.get("timestamp")
        ))
        
    # --- Procesar datos de Combustible ---
    elif "/combustible" in topic:
        fuel = payload.get("fuel_level", 0)
        vehicle_id = payload.get("vehicle_id")
        
        # Evaluar regla de alerta
        if fuel < 20:
            print(f"⚠️  [ALERTA COMBUSTIBLE] Vehículo: {vehicle_id} | Nivel: {fuel}% (Bajo el 20%)")
            
        cursor.execute('''
            INSERT INTO fuel_data (vehicle_id, fuel_level, unit, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (
            vehicle_id,
            fuel,
            payload.get("unit", "percent"),
            payload.get("timestamp")
        ))
        
    conn.commit()
    conn.close()

def principal():
    """Función principal para iniciar el suscriptor MQTT."""
    inicializar_base_datos()
    
    client = mqtt.Client()
    client.on_message = al_recibir_mensaje
    
    client.connect(BROKER, PORT, 60)
    
    # Suscripción a topics mediante comodines MQTT
    client.subscribe("flota/+/gps")
    client.subscribe("flota/+/temperatura")
    client.subscribe("flota/+/combustible")
    
    print("Suscriptor activo. Escuchando los topics flota/+/... (Presiona Ctrl+C para salir)\n")
    
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo suscriptor...")
        client.disconnect()

if __name__ == "__main__":
    principal()