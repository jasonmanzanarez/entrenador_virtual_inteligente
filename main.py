import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import threading
import random
import time
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import tempfile
import os
import csv
from datetime import datetime
from pyswip import Prolog
from PIL import Image

# === Inicializar Prolog ===
prolog = Prolog()
prolog.consult("entrenador_conocimiento.pl")

def angulo_valido(ejercicio, angulo):
    try:
        resultado = list(prolog.query(f"angulo_valido_para_{ejercicio}({int(angulo)})"))
        return len(resultado) > 0
    except Exception as e:
        print(f"❌ Error al consultar Prolog: {e}")
        return False

# === Inicializar voz ===
voz = pyttsx3.init()
voz.setProperty('rate', 150)
ultimo_mensaje = ""
voz_lock = threading.Lock()

def hablar(mensaje):
    global ultimo_mensaje
    if mensaje != ultimo_mensaje:
        ultimo_mensaje = mensaje
        threading.Thread(target=_decir_bloqueado, args=(mensaje,), daemon=True).start()

def _decir_bloqueado(mensaje):
    with voz_lock:
        voz.say(mensaje)
        voz.runAndWait()

# === Escuchar comando en hilo ===
comando_detectado = ""

def hilo_escucha():
    global comando_detectado
    while True:
        fs = 44100
        seconds = 4
        audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            sf.write(f.name, audio, fs)
            audio_path = f.name
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
        os.unlink(audio_path)
        try:
            texto = recognizer.recognize_google(audio_data, language="es-MX").lower()
            if "terminar" in texto or "salir" in texto:
                comando_detectado = texto
        except:
            continue

# === Frases motivadoras ===
frases_correctas = [
    "¡Buena repetición!", "¡Eso estuvo perfecto!", "¡Muy bien hecho!",
    "¡Excelente ejecución!", "¡Gran esfuerzo!", "¡Correcto, sigue así!"
]

# === Guardar registro CSV ===
def guardar_registro(usuario, repeticiones_totales, duracion_segundos):
    nombre_archivo = "registro.csv"
    encabezado = ["Usuario", "Fecha", "Repeticiones", "Duración (s)"]
    fila = [usuario, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), repeticiones_totales, round(duracion_segundos, 2)]
    archivo_existe = os.path.isfile(nombre_archivo)
    with open(nombre_archivo, "a", newline="") as archivo:
        escritor = csv.writer(archivo)
        if not archivo_existe:
            escritor.writerow(encabezado)
        escritor.writerow(fila)

# === Mostrar GIF en ventana separada ===
def cargar_gif_frame(ruta):
    gif = Image.open(ruta)
    gif = gif.convert('RGB').resize((300, 300))
    return np.array(gif)[:, :, ::-1]  # Convert RGB to BGR

def mostrar_gif_en_ventana(ruta):
    gif_img = cargar_gif_frame(ruta)
    nombre_ventana = "Correccion Visual"
    cv2.namedWindow(nombre_ventana, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(nombre_ventana, 300, 300)
    cv2.imshow(nombre_ventana, gif_img)
    cv2.waitKey(4000)
    cv2.destroyWindow(nombre_ventana)

# === Cálculo de ángulo ===
def calcular_angulo(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    coseno = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angulo = np.arccos(coseno)
    return np.degrees(angulo)

# === Obtener nombre por voz ===
def obtener_nombre_por_voz():
    hablar("Por favor, dime tu nombre")
    while True:
        fs = 44100
        seconds = 4
        audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            sf.write(f.name, audio, fs)
            audio_path = f.name
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
        os.unlink(audio_path)
        try:
            nombre = recognizer.recognize_google(audio_data, language="es-MX").title()
            hablar(f"Hola {nombre}, comenzamos cuando estés listo.")
            return nombre
        except:
            hablar("No entendí tu nombre. Por favor, repítelo.")
            continue

# === Entrenamiento de sentadillas ===
def iniciar_sentadillas(usuario):
    global comando_detectado
    repeticiones = 0
    estado = "arriba"
    tiempo_inicio = time.time()

    hablar("Vamos a comenzar con tus sentadillas. Di 'terminar' si deseas salir.")
    threading.Thread(target=hilo_escucha, daemon=True).start()

    cam = cv2.VideoCapture(0)
    with mp.solutions.pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cam.isOpened():
            ret, frame = cam.read()
            if not ret:
                break

            imagen = cv2.flip(frame, 1)
            imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
            resultados = pose.process(imagen_rgb)

            if resultados.pose_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    imagen,
                    resultados.pose_landmarks,
                    mp.solutions.pose.POSE_CONNECTIONS,
                    mp.solutions.drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                    mp.solutions.drawing_utils.DrawingSpec(color=(255, 0, 0), thickness=2)
                )

                puntos = resultados.pose_landmarks.landmark
                cadera = [puntos[23].x, puntos[23].y]
                rodilla = [puntos[25].x, puntos[25].y]
                tobillo = [puntos[27].x, puntos[27].y]

                angulo = calcular_angulo(cadera, rodilla, tobillo)
                if not angulo_valido("sentadilla", angulo) and estado == "arriba":
                    estado = "abajo"
                    resultado_visual = list(prolog.query(f"retroalimentar_visual(sentadilla, {int(angulo)}, Mensaje, Recurso)"))
                    if resultado_visual:
                        mensaje_visual = resultado_visual[0]["Mensaje"]
                        recurso = resultado_visual[0]["Recurso"]
                        hablar(mensaje_visual)
                        threading.Thread(target=mostrar_gif_en_ventana, args=(recurso,), daemon=True).start()

                elif angulo_valido("sentadilla", angulo) and estado == "abajo":
                    estado = "arriba"
                    repeticiones += 1
                    hablar(random.choice(frases_correctas))

                cv2.putText(imagen, f"Sentadillas: {repeticiones}",
                            (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            cv2.imshow("Entrenador Virtual - Sentadillas", imagen)

            if comando_detectado:
                hablar("Finalizando la rutina. Buen trabajo.")
                break

            if cv2.waitKey(10) & 0xFF == 27:
                break

    cam.release()
    cv2.destroyAllWindows()
    duracion_total = time.time() - tiempo_inicio
    guardar_registro(usuario, repeticiones, duracion_total)

# === MAIN ===
if __name__ == "__main__":
    usuario = obtener_nombre_por_voz()
    hablar("Cuando estés listo, presiona una tecla para comenzar")
    input("Presiona ENTER para iniciar...")
    iniciar_sentadillas(usuario)
