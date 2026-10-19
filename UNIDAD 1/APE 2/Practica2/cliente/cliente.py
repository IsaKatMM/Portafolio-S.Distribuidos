import os
import time

RUTA_ENTRADA = os.path.join("..", "compartida", "entrada_servidor.txt")
RUTA_SALIDA = os.path.join("..", "compartida", "salida_servidor.txt")

def contar_lineas(ruta):
    """cuenta las lineas no vacías de un archivo"""
    if not os.path.exists(ruta):
        return 0
    with open(ruta, "r", encoding="utf-8") as f:
        return len([l.strip() for l in f.readlines() if l.strip()])

def enviar_mensaje(mensaje):
    lineas_salida_iniciales = contar_lineas(RUTA_SALIDA)

    
    print(f"\n Enviando mensaje a '{RUTA_ENTRADA}'...")
    with open(RUTA_ENTRADA, "a", encoding="utf-8") as f:
        f.write(mensaje + "\n")
        
    print("Mensaje enviado correctamente.")
    print("Esperando respuesta del servidor...")
    
    
    intentos = 10 #maximo 10s
    respuesta = ""
    
    while intentos > 0:
        time.sleep(1)
        if contar_lineas(RUTA_SALIDA) > lineas_salida_iniciales:
            with open(RUTA_SALIDA, "r", encoding="utf-8") as f:
                lineas = [l.strip() for l in f.readlines() if l.strip()]
                respuesta = lineas[-1] # Lee la última línea añadida
            break
        intentos -= 1

    if respuesta:
        print(f"Respuesta del servidor: {respuesta}")
    else:
        print("Tiempo de espera agotado. El servidor no respondió.")

def ejecutar_cliente():
    print("CLIENTE INICIADO ")
    print("Escribe 'salir' para finalizar el programa.\n")
    
    while True:
        mensaje = input("\nIngrese un mensaje: ").strip()
        
        if mensaje.lower() == 'salir':
            print("Cerrando el cliente...")
            break
            
        if not mensaje:
            print("El mensaje no puede estar vacío.")
            continue

        enviar_mensaje(mensaje)

if __name__ == "__main__":
    ejecutar_cliente()