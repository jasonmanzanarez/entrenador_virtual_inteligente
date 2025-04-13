# Entrenador Virtual Inteligente

## 🚀 **Descripción del Proyecto**

Este proyecto tiene como objetivo crear un **Entrenador Virtual Inteligente** que utiliza **visión artificial** y **reconocimiento de voz** para asistir a los usuarios en sus entrenamientos en casa. 

Utiliza **MediaPipe** para la detección en tiempo real de poses y calcula los ángulos de las articulaciones para contar repeticiones de ejercicios como **sentadillas** y **lagartijas**. Además, da retroalimentación por **voz** con **pyttsx3** y permite elegir la rutina de entrenamiento mediante **comandos de voz**.

---

## ⚙️ **Tecnologías Utilizadas**

- **Python 3.x**
- **MediaPipe**: para detección de poses y cálculo de ángulos.
- **OpenCV**: para acceder a la cámara y mostrar los resultados.
- **pyttsx3**: para retroalimentación por voz.
- **SpeechRecognition**: para reconocimiento de voz.
- **NumPy**: para cálculos matemáticos.
- **threading**: para ejecutar la voz en segundo plano sin congelar el video.

---

## 🚀 **Requisitos**

Asegúrate de tener Python 3.7 o superior. Para instalar las dependencias necesarias, ejecuta:

```bash
pip install -r requirements.txt
Las dependencias son:

opencv-python

mediapipe

numpy

pyttsx3

SpeechRecognition

pyaudio

⚡ Instrucciones para Ejecutar el Proyecto
Clona este repositorio o descarga el código.

Instala las dependencias mencionadas anteriormente usando el archivo requirements.txt.

Ejecuta el archivo principal (main.py):

bash
Copy
python main.py
El programa te pedirá que elijas una rutina (corta, media o larga) por comando de voz. Luego, se activará la cámara y comenzará a contar repeticiones de los ejercicios seleccionados (sentadillas o lagartijas).

Feedback en voz: El sistema te dará retroalimentación cada vez que completes una repetición correctamente.

🛠 ¿Cómo funciona el entrenamiento?
Elección de rutina: Al ejecutar el código, el sistema escuchará un comando de voz para elegir una rutina: "corta", "media", o "larga".

Detección de ejercicios: Utilizando MediaPipe, el sistema detecta los puntos clave de tu cuerpo (rodillas, tobillos, hombros, etc.) para verificar si estás haciendo el ejercicio correctamente.

Cálculo de ángulos: Se calculan los ángulos entre diferentes articulaciones (como la rodilla y el tobillo para las sentadillas) para contar cuántas repeticiones completas has hecho.

Retroalimentación: Cuando completes una repetición correctamente, el sistema te dará retroalimentación verbal positiva como "¡Muy bien hecho!".

⚡ Próximos pasos
Añadir más ejercicios: Puedes agregar otros ejercicios como abdominales, flexiones y más, siguiendo la misma lógica de detección de ángulos.

Guardar estadísticas: Agregar la opción de guardar las estadísticas de entrenamiento (número de repeticiones, tiempo, etc.) para análisis posteriores.

Integración con Prolog: Puedes integrar un sistema basado en Prolog para evaluar la postura de manera más avanzada y personalizada.

📞 Contacto
Si tienes alguna pregunta o sugerencia, no dudes en contactarme:

Correo: jason.samuel.manzanarez.cota@gmail.com