import os
import time

RUTA_ENTRADA = os.path.join("..", "compartida", "entrada_servidor.txt")
RUTA_SALIDA = os.path.join("..", "compartida", "salida_servidor.txt")

def inicializar_archivos():
    os.makedirs(os.path.dirname(RUTA_ENTRADA), exist_ok=True)
    if not os.path.exists(RUTA_ENTRADA):
        open(RUTA_ENTRADA, "w", encoding="utf-8").close() #se permite tildes y ñ
    if not os.path.exists(RUTA_SALIDA):
        open(RUTA_SALIDA, "w", encoding="utf-8").close()

def procesar_servidor():
    inicializar_archivos()
    lineas_procesadas = 0
    
    print("SERVIDOR INICIADO Y EN ESPERA DE MENSAJES ")
    print(f"Monitoreando la entrada: {RUTA_ENTRADA}\n")
    
    while True:
        try:
            if os.path.exists(RUTA_ENTRADA):
                with open(RUTA_ENTRADA, "r", encoding="utf-8") as f: #abre la ruta de entrada en modo lectura
                    lineas = [l.strip() for l in f.readlines() if l.strip()]
                
                
                if len(lineas) > lineas_procesadas:
                    
                    for i in range(lineas_procesadas, len(lineas)):
                        nuevo_mensaje = lineas[i]
                        print(f"Nuevo mensaje detectado: '{nuevo_mensaje}'")
                        
                        resultado = nuevo_mensaje.upper()
                        
                        #
                        with open(RUTA_SALIDA, "a", encoding="utf-8") as f_salida:
                            f_salida.write(resultado + "\n")
                        
                        print(f"Mensaje procesado y guardado: '{resultado}'")
                    
                    lineas_procesadas = len(lineas)

        except Exception as e:
            print(f"Error: {e}")
            
        time.sleep(1)

if __name__ == "__main__":
    procesar_servidor()