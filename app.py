import random
from flask import Flask, redirect, request, render_template, send_from_directory, url_for
from moviepy.editor import AudioFileClip, VideoFileClip
from werkzeug.utils import secure_filename
import os
from utils import process_image
from utils_video import process_video
from uuid import uuid4

app = Flask(__name__, static_folder='processed')  # Servir archivos estáticos desde 'processed'
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'processed'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Para servir imágenes estáticas desde processed
@app.route('/processed/<path:filename>')
def processed_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Imagenes

@app.route('/imagenes')
def imagenes():
    return render_template('image_form.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'images' not in request.files:
        return "No se encontraron archivos", 400

    # Obtener redes sociales seleccionadas
    selected_networks = request.form.getlist('networks')
    if not selected_networks:
        return "No seleccionaste ningún formato de red social.", 400

    files = request.files.getlist('images')
    saved_files = []
    previews = []

    for file in files:
        if file.filename.endswith(('.png', '.jpg', '.jpeg', '.webp')):
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)

            process_image(input_path, OUTPUT_FOLDER, filename, selected_networks)

            for network in selected_networks:
                previews.append({
                    'network': network,
                    'path': f'/processed/{network}/{filename}'
                })

    return render_template('index.html', previews=previews)

# Videos

@app.route('/videos', methods=['GET', 'POST'])
def videos():
    if request.method == 'POST':
        # Aquí va tu código para procesar el video
        # Por ejemplo, tomar el archivo del formulario
        video_file = request.files['video']  # Asegúrate de tener un campo con name="video" en tu formulario
        
        if video_file:
            # Guardar el archivo, procesarlo, y luego hacer lo que necesites
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_file.filename)
            video_file.save(video_path)

            # Ahora procesas el video y lo guardas en la carpeta "processed"
            processed_video_path = os.path.join(app.static_folder, 'processed', video_file.filename)
            process_video(video_path, processed_video_path)  # Aquí llamas a tu función de procesamiento de video

            # Redirigir al usuario de vuelta a la lista de videos procesados
            return redirect(url_for('videos'))  # Esto hará que se recargue la página con los videos procesados

    # En el caso de GET, solo renderizamos el formulario
    processed_path = os.path.join(app.static_folder, 'processed')
    if not os.path.exists(processed_path):
        os.makedirs(processed_path)

    # Obtener todos los videos procesados
    videos = [f for f in os.listdir(processed_path) if f.endswith('.mp4')]

    return render_template('video_form.html', videos=videos)    

@app.route('/upload_video', methods=['POST'])
def upload_video():
    video_files = request.files.getlist('videos')
    audio_file = request.files['audio']
    formats = request.form.getlist('format')
    random_audio = 'random_audio' in request.form

    if not video_files:
        return "No se enviaron videos", 400

    audio_path = None
    if audio_file:
        audio_path = os.path.join('uploads', audio_file.filename)
        audio_file.save(audio_path)
        audio_duration = AudioFileClip(audio_path).duration
    else:
        audio_duration = 0

    output_folder = 'static/processed'
    os.makedirs(output_folder, exist_ok=True)

    previews = []

    # Divide el audio en segmentos únicos para cada video
    segment_durations = []
    total_video_duration = 0

    video_clips = []
    for video in video_files:
        video_path = os.path.join('uploads', video.filename)
        video.save(video_path)
        clip = VideoFileClip(video_path)
        video_clips.append((video_path, clip))
        segment_durations.append(clip.duration)
        total_video_duration += clip.duration

    current_time = 0
    for idx, (video_path, clip) in enumerate(video_clips):
        video_filename = os.path.basename(video_path)
        segment_start = 0
        if random_audio and audio_duration > clip.duration:
            max_start = audio_duration - clip.duration
            segment_start = random.uniform(0, max_start)
        else:
            segment_start = current_time

        process_video(
            video_path,
            output_folder,
            video_filename,
            formats,
            audio_path,
            random_audio=random_audio,
            audio_start=segment_start
        )

        current_time += clip.duration
        clip.close()

        for fmt in formats:
            previews.append({
                'filename': f"{os.path.splitext(video_filename)[0]}_{fmt}.mp4",
                'path': f"/static/processed/{os.path.splitext(video_filename)[0]}_{fmt}.mp4"
            })

    return render_template('video_form.html', videos=previews)

if __name__ == '__main__':
    app.run(debug=True)
