from flask import Flask, request, render_template, redirect, url_for
import moviepy.editor as mp
import os
from loguru import logger

app = Flask(__name__)

logger.add("file_{time}.log", rotation="10 MB")


def load_texts(file_path):
    logger.info(f"Loading texts from {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        texts = file.readlines()
    return [text.strip() for text in texts]


def repeat_audio(audio, duration):
    """Повтор аудиофайла до заданной продолжительности."""
    repeated_clips = []
    current_duration = 0

    while current_duration < duration:
        clip_duration = min(audio.duration, duration - current_duration)
        repeated_clips.append(audio.subclip(0, clip_duration))
        current_duration += clip_duration

    return mp.concatenate_audioclips(repeated_clips)


def create_text_clip(text, duration, video_size):
    """Создание текстового клипа с разбиением на строки."""
    lines = text.split('\n')
    formatted_text = '\n'.join(lines)
    txt_clip = mp.TextClip(formatted_text, fontsize=44, color='white', size=video_size, method='caption',
                           align='center')
    txt_clip = txt_clip.set_pos('center').set_duration(duration)
    return txt_clip


def split_video(input_path, output_dir, chunk_duration, audio_track_path, text_list):
    logger.info(f"Splitting video: {input_path} into chunks of {chunk_duration} seconds")
    video = mp.VideoFileClip(input_path)
    video_duration = video.duration
    audio = mp.AudioFileClip(audio_track_path)

    if audio.duration < chunk_duration:
        audio = repeat_audio(audio, chunk_duration)

    for i in range(0, int(video_duration), chunk_duration):
        start = i
        end = min(i + chunk_duration, video_duration)
        video_chunk = video.subclip(start, end)
        video_chunk = video_chunk.set_audio(audio.subclip(0, end - start))

        if i // chunk_duration < len(text_list):
            txt_clip = create_text_clip(text_list[i // chunk_duration], end - start, video.size)
            video_chunk = mp.CompositeVideoClip([video_chunk, txt_clip])

        output_path = os.path.join(output_dir, f"chunk_{i // chunk_duration}.mp4")
        logger.info(f"Saving video chunk to {output_path}")
        video_chunk.write_videofile(output_path, codec="libx264")


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            video_file = request.files['video']
            audio_file = request.files['audio']
            text_file = request.files['texts']

            video_path = os.path.join('uploads', video_file.filename)
            audio_path = os.path.join('uploads', audio_file.filename)
            text_path = os.path.join('uploads', text_file.filename)

            logger.info(f"Received video file: {video_path}")
            logger.info(f"Received audio file: {audio_path}")
            logger.info(f"Received text file: {text_path}")

            video_file.save(video_path)
            audio_file.save(audio_path)
            text_file.save(text_path)

            output_dir = os.path.join('output')
            os.makedirs(output_dir, exist_ok=True)

            text_list = load_texts(text_path)

            split_video(video_path, output_dir, 15, audio_path, text_list)
        except Exception as e:
            logger.error(f"Error processing files: {e}")
            return str(e)

        return redirect(url_for('download'))
    return render_template('index.html')


@app.route('/download')
def download():
    files = os.listdir('output')
    return render_template('download.html', files=files)


if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('output', exist_ok=True)
    logger.info("Starting the Flask application")
    app.run(debug=True)
