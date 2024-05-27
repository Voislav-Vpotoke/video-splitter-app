import os
import moviepy.editor as mp
from loguru import logger

logger.add("logs/general.log", rotation="10 MB", level="INFO")
logger.add("logs/critical.log", rotation="10 MB", level="ERROR", filter=lambda record: record["level"].name == "ERROR")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Путь к шрифту
FONT_PATH = os.path.join(BASE_DIR, 'fonts', 'DejaVuSans-Bold.ttf')
# EMOJI_FONT_PATH = os.path.join(BASE_DIR, 'fonts', 'NotoColorEmoji.ttf')

def load_text_blocks(file_path):
    logger.info(f"Загрузка текстов из {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    text_blocks = [block.strip() for block in content.split('\n\n') if block.strip()]
    return text_blocks

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
    """Создание текстового клипа с фоновым цветом только вокруг текста."""
    lines = text.split('\n')
    title = lines[0]
    body = '\n'.join(lines[1:])

    # Настройки отступов
    margin_top = 100
    margin_left = 60

    # Создание заголовка
    title_clip = mp.TextClip(title, fontsize=40, font=FONT_PATH, color='white', method='caption', align='center',
                             size=(video_size[0] - 2 * margin_left, None))
    title_clip = title_clip.on_color(size=(title_clip.w + 20, title_clip.h + 20), color=(0, 0, 0), col_opacity=0.6)
    title_clip = title_clip.set_position(('center', margin_top)).set_duration(duration)

    # Создание тела текста с эмодзи
    body_lines = [f"{line}" for line in lines[1:]]
    formatted_body = '\n'.join(body_lines)
    body_clip = mp.TextClip(formatted_body, fontsize=30, font=FONT_PATH, color='white', method='caption',
                            align='west',
                            size=(video_size[0] - 2 * margin_left, None))
    body_clip = body_clip.on_color(size=(body_clip.w + 20, body_clip.h + 20), color=(0, 0, 0), col_opacity=0.6)
    body_clip = body_clip.set_position((margin_left, title_clip.size[1] + margin_top + 40)).set_duration(duration)

    # Создание текстового клипа с фоновым цветом только вокруг текста
    txt_clip = mp.CompositeVideoClip([title_clip, body_clip], size=video_size)
    txt_clip = txt_clip.set_duration(duration)

    return txt_clip

def split_video(input_path, output_dir, chunk_duration, audio_track_path, text_blocks):
    logger.info(f"Разделение видео: {input_path} на части по {chunk_duration} секунд")
    video = mp.VideoFileClip(input_path)
    video_duration = video.duration
    audio = mp.AudioFileClip(audio_track_path)

    for i, text_chunk in enumerate(text_blocks):
        start = i * chunk_duration
        end = min((i + 1) * chunk_duration, video_duration)

        if start >= video_duration:
            break

        video_chunk = video.subclip(start, end)

        # Обработка аудио для текущего куска
        if audio.duration < (end - start):
            audio_chunk = repeat_audio(audio, end - start)
        else:
            audio_chunk = audio.subclip(start, end)

        video_chunk = video_chunk.set_audio(audio_chunk)

        # Применение текста к видеофрагменту
        txt_clip = create_text_clip(text_chunk, end - start, video.size)
        video_chunk = mp.CompositeVideoClip([video_chunk, txt_clip])

        output_path = os.path.join(output_dir, f"chunk_{i}.mp4")
        logger.info(f"Сохранение фрагмента видео в {output_path}")
        video_chunk.write_videofile(output_path, codec="libx264")

if __name__ == '__main__':
    input_path = 'path_to_your_video.mp4'
    output_dir = 'output'
    chunk_duration = 15  # Продолжительность каждого куска в секундах
    audio_track_path = 'path_to_your_audio.mp3'
    text_path = 'path_to_your_text_file.txt'

    os.makedirs(output_dir, exist_ok=True)

    text_blocks = load_text_blocks(text_path)
    split_video(input_path, output_dir, chunk_duration, audio_track_path, text_blocks)
