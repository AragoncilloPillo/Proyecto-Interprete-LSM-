# Arducam port to Pico

from machine import Pin, SPI#, reset
# Developing on 1.24
from camera_Pi3 import Camera, FileManager
from utime import sleep_ms, ticks_ms, ticks_diff
import uos
import _thread  # Para ejecutar operaciones en paralelo
import ubinascii  # Para comprimir la imagen
#import numpy as np


#################### PINOUT ####################
'''
Camera pin - Pico Pin
VCC - 3V3 - red
GND - GND - black
SPI - 0
SCK - GP18 - white
MISO - RX - GP16 - brown
MOSI - TX - GP19 - yellow
CS - GP17 - orange

Camera pin - ESP32 S3
VCC - 3V3 - red
GND - GND - black
SPI - 2
SCK - GP12 - white
MISO - RX - GP13 - brown
MOSI - TX - GP11 - yellow
CS - GP17 - orange
'''


################################################################## CODE ACTUAL ##################################################################
#Pi pico

spi = SPI(0,sck=Pin(18), miso=Pin(16), mosi=Pin(19), baudrate=23000000)#baudrate=25000000)
cs = Pin(17, Pin.OUT)

# button = Pin(15, Pin.AIN,Pin.PULL_UP)
onboard_LED = Pin(25, Pin.OUT)

#ESP 32 S3

#spi = SPI(2,sck=Pin(12), miso=Pin(13), mosi=Pin(11), baudrate=8000000)
#cs = Pin(17, Pin.OUT)

# button = Pin(15, Pin.IN,Pin.PULL_UP)
#onboard_LED = Pin(48, Pin.OUT)


#Adds _# to end of filename, is same file name is used more than once images are stacked in the same file and only the first image renders while the size grows
fm = FileManager()

cam = Camera(spi, cs, debug_information=False)
cam.resolution = '320x240'
#cam.resolution = '640x480'
# cam.set_filter(cam.SPECIAL_REVERSE)
#cam.set_brightness_level(cam.BRIGHTNESS_PLUS_4)
#cam.set_contrast(cam.CONTRAST_MINUS_3)
cam.set_filter(cam.SPECIAL_NORMAL)  # Desactiva efectos de color
cam.set_brightness_level(cam.BRIGHTNESS_DEFAULT)  # Desactiva ajustes de brillo

# Reducir el tiempo de espera del balance de blancos
#cam.WHITE_BALANCE_WAIT_TIME_MS = 100  # 100 ms

def delete_all_images():
    """Elimina todas las imágenes guardadas en la Pico."""
    files = uos.listdir()
    for file in files:
        if file.startswith('image_') and file.endswith('.b64'):
            print(f"Eliminando {file}...")
            uos.remove(file)


def delete_oldest_image():
    """Elimina la imagen más antigua si hay más de 10 imágenes."""
    files = uos.listdir()
    image_files = [file for file in files if file.startswith('image_') and file.endswith('.jpg')]
    
    # Si hay más de 20 imágenes, elimina la más antigua
    if len(image_files) > 5:
        # Ordena las imágenes por el número en el nombre
        image_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
        oldest_image = image_files[0]  # La primera es la más antigua
        print(f"Eliminando la imagen más antigua: {oldest_image}")
        uos.remove(oldest_image)

def delete_oldest_compres():
    """Elimina la imagen más antigua si hay más de 10 imágenes."""
    files = uos.listdir()
    com_files = [file for file in files if file.startswith('image_') and file.endswith('.b64')]
    
    # Si hay más de 20 imágenes, elimina la más antigua
    if len(com_files) > 5:
        # Ordena las imágenes por el número en el nombre
        com_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
        oldest_com = com_files[0]  # La primera es la más antigua
        print(f"Eliminando la imagen más antigua: {oldest_com}")
        uos.remove(oldest_com)


# Paso 1:  Eliminar la imagen más antigua si hay más de 20 imágenes
#delete_oldest_compres()

delete_oldest_image()

#delete_all_images()
'''
# Función para comprimir la imagen en base64
def compress_image(image_data):
    """Comprime la imagen en formato base64."""
    return ubinascii.b2a_base64(image_data)
'''
# Función para capturar, comprimir y guardar una imagen
def capture_and_save_image():
    """Captura, comprime y guarda una imagen."""
    onboard_LED.on()  # Enciende el LED para indicar que la cámara está trabajando
    # Capturar y guardar una nueva imagen
    #onboard_LED.on()  # Enciende el LED para indicar que la cámara está trabajando

    # Inicio del proceso de captura
    start_time = ticks_ms()

    cam.capture_jpg()  # Captura la imagen
    #sleep_ms(10)  # Pequeña pausa
    capture_time = ticks_diff(ticks_ms(), start_time)
    print(f"Tiempo de captura: {capture_time} ms")

    #cam.saveJPG(image_name)  # Guarda la imagen con el nombre generado
    save_start_time = ticks_ms()
    image_name = fm.new_jpg_fn('image')  # Genera un nombre único para la imagen
    cam.save_JPG_burst(image_name)# Guarda la imagen en modo burst
    save_time = ticks_diff(ticks_ms(), save_start_time)
    print(f"Tiempo de guardado: {save_time} ms")


##intento de compresion 
    '''
    # Comprimir la imagen
    with open(image_name, 'rb') as f:
        image_data = f.read()
    compressed_image = compress_image(image_data)

    # Guardar la imagen comprimida
    compressed_image_name = image_name.replace('.jpg', '.b64')
    with open(compressed_image_name, 'wb') as f:
        f.write(compressed_image)
    '''


########

 # Tiempo total en la Pico
    total_time = ticks_diff(ticks_ms(), start_time)
    print(f"Tiempo total en la Pico: {total_time} ms")

    onboard_LED.off()  # Apaga el LED
    print(f"Imagen guardada como: {image_name}")  # Imprime el nombre de la imagen
    #print(f"Imagen comprimida guardada como: {compressed_image_name}")  # Imprime el nombre de la imagen comprimida

    #return compressed_image_name  # Retorna el nombre de la imagen comprimida

# Ejecutar la captura y guardado en un hilo separado
image_name = capture_and_save_image()  # Ejecutar en el hilo principal
#print(f"Imagen comprimida guardada como: {image_name}")  # Asegurar que el nombre se imprima



#################################################################################################################################################
'''
Benchmarks
- Default SPI speed (1000000?), cam.resolution = '640X480', no burst read (camera pointed at roof) ==== TIME: ~7.8 seconds
- Increased speed (8000000), cam.resolution = '640X480', no burst read (camera pointed at roof) ==== TIME: ~7.3 seconds
'''
###########
#Segunda version 

'''
from machine import Pin, SPI
from cameraPI import Camera, FileManager
from utime import sleep_ms, ticks_ms, ticks_diff
import uos
import sys

# Configuración del SPI y CS
spi = SPI(0, sck=Pin(18), miso=Pin(16), mosi=Pin(19), baudrate=23000000)
cs = Pin(17, Pin.OUT)

# LED onboard para indicar actividad
onboard_LED = Pin(25, Pin.OUT)

# Inicializar el FileManager para manejar nombres de archivos
fm = FileManager()

# Inicializar la cámara
cam = Camera(spi, cs, debug_information=False)

# Verificar que la cámara se haya inicializado correctamente
if not hasattr(cam, 'camera_idx'):
    print("Error: La cámara no se inicializó correctamente.")
    sys.exit(1)  # Terminar el programa si la cámara no se inicializa

# Configurar la resolución de la cámara
cam.resolution = '320x240'  # Resolución fija
cam.set_filter(cam.SPECIAL_NORMAL)  # Desactiva efectos de color
cam.set_brightness_level(cam.BRIGHTNESS_DEFAULT)  # Desactiva ajustes de brillo

# Reducir el tiempo de espera del balance de blancos
cam.WHITE_BALANCE_WAIT_TIME_MS = 0  # Eliminar el tiempo de espera

# Aumentar el tamaño del búfer
cam.BUFFER_MAX_LENGTH = 256  # Prueba con un tamaño de búfer más grande

# Función para eliminar la imagen más antigua si hay más de 5 imágenes
def delete_oldest_image():
    """Elimina la imagen más antigua si hay más de 5 imágenes."""
    files = uos.listdir()
    image_files = [file for file in files if file.startswith('image_') and file.endswith('.jpg')]
    
    if len(image_files) > 5:
        # Ordena las imágenes por el número en el nombre
        image_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
        oldest_image = image_files[0]  # La primera es la más antigua
        print(f"Eliminando la imagen más antigua: {oldest_image}")
        uos.remove(oldest_image)

# Eliminar la imagen más antigua si es necesario
delete_oldest_image()

# Función para capturar y guardar una imagen
def capture_and_save_image():
    """Captura y guarda una imagen."""
    onboard_LED.on()  # Enciende el LED para indicar que la cámara está trabajando

    # Medir el tiempo de captura y guardado
    start_time = ticks_ms()

    # Capturar la imagen
    cam.capture_jpg()
    capture_time = ticks_diff(ticks_ms(), start_time)
    print(f"Tiempo de captura: {capture_time} ms")

    # Guardar la imagen
    save_start_time = ticks_ms()
    image_name = fm.new_jpg_fn('image')  # Genera un nombre único para la imagen
    cam.save_JPG_burst(image_name)  # Guarda la imagen en modo burst
    save_time = ticks_diff(ticks_ms(), save_start_time)
    print(f"Tiempo de guardado: {save_time} ms")

    # Tiempo total en la Pico
    total_time = ticks_diff(ticks_ms(), start_time)
    print(f"Tiempo total en la Pico: {total_time} ms")

    onboard_LED.off()  # Apaga el LED
    print(f"Imagen guardada como: {image_name}")  # Imprime el nombre de la imagen

    return image_name  # Retorna el nombre de la imagen

# Función para enviar la imagen por USB (serial integrado)
def send_image_over_usb(image_name):
    """Envía la imagen a través de USB (serial integrado)."""
    with open(image_name, 'rb') as f:
        image_data = f.read()

    # Enviar el tamaño de la imagen primero
    image_size = len(image_data)
    print(f"Tamaño de la imagen: {image_size} bytes")
    sys.stdout.write(str(image_size) + '\n')  # Envía el tamaño como una cadena seguida de un salto de línea

    # Enviar la imagen en fragmentos
    chunk_size = 64  # Tamaño del fragmento (ajusta según sea necesario)
    for i in range(0, len(image_data), chunk_size):
        chunk = image_data[i:i + chunk_size]
        sys.stdout.write(chunk)  # Envía el fragmento a través del USB
        sleep_ms(10)  # Pequeña pausa para evitar saturar el búfer

    print(f"Imagen {image_name} enviada por USB.")

# Ejecutar la captura y guardado
image_name = capture_and_save_image()  # Captura y guarda la imagen

# Enviar la imagen por USB
send_image_over_usb(image_name)'
''
'''
