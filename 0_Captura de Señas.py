import os
import cv2
import numpy as np
import subprocess
import re
import time
from mediapipe.python.solutions.holistic import Holistic
from helpers import create_folder, draw_keypoints, mediapipe_detection, save_frames, there_hand
from constants import FONT, FONT_POS, FONT_SIZE, FRAME_ACTIONS_PATH, ROOT_PATH

# Configuración
PORT = "COM7"  # Puerto serial de la Pico
IMAGE_FOLDER = "c:/Users/Rodrigo-Lap/Desktop/Modelo Camara"  # Ruta de la carpeta donde se guardan las imágenes
DELAY_BETWEEN_CAPTURES = 0.1  # Retraso en segundos entre cada captura

# Función para obtener el siguiente número de intento
def get_next_attempt_number(path):
    attempt_number = 1
    while os.path.exists(os.path.join(path, f"Intento_{attempt_number}")):
        attempt_number += 1
    return attempt_number

# Función para ejecutar el script en la Pico y obtener el nombre de la imagen
def run_pico_script():
    """Ejecuta el script bootPI.py en la Raspberry Pi Pico y captura el nombre de la imagen."""
    print("Ejecutando bootPI.py en la Pico...")
    command = f"ampy --port {PORT} run bootPI.py"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print("Ejecutado")

    # Captura la salida del comando
    output = result.stdout
    print(f"Salida de la Pico:\n", output)
    
    # Busca el nombre de la imagen en la salida
    match = re.search(r"Imagen guardada como: (image_\d+\.jpg)", output)
    if match:
        image_name = match.group(1)
        print(f"Nombre de la imagen capturada: {image_name}")
        return image_name
    else:
        raise ValueError("No se pudo encontrar el nombre de la imagen en la salida.")

# Función para descargar la imagen desde la Pico
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

# Función principal para capturar señas
def captura_señas(path, margin_frame=1, min_cant_frames=15, delay_frames=3):
    """
    Captura los fotogramas del video desde la Raspberry Pi Pico y los procesa con MediaPipe.
    
    Parámetros:
    - path: Ruta de la carpeta de la palabra.
    - margin_frame: Cantidad de frames que se ignoran al comienzo y al final.
    - min_cant_frames: Cantidad mínima de frames para cada muestra.
    - delay_frames: Cantidad de frames que espera antes de detener la captura después de no detectar manos.
    """
    create_folder(path)
    
    count_frame = 0
    frames = []
    fix_frames = 0
    recording = False
    
    # Inicializa el modelo de MediaPipe para detectar cuerpo, manos y rostro.
    with Holistic() as holistic_model:
        while True:  # Bucle infinito para captura continua
            try:
                # Paso 1: Ejecutar el script en la Pico y obtener el nombre de la imagen
                image_name = run_pico_script()
                
                # Paso 2: Descargar la imagen
                local_image_name = download_image(image_name)
                
                if local_image_name:
                    # Cargar la imagen descargada
                    frame = cv2.imread(local_image_name)
                    if frame is None:
                        print(f"Error: No se pudo cargar la imagen {local_image_name}.")
                        continue
                    
                    # Procesamiento de la imagen con MediaPipe
                    image = frame.copy()
                    results = mediapipe_detection(frame, holistic_model)
                    
                    # Inicio de la captura y almacenamiento
                    if there_hand(results) or recording:
                        recording = False
                        count_frame += 1
                        if count_frame > margin_frame:
                            cv2.putText(image, 'Capturando...', FONT_POS, FONT, FONT_SIZE, (255, 80, 0))
                            frames.append(np.asarray(frame))
                    
                    # Finalización de la captura y almacenamiento                        
                    else:
                        if len(frames) >= min_cant_frames + margin_frame:
                            fix_frames += 1
                            if fix_frames < delay_frames:
                                recording = True
                                continue
                            frames = frames[: - (margin_frame + delay_frames)]
                            
                            # Obtener el siguiente número de intento
                            next_attempt = get_next_attempt_number(path)
                            output_folder = os.path.join(path, f"Intento_{next_attempt}")
                            
                            create_folder(output_folder)
                            save_frames(frames, output_folder)
                        
                        recording, fix_frames = False, 0
                        frames, count_frame = [], 0
                        cv2.putText(image, 'Listo para capturar...', FONT_POS, FONT, FONT_SIZE, (0, 220, 100))
                    
                    # Mostrar la captura en pantalla
                    draw_keypoints(image, results)
                    cv2.imshow(f'Toma de muestras para "{os.path.basename(path)}"', image)
                    if cv2.waitKey(10) & 0xFF == ord('z'):
                        break
                
            except Exception as e:
                print(f"Error: {e}")
                break
            
            # Espera un momento antes de la siguiente captura
            time.sleep(DELAY_BETWEEN_CAPTURES)
        
        # Liberación de recursos
        cv2.destroyAllWindows()

if __name__ == "__main__":
    word_name = "comezon"  # INSERTAR PALABRA
    word_path = os.path.join(ROOT_PATH, FRAME_ACTIONS_PATH, word_name)
    captura_señas(word_path)

print("------->Proceso terminado")






################################################################
#                                ORIGINAL
################################################################
'''
import os
import cv2
import numpy as np
from mediapipe.python.solutions.holistic import Holistic
from helpers import create_folder, draw_keypoints, mediapipe_detection, save_frames, there_hand
from constants import FONT, FONT_POS, FONT_SIZE, FRAME_ACTIONS_PATH, ROOT_PATH
from datetime import datetime

# Función para obtener el siguiente número de intento
def get_next_attempt_number(path):
    attempt_number = 1
    while os.path.exists(os.path.join(path, f"Intento_{attempt_number}")):
        attempt_number += 1
    return attempt_number

#Captura los fotogramas del video
def captura_señas(path, margin_frame=1, min_cant_frames=15, delay_frames=3):
    
    ### CAPTURA DE MUESTRAS PARA UNA PALABRA
    #Recibe como parámetro la ubicación de guardado y guarda los frames
    
    #`path` ruta de la carpeta de la palabra \n
    #`margin_frame` cantidad de frames que se ignoran al comienzo y al final \n
    #`min_cant_frames` cantidad de frames minimos para cada muestra \n
    #`delay_frames` cantidad de frames que espera antes de detener la captura después de no detectar manos
    
    create_folder(path)
    
    count_frame = 0
    frames = []
    fix_frames = 0
    recording = False
    
    # Inicializa el modelo de MediaPipe para detectar cuerpo, manos y rostro.
    with Holistic() as holistic_model:
        video = cv2.VideoCapture(0)
        video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        video.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        while video.isOpened():
            ret, frame = video.read()
            if not ret:
                break
            
            #Empieza procesamiento de imagen
            image = frame.copy()
            #Se usa MediaPipe para detectar puntos clave en el fotograma.
            results = mediapipe_detection(frame, holistic_model)
            
            #Inicio de la captura y almacenamiento
            if there_hand(results) or recording:
                recording = False
                count_frame += 1
                if count_frame > margin_frame:
                    cv2.putText(image, 'Capturando...', FONT_POS, FONT, FONT_SIZE, (255, 80, 0))
                    frames.append(np.asarray(frame))
            
            #Finalización de la captura y almacenamiento                        
            else:
                if len(frames) >= min_cant_frames + margin_frame:
                    fix_frames += 1
                    if fix_frames < delay_frames:
                        recording = True
                        continue
                    frames = frames[: - (margin_frame + delay_frames)]
                    
                    # Obtener el siguiente número de intento
                    next_attempt = get_next_attempt_number(path)
                    output_folder = os.path.join(path, f"Intento_{next_attempt}")
                    
                    create_folder(output_folder)
                    save_frames(frames, output_folder)
                
                recording, fix_frames = False, 0
                frames, count_frame = [], 0
                cv2.putText(image, 'Listo para capturar...', FONT_POS, FONT, FONT_SIZE, (0,220, 100))
            
            #Mostrar la captura en pantalla
            draw_keypoints(image, results)
            cv2.imshow(f'Toma de muestras para "{os.path.basename(path)}"', image)
            if cv2.waitKey(10) & 0xFF == ord('z'):
                break
        
        #Liberación de recursos
        video.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    word_name = "comezon" #INSERTAR PALABRA
    word_path = os.path.join(ROOT_PATH, FRAME_ACTIONS_PATH, word_name)
    captura_señas(word_path)

print("------->Proceso terminado")
'''
