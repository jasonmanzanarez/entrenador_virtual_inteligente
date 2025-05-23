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

# === Escuchar comando de voz (sin PyAudio) ===
def escuchar_comando():
    fs = 44100
    seconds = 4
    print("🎙️ Grabando... habla ahora")
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
        print(f"🧠 Se escuchó: {texto}")
        return texto
    except sr.UnknownValueError:
        print("⚠️ No se entendió el audio")
        return ""
    except sr.RequestError:
        print("🚫 Error con el servicio de reconocimiento")
        return ""

def obtener_nombre_usuario():
    hablar("Por favor, di tu nombre")
    nombre = escuchar_comando()
    if not nombre:
        nombre = input("No se entendió el nombre. Escríbelo manualmente: ")
    print(f"📌 Usuario identificado: {nombre}")
    return nombre

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

# === Cálculo de ángulo ===
def calcular_angulo(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    coseno = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angulo = np.arccos(coseno)
    return np.degrees(angulo)

# === Lógica de entrenamiento solo para sentadillas ===
def iniciar_sentadillas(usuario):
    repeticiones = 0
    estado = "arriba"
    tiempo_inicio = time.time()
    hablar("Vamos a comenzar con tus sentadillas")

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
                # Dibuja puntos y conexiones del cuerpo
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
                elif angulo_valido("sentadilla", angulo) and estado == "abajo":
                    estado = "arriba"
                    repeticiones += 1
                    hablar(random.choice(frases_correctas))

                cv2.putText(imagen, f"Sentadillas: {repeticiones}",
                            (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            cv2.imshow("Entrenador Virtual - Sentadillas", imagen)
            if cv2.waitKey(10) & 0xFF == 27:
                break

    cam.release()
    cv2.destroyAllWindows()
    duracion_total = time.time() - tiempo_inicio
    guardar_registro(usuario, repeticiones, duracion_total)

# === MAIN ===
if __name__ == "__main__":
    usuario = obtener_nombre_usuario()
    hablar("Cuando estés listo, presiona una tecla para comenzar")
    input("Presiona ENTER para iniciar...")
    iniciar_sentadillas(usuario)
