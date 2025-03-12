import spidev
import os
import time
import threading
from cameraPI import Camera, FileManager
import RPi.GPIO as GPIO

#################### CONFIGURACIÓN DEL SPI ####################
spi = spidev.SpiDev()
spi.open(0, 0)  # Bus 0, dispositivo CE0
spi.max_speed_hz = 23000000  # Velocidad del SPI

# Configurar el pin CS
CS_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(CS_PIN, GPIO.OUT)
GPIO.output(CS_PIN, GPIO.HIGH)

# Configuración de archivos
fm = FileManager()

# Inicializar la cámara
cam = Camera(spi, CS_PIN, debug_information=False)
cam.resolution = '320x240'
cam.set_filter(cam.SPECIAL_NORMAL)
cam.set_brightness_level(cam.BRIGHTNESS_DEFAULT)

# Función para eliminar imágenes antiguas
def delete_oldest_image():
    files = os.listdir()
    image_files = [file for file in files if file.startswith('image_') and file.endswith('.jpg')]
    if len(image_files) > 5:
        image_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
        oldest_image = image_files[0]
        print(f"Eliminando la imagen más antigua: {oldest_image}")
        os.remove(oldest_image)

delete_oldest_image()

# Función para capturar y guardar imágenes
def capture_and_save_image():
    print("Capturando imagen...")
    start_time = time.time()
    cam.capture_jpg()
    capture_time = time.time() - start_time
    print(f"Tiempo de captura: {capture_time:.3f} segundos")

    save_start_time = time.time()
    image_name = fm.new_jpg_fn('image')
    cam.save_JPG_burst(image_name)
    save_time = time.time() - save_start_time
    print(f"Tiempo de guardado: {save_time:.3f} segundos")
    print(f"Imagen guardada como: {image_name}")
    return image_name

# Ejecutar la captura
image_name = capture_and_save_image()

# Liberar recursos
spi.close()
GPIO.cleanup()
