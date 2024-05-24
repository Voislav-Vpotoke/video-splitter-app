import moviepy.editor as mp
import os
from loguru import logger

logger.add("logs/general.log", rotation="10 MB", level="INFO")
logger.add("logs/critical.log", rotation="10 MB", level="ERROR", filter=lambda record: record["level"].name == "ERROR")


def load_texts(file_path):
    logger.info(f"Загрузка текстов из {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    texts = [text.strip() for text in content.split('---') if text.strip()]
    return texts


def check_texts(text_list, video_duration, chunk_duration):
    if not text_list:
        raise ValueError("Текстовый файл пуст.")

    expected_chunks = int(video_duration // chunk_duration) + (1 if video_duration % chunk_duration > 0 else 0)
    if len(text_list) < expected_chunks:
        raise ValueError(f"Недостаточно текста: требуется {expected_chunks}, но найдено {len(text_list)} блоков(а).")


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
    """Создание текстового клипа с фоновым цветом и стилизованным текстом."""
    lines = text.split('\n')
    formatted_text = '\n'.join(lines)
    txt_clip = mp.TextClip(formatted_text, fontsize=70, font='DejaVuSans-Bold', color='white', method='caption',
                           align='center', size=(video_size[0] - 60, None))
    txt_clip = txt_clip.on_color(color=(0, 0, 0), col_opacity=0.6).set_pos('center').set_duration(duration)
    return txt_clip


def split_video(input_path, output_dir, chunk_duration, audio_track_path, text_list):
    logger.info(f"Разделение видео: {input_path} на части по {chunk_duration} секунд")
    video = mp.VideoFileClip(input_path)
    video_duration = video.duration
    audio = mp.AudioFileClip(audio_track_path)

    check_texts(text_list, video_duration, chunk_duration)

    for i in range(0, int(video_duration), chunk_duration):
        start = i
        end = min(i + chunk_duration, video_duration)
        video_chunk = video.subclip(start, end)

        # Обработка аудио для текущего куска
        if audio.duration < chunk_duration:
            audio_chunk = repeat_audio(audio, chunk_duration)
        else:
            audio_chunk = audio.subclip(start, end)

        video_chunk = video_chunk.set_audio(audio_chunk)

        # Применение текста к видеофрагменту
        text_index = i // chunk_duration
        if text_index < len(text_list):
            txt_clip = create_text_clip(text_list[text_index], end - start, video.size)
            video_chunk = mp.CompositeVideoClip([video_chunk, txt_clip])
        else:
            logger.warning(f"Нет текста для фрагмента {text_index}")

        output_path = os.path.join(output_dir, f"chunk_{text_index}.mp4")
        logger.info(f"Сохранение фрагмента видео в {output_path}")
        video_chunk.write_videofile(output_path, codec="libx264")
