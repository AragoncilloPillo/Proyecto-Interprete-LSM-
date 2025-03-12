'''
import subprocess
import re
import cv2
import time
import os

# Configuración
PORT = "COM7"  # Puerto serial de la Pico
IMAGE_FOLDER = "c:/Users/Rodrigo-Lap/Desktop/Modelo Camara"  # Ruta de la carpeta donde se guardan las imágenes

def run_pico_script():
    """Ejecuta el script bootPI.py en la Raspberry Pi Pico y captura el nombre de la imagen."""
    print("Ejecutando bootPI.py en la Pico...")
    command = f"ampy --port {PORT} run bootPI.py"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    # Captura la salida del comando
    output = result.stdout
    print("Salida de la Pico:", output)
    
    # Busca el nombre de la imagen en la salida
    match = re.search(r"Imagen guardada como: (image_\d+\.jpg)", output)
    if match:
        image_name = match.group(1)
        print(f"Nombre de la imagen capturada: {image_name}")
        return image_name
    else:
        raise ValueError("No se pudo encontrar el nombre de la imagen en la salida.")
    
def download_image(image_name):
    """Descarga la imagen desde la Pico a la computadora."""
    local_image_name = "la_ptm.jpg"  # Nombre local de la imagen
    #print(f"Nombre local de la imagen {local_image_name}")
    print(f"Descargando {image_name} desde la Pico...")
    command = f"ampy --port {PORT} get {image_name} {local_image_name}"
    subprocess.run(command, shell=True)
    
    # Verifica si la imagen se descargó correctamente
    if os.path.exists(local_image_name):
        print(f"Imagen descargada como {local_image_name}.")
        return local_image_name
    else:
        print(f"Error: No se pudo descargar {image_name}.")
        return None

def main():
    try:
        # Paso 1: Ejecutar el script en la Pico y obtener el nombre de la imagen
        image_name = run_pico_script()
        
        # Paso 2: Descargar la imagen
        local_image_name = download_image(image_name)
        
        # Paso 3: Mostrar la imagen
       

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

'''
#########

'''
import subprocess
import re
import cv2
import time
import os

# Configuración
PORT = "COM7"  # Puerto serial de la Pico
IMAGE_FOLDER = "c:/Users/Rodrigo-Lap/Desktop/Modelo Camara"  # Ruta de la carpeta donde se guardan las imágenes

def run_pico_script():
    """Ejecuta el script bootPI.py en la Raspberry Pi Pico y captura el nombre de la imagen."""
    print("Ejecutando bootPI.py en la Pico...")
    command = f"ampy --port {PORT} run bootPI.py"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    # Captura la salida del comando
    output = result.stdout
    print("Salida de la Pico:", output)
    
    # Busca el nombre de la imagen en la salida
    match = re.search(r"Imagen guardada como: (image_\d+\.jpg)", output)
    if match:
        image_name = match.group(1)
        print(f"Nombre de la imagen capturada: {image_name}")
        return image_name
    else:
        raise ValueError("No se pudo encontrar el nombre de la imagen en la salida.")
    
def download_image(image_name):
    """Descarga la imagen desde la Pico a la computadora."""
    local_image_name = os.path.join(IMAGE_FOLDER, image_name)  # Ruta completa de la imagen
    print(f"Descargando {image_name} desde la Pico...")
    
    # Asegúrate de que la ruta esté entre comillas para manejar espacios o caracteres especiales
    command = f'ampy --port {PORT} get "{image_name}" "{local_image_name}"'
    subprocess.run(command, shell=True)
    
    # Verifica si la imagen se descargó correctamente
    if os.path.exists(local_image_name):
        print(f"Imagen descargada como {local_image_name}.")
        return local_image_name
    else:
        print(f"Error: No se pudo descargar {image_name}.")
        return None

def show_image(image_path):
    """Muestra la imagen utilizando OpenCV."""
    if os.path.exists(image_path):
        print(f"Mostrando la imagen {image_path}...")
        image = cv2.imread(image_path)
        if image is not None:
            cv2.imshow("Captura de la Pico", image)
            cv2.waitKey(0)  # Espera hasta que se presione una tecla
            cv2.destroyAllWindows()
        else:
            print(f"Error: No se pudo cargar la imagen {image_path}.")
    else:
        print(f"Error: La imagen {image_path} no existe.")

def main():
    try:
        # Paso 1: Ejecutar el script en la Pico y obtener el nombre de la imagen
        image_name = run_pico_script()
        
        # Paso 2: Descargar la imagen
        local_image_name = download_image(image_name)
        
        # Paso 3: Mostrar la imagen
        if local_image_name:
            show_image(local_image_name)
       
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

'''
###FUNCIONA

import subprocess
import re
import cv2
import time
import os
import threading
import base64  # Para descomprimir la imagen
import numpy as np

# Configuración
PORT = "COM7"  # Puerto serial de la Pico
BAUDRATE = 921600   # Aumentar el baudrate
IMAGE_FOLDER = "c:/Users/Rodrigo-Lap/Desktop/Modelo Camara"  # Ruta de la carpeta donde se guardan las imágenes
DELAY_BETWEEN_CAPTURES = 0.01 # Retraso en segundos entre cada captura

def run_pico_script():
    """Ejecuta el script bootPI.py en la Raspberry Pi Pico y captura el nombre de la imagen."""
    start_time = time.time()
    print("Ejecutando bootPI.py en la Pico...")
    command = f"ampy --port {PORT} --baud {BAUDRATE} run bootPI.py"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    execution_time = time.time() - start_time
    print(f"Tiempo de ejecución en la Pico: {execution_time:.2f} segundos")
    #print("Ejecutado")
    # Captura la salida del comando
    output = result.stdout
    #print(f"Salida de la Pico:\n", output)
    
    # Busca el nombre de la imagen en la salida
    match = re.search(r"Imagen guardada como: (image_\d+\.jpg)", output)
    #match = re.search(r"Imagen comprimida guardada como: (image_\d+\.b64)", output)
    if match:
        #image_name = match.group(1)
        #print(f"Nombre de la imagen capturada: {image_name}")
        #return image_name
        return match.group(1)
    #else:
    #    raise ValueError("No se pudo encontrar el nombre de la imagen en la salida.")
    raise ValueError("No se pudo encontrar el nombre de la imagen en la salida.")
    
def download_image(image_name):
    """Descarga la imagen desde la Pico a la computadora."""
    start_time = time.time()
    local_image_name = os.path.join(IMAGE_FOLDER, image_name)
    command = f'ampy --port {PORT} --baud {BAUDRATE} get "{image_name}" "{local_image_name}"'
    subprocess.run(command, shell=True)
    download_time = time.time() - start_time
    print(f"Tiempo de descarga: {download_time:.2f} segundos")
    
    # Verifica si la imagen se descargó correctamente
    #if os.path.exists(local_image_name):
    ##    print(f"Imagen descargada como {local_image_name}.")
    #    return local_image_name
    #else:
    #    print(f"Error: No se pudo descargar {image_name}.")
    #    return None
    
    return local_image_name
'''
def decompress_image(image_path):
    """Descomprime la imagen en formato base64."""
    try:
        with open(image_path, 'rb') as f:
            compressed_data = f.read()
        
        # Verificar si los datos están vacíos
        if not compressed_data:
            print("Error: El archivo de imagen está vacío.")
            return None
        
        # Descomprimir la imagen desde base64
        image_data = base64.b64decode(compressed_data)
        
        # Verificar si la descompresión fue exitosa
        if not image_data:
            print("Error: No se pudo descomprimir la imagen.")
            return None
        
        return image_data
    except Exception as e:
        print(f"Error al descomprimir la imagen: {e}")
        return None
'''
def show_image(image_path):
    """Muestra la imagen utilizando OpenCV."""
    start_time = time.time()
    if os.path.exists(image_path):
        #print(f"Mostrando la imagen {image_path}\n\n")
        #image_data = decompress_image(image_path)
        #if image_data is None:
        #    print("Error: No se pudo descomprimir la imagen.")
        #    return True  # Continuar el bucle incluso si hay errores
        image = cv2.imread(image_path)
        #image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
        
        #image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
        if image is not None:
            
            cv2.imshow("Captura de la Pico", image)
            # Espera 1 ms y verifica si se presionó la tecla 'q' para salir
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return False  # Indica que se debe detener el bucle
        else:
            print("Error: No se pudo decodificar la imagen.")
        
        display_time = time.time() - start_time
        print(f"Tiempo de visualización: {display_time:.2f} segundos")
        #return True  # Indica que se debe continuar el bucle
        #else:
        #    print(f"Error: No se pudo cargar la imagen {image_path}.")
    #else:
    #    print(f"Error: La imagen {image_path} no existe.")
    #return True  # Continuar el bucle incluso si hay errores

    else:
        print(f"Error: La imagen {image_path} no existe.")
    return True

def capture_and_download():
    """Función para capturar y descargar imágenes en un bucle."""
    while True:
        try:
            start_time = time.time()  # Inicio del proceso total

            # Ejecutar el script en la Pico
            image_name = run_pico_script()

            # Descargar la imagen
            local_image_name = download_image(image_name)

            if local_image_name:
                if not show_image(local_image_name):  # Si show_image devuelve False, salir del bucle
                    break
            
            # Tiempo total del proceso
            total_time = time.time() - start_time
            print(f"Tiempo total del proceso: {total_time:.2f} segundos")

            time.sleep(DELAY_BETWEEN_CAPTURES)
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    # Iniciar el proceso de captura y descarga en un hilo separado
    threading.Thread(target=capture_and_download).start()



'''
def main():
    try:
        while True:  # Bucle infinito para captura continua
            # Paso 1: Ejecutar el script en la Pico y obtener el nombre de la imagen
            image_name = run_pico_script()
            
            # Paso 2: Descargar la imagen
            local_image_name = download_image(image_name)
            
            # Paso 3: Mostrar la imagen
            if local_image_name:
                if not show_image(local_image_name):  # Si show_image devuelve False, salir del bucle
                    break
            
            # Espera un momento antes de la siguiente captura
            time.sleep(DELAY_BETWEEN_CAPTURES)
       
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
'''



##############
################            Usando otro metodo #################
'''
import serial
import time
import cv2
import numpy as np
import os

# Configuración
PORT = "COM7"  # Puerto serial de la Pico (ajusta según tu sistema)
BAUDRATE = 921600  # Aumentar el baudrate para una transferencia más rápida
IMAGE_FOLDER = "c:/Users/Rodrigo-Lap/Desktop/Modelo Camara"  # Ruta de la carpeta donde se guardan las imágenes

# Inicializar la conexión serial
ser = serial.Serial(PORT, baudrate=BAUDRATE, timeout=1)

def receive_image():
    """Recibe la imagen a través de USB (serial integrado)."""
    # Leer el tamaño de la imagen
    size_data = ser.readline().decode().strip()
    if not size_data:
        print("Error: No se recibió el tamaño de la imagen.")
        return None

    try:
        image_size = int(size_data)
    except ValueError:
        print(f"Error: Tamaño de imagen no válido: {size_data}")
        return None

    # Leer la imagen en fragmentos
    image_data = b''
    while len(image_data) < image_size:
        chunk = ser.read(min(512, image_size - len(image_data)))  # Lee fragmentos de 512 bytes
        if not chunk:
            break  # Si no hay más datos, salir del bucle
        image_data += chunk

    print(f"Imagen recibida ({len(image_data)} bytes).")
    return image_data

def show_image(image_data):
    """Muestra la imagen utilizando OpenCV."""
    if image_data is None:
        return

    # Convertir los datos de la imagen en un array de numpy
    image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)

    if image is not None:
        cv2.imshow("Captura de la Pico", image)
        cv2.waitKey(1)  # Espera 1 ms para actualizar la ventana
    else:
        print("Error: No se pudo decodificar la imagen.")

def main():
    """Función principal para recibir y mostrar imágenes."""
    try:
        while True:
            # Recibir la imagen
            image_data = receive_image()

            # Mostrar la imagen
            show_image(image_data)

            # Esperar un momento antes de la siguiente captura
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Programa terminado.")
    finally:
        ser.close()  # Cerrar la conexión serial

if __name__ == "__main__":
    main()'
    '''