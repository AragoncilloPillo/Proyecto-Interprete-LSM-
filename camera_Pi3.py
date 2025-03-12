import spidev
import time
import os
import json
import RPi.GPIO as GPIO

class FileManager:
    def __init__(self, file_manager_name='filemanager.log'):
        self.FILE_MANAGER_LOG_NAME = file_manager_name
        self.file_dict = {}

        if not os.path.exists(self.FILE_MANAGER_LOG_NAME):
            with open(self.FILE_MANAGER_LOG_NAME, 'w') as f:
                json.dump(self.file_dict, f)

        with open(self.FILE_MANAGER_LOG_NAME, 'r') as f:
            self.file_dict = json.load(f)

    def new_jpg_fn(self, requested_filename):
        count = self.file_dict.get(requested_filename, 0) + 1
        self.file_dict[requested_filename] = count
        self.save_manager_file()
        return f"{requested_filename}_{count}.jpg"

    def save_manager_file(self):
        with open(self.FILE_MANAGER_LOG_NAME, 'w') as f:
            json.dump(self.file_dict, f)

class Camera:
    def __init__(self, spi, cs_pin, debug_information=False):
        self.spi = spi
        self.cs_pin = cs_pin
        self.DEBUG_MODE = debug_information
        self.resolution = '320x240'
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.cs_pin, GPIO.OUT)
        GPIO.output(self.cs_pin, GPIO.HIGH)

    def _write_register(self, reg, value):
        GPIO.output(self.cs_pin, GPIO.LOW)
        self.spi.xfer2([reg | 0x80, value])
        GPIO.output(self.cs_pin, GPIO.HIGH)

    def _read_register(self, reg):
        GPIO.output(self.cs_pin, GPIO.LOW)
        self.spi.xfer2([reg])
        value = self.spi.xfer2([0x00])[0]
        GPIO.output(self.cs_pin, GPIO.HIGH)
        return value

    def capture_jpg(self):
        if self.DEBUG_MODE:
            print("Iniciando captura de imagen...")
        self._write_register(0x04, 0x01)  # Comando para iniciar captura
        time.sleep(0.1)  # Esperar captura

        while not (self._read_register(0x41) & 0x08):
            time.sleep(0.01)  # Esperar hasta que la imagen esté lista
        if self.DEBUG_MODE:
            print("Imagen capturada correctamente.")

    def save_JPG_burst(self, filename):
        if self.DEBUG_MODE:
            print(f"Guardando imagen en {filename}")
        GPIO.output(self.cs_pin, GPIO.LOW)
        self.spi.xfer2([0x3C])  # Comando para lectura burst

        with open(filename, 'wb') as f:
            while True:
                buffer = self.spi.readbytes(512)
                f.write(buffer)
                if buffer[-2:] == b'\xff\xd9':  # Fin de imagen JPEG
                    break
        GPIO.output(self.cs_pin, GPIO.HIGH)
        if self.DEBUG_MODE:
            print("Imagen guardada correctamente.")
