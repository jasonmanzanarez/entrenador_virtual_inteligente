import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import threading
import random
import time
import speech_recognition as sr

# === Inicializar voz ===
voz = pyttsx3.init()
voz.setProperty('rate', 150)
ultimo_mensaje = ""


def hablar(mensaje):
    global ultimo_mensaje
    if mensaje != ultimo_mensaje:
        ultimo_mensaje = mensaje
        threading.Thread(target=_decir, args=(mensaje,), daemon=True).start()


def _decir(mensaje):
    voz.say(mensaje)
    voz.runAndWait()


# === Escuchar comando de voz ===
def escuchar_comando():
    r = sr.Recognizer()
    with sr.Microphone(device_index=1) as source:
        print("🎙️ Micrófono activo... habla ahora")
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)
        try:
            texto = r.recognize_google(audio, language="es-MX").lower()
            print(f"🧠 Se escuchó: {texto}")
            return texto
        except:
            print("⚠️ No se entendió el audio")
            return ""


# === Rutinas disponibles ===
rutinas = {
    "corta": [("sentadilla", 3), ("lagartija", 3)],
    "media": [("sentadilla", 5), ("lagartija", 5)],
    "larga": [("sentadilla", 8), ("lagartija", 8)]
}

# === Frases motivadoras ===
frases_correctas = [
    "¡Buena repetición!", "¡Eso estuvo perfecto!", "¡Muy bien hecho!",
    "¡Excelente ejecución!", "¡Gran esfuerzo!", "¡Correcto, sigue así!"
]

# === Cálculo de ángulo ===
def calcular_angulo(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    coseno = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angulo = np.arccos(coseno)
    return np.degrees(angulo)


# === Lógica de entrenamiento ===
def iniciar_entrenamiento(rutina_actual):
    repeticiones = 0
    estado = "arriba"
    actual = 0
    ejercicio, meta = rutina_actual[actual]
    hablar(f"Vamos a comenzar con {meta} {ejercicio}s")

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
                hombro = [puntos[11].x, puntos[11].y]
                cadera = [puntos[23].x, puntos[23].y]
                rodilla = [puntos[25].x, puntos[25].y]
                tobillo = [puntos[27].x, puntos[27].y]
                codo = [puntos[14].x, puntos[14].y]
                muñeca = [puntos[16].x, puntos[16].y]

                if ejercicio == "sentadilla":
                    angulo = calcular_angulo(cadera, rodilla, tobillo)
                    if angulo < 80 and estado == "arriba":
                        estado = "abajo"
                    elif angulo > 100 and estado == "abajo":
                        estado = "arriba"
                        repeticiones += 1
                        hablar(random.choice(frases_correctas))

                elif ejercicio == "lagartija":
                    angulo = calcular_angulo(hombro, codo, muñeca)
                    if angulo < 70 and estado == "arriba":
                        estado = "abajo"
                    elif angulo > 150 and estado == "abajo":
                        estado = "arriba"
                        repeticiones += 1
                        hablar(random.choice(frases_correctas))

                if repeticiones >= meta:
                    hablar(f"¡Completaste {meta} {ejercicio}s!")
                    actual += 1
                    repeticiones = 0

                    if actual >= len(rutina_actual):
                        hablar("🏁 ¡Rutina completada! Excelente trabajo.")
                        break
                    else:
                        ejercicio, meta = rutina_actual[actual]
                        hablar(f"🟢 Siguiente ejercicio: {meta} {ejercicio}s")
                        time.sleep(2)

            # Mostrar en pantalla
            cv2.putText(imagen, f"Ejercicio: {ejercicio.upper()} ({repeticiones}/{meta})",
                        (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            if actual + 1 < len(rutina_actual):
                siguiente = rutina_actual[actual + 1]
                cv2.putText(imagen, f"Siguiente: {siguiente[0].capitalize()} x{siguiente[1]}",
                            (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            cv2.imshow("Entrenador Virtual AI", imagen)
            if cv2.waitKey(10) & 0xFF == 27:
                break

    cam.release()
    cv2.destroyAllWindows()


# === MAIN ===
if __name__ == "__main__":
    hablar("Di qué rutina quieres hacer: corta, media o larga")
    seleccion = ""
    while seleccion not in rutinas:
        seleccion = escuchar_comando()
        if seleccion not in rutinas:
            hablar("No entendí. Repite: corta, media o larga.")
    rutina = rutinas[seleccion]
    iniciar_entrenamiento(rutina)
