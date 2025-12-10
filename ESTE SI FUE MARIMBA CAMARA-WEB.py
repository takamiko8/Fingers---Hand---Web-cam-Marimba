import os
import cv2
import mediapipe as mp
import mido  # Asegúrate de importar mido
from mido import MidiFile, MidiTrack, Message
import random  # Para variabilidad en las duraciones y velocidades

# Configuración de MediaPipe para la detección de manos
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Configuración de OpenCV para capturar video
cap = cv2.VideoCapture(0)

# Crear un archivo MIDI vacío
midi_file = MidiFile()
track = MidiTrack()
midi_file.tracks.append(track)

# Configuración de la pista MIDI
track.append(mido.Message('program_change', program=12))  # Instrumento
track.append(mido.Message('control_change', control=7, value=100))  # Volumen

# Función para mapear la posición de los dedos a una nota MIDI con variabilidad
def finger_to_midi(finger_tip_y, base_note=60, offset=0):
    """Mapea la posición de los dedos a notas MIDI con variabilidad."""
    note = int(base_note + (finger_tip_y - 0.2) * 12 + random.randint(-3, 3))  # Aleatoriedad en la altura de la nota
    note = max(0, min(127, note))  # Limitar a rango MIDI válido
    return note + offset  # Agregar un offset para tener notas más diversas

# Función para agregar una nota MIDI con duraciones y velocidades aleatorias
def add_midi_note(note, time_offset=0):
    """Agrega una nota MIDI con duraciones aleatorias y variabilidad en la velocidad."""
    duration = random.choice([240, 480, 720, 960])  # Duraciones aleatorias de notas
    velocity = random.randint(50, 100)  # Velocidad aleatoria de la nota
    track.append(Message('note_on', note=note, velocity=velocity, time=time_offset))
    track.append(Message('note_off', note=note, velocity=velocity, time=duration))  # Duración variable
    print(f"Nota MIDI agregada: {note} con duración {duration} y velocidad {velocity}")  # Depuración

# Tiempo relativo para las notas
time_offset = 0

# Ruta de la carpeta "fdwer578"
script_dir = os.getcwd()  # Directorio actual donde se ejecuta el script
fdwer578_dir = os.path.join(script_dir, "fdwer578")  # Ruta completa a la carpeta "fdwer578"

# Verificar si la carpeta "fdwer578" existe, si no, crearla
print(f"Verificando si la carpeta {fdwer578_dir} existe...")
if not os.path.exists(fdwer578_dir):
    print(f"La carpeta {fdwer578_dir} no existe, creando la carpeta...")
    os.makedirs(fdwer578_dir)  # Crea la carpeta si no existe
else:
    print(f"La carpeta {fdwer578_dir} ya existe.")

# Crear la ruta completa para el archivo MIDI dentro de "fdwer578"
midi_file_path = os.path.join(fdwer578_dir, "output_melody.mid")

# Verificar la ruta completa del archivo antes de guardarlo
print(f"Ruta completa donde se guardará el archivo MIDI: {midi_file_path}")

# Inicializar un contador para las notas MIDI
midi_note_count = 0
max_notes = 150  # Límite de notas MIDI a grabar

# Bucle para capturar el video
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error al capturar la imagen del video")
        break

    # Convertir a RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            # Obtener las posiciones de los dedos índice (8) y medio (12)
            finger_index_y = landmarks.landmark[8].y
            finger_middle_y = landmarks.landmark[12].y

            # Generar notas para el dedo índice y medio con diferentes variaciones
            midi_note_index = finger_to_midi(finger_index_y, base_note=60, offset=0)
            midi_note_middle = finger_to_midi(finger_middle_y, base_note=60, offset=12)  # Cambio en el offset

            # Agregar notas MIDI para los dos dedos
            add_midi_note(midi_note_index, time_offset)
            midi_note_count += 1  # Incrementar el contador
            time_offset += 240  # Tiempo para la siguiente nota

            add_midi_note(midi_note_middle, time_offset)
            midi_note_count += 1  # Incrementar el contador
            time_offset += 240  # Tiempo para la siguiente nota

            # Si hemos alcanzado el límite de notas, detener la grabación
            if midi_note_count >= max_notes:
                print(f"Se han grabado {midi_note_count} notas. Deteniendo grabación...")
                break

            # Dibujar las marcas de la mano
            mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

    # Mostrar video
    cv2.imshow("Hand Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Si alcanzamos el límite de notas, salir del bucle
    if midi_note_count >= max_notes:
        break

# Verificar si el archivo MIDI tiene alguna nota antes de intentar guardarlo
if len(track) > 2:  # Si hay al menos un mensaje de "note_on"
    try:
        # Imprimir los primeros 10 mensajes para depuración
        print(f"Primeros 10 mensajes del track: {track[:10]}")  # Depuración

        # Verificar si el archivo MIDI tiene contenido antes de guardar
        print("Guardando archivo MIDI...")
        midi_file.save(midi_file_path)
        print(f"Archivo MIDI guardado correctamente en: {midi_file_path}")
    except OSError as e:
        print(f"Error al guardar el archivo MIDI: {e}")
    except Exception as e:
        print(f"Error inesperado al guardar el archivo MIDI: {e}")
else:
    print("No se han agregado notas MIDI al archivo, no se guardará.")

# Liberar recursos
cap.release()
cv2.destroyAllWindows()
