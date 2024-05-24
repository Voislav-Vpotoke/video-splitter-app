from flask import Flask, request, render_template, redirect, url_for, send_file, after_this_request, abort, jsonify
import os
from werkzeug.utils import secure_filename
from video_processing import load_texts, split_video
from loguru import logger

app = Flask(__name__)

# Настройка логирования
logger.add("logs/general.log", rotation="10 MB", level="INFO")
logger.add("logs/critical.log", rotation="10 MB", level="ERROR", filter=lambda record: record["level"].name == "ERROR")

# Конфигурация приложения
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1 GB
ALLOWED_EXTENSIONS = {'mp4', 'mkv', 'mp3', 'wav', 'txt'}
ALLOWED_VIDEO_MIME_TYPES = ['video/mp4', 'video/x-matroska']
ALLOWED_AUDIO_MIME_TYPES = ['audio/mpeg', 'audio/wav']
ALLOWED_TEXT_MIME_TYPES = ['text/plain']

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_mime_type(file, allowed_mime_types):
    return file.content_type in allowed_mime_types


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            video_file = request.files.get('video')
            audio_file = request.files.get('audio')
            text_file = request.files.get('texts')
            modified_text = request.form.get('modified_text')

            if not video_file or not audio_file or not text_file:
                return "Необходимо предоставить все файлы (видео, аудио, текст).", 400

            # Проверка расширений файлов
            if not (allowed_file(video_file.filename) and allowed_file(audio_file.filename) and allowed_file(
                    text_file.filename)):
                return "Неверный тип файла.", 400

            # Проверка MIME-типов
            if not allowed_mime_type(video_file, ALLOWED_VIDEO_MIME_TYPES):
                return "Неверный тип видео файла.", 400
            if not allowed_mime_type(audio_file, ALLOWED_AUDIO_MIME_TYPES):
                return "Неверный тип аудио файла.", 400
            if not allowed_mime_type(text_file, ALLOWED_TEXT_MIME_TYPES):
                return "Неверный тип текстового файла.", 400

            uploads_dir = os.path.join(BASE_DIR, 'uploads')
            output_dir = os.path.join(BASE_DIR, 'output')

            video_filename = secure_filename(video_file.filename)
            audio_filename = secure_filename(audio_file.filename)
            text_filename = secure_filename(text_file.filename)

            video_path = os.path.join(uploads_dir, video_filename)
            audio_path = os.path.join(uploads_dir, audio_filename)
            text_path = os.path.join(uploads_dir, text_filename)

            logger.info(f"Получен видео файл: {video_path}")
            logger.info(f"Получен аудио файл: {audio_path}")
            logger.info(f"Получен текстовый файл: {text_path}")

            try:
                with open(video_path, 'wb') as vf:
                    vf.write(video_file.read())
                with open(audio_path, 'wb') as af:
                    af.write(audio_file.read())
                with open(text_path, 'wb') as tf:
                    tf.write(text_file.read())
            except IOError as e:
                logger.error(f"Ошибка при сохранении файлов: {e}")
                return "Ошибка при сохранении файлов. Пожалуйста, попробуйте снова.", 500

            # Проверка на существование файлов
            if not (os.path.exists(video_path) and os.path.exists(audio_path) and os.path.exists(text_path)):
                return "Ошибка при сохранении файлов.", 500

            os.makedirs(output_dir, exist_ok=True)

            if modified_text:
                text_list = modified_text.split('\n')
            else:
                try:
                    text_list = load_texts(text_path)
                except Exception as e:
                    logger.error(f"Ошибка при загрузке текстового файла: {e}")
                    return "Ошибка при загрузке текстового файла. Пожалуйста, убедитесь, что файл правильно отформатирован.", 500

            try:
                split_video(video_path, output_dir, 15, audio_path, text_list)
            except ValueError as e:
                logger.error(f"Ошибка при проверке текстового файла: {e}")
                return f"Ошибка при проверке текстового файла: {e}", 400
            except Exception as e:
                logger.error(f"Ошибка при обработке видео: {e}")
                return "Ошибка при обработке видео. Пожалуйста, убедитесь, что файлы правильно отформатированы.", 500

            # Удаление загруженных файлов после обработки
            try:
                os.remove(video_path)
                os.remove(audio_path)
                os.remove(text_path)
                logger.info(f"Удалены файлы: {video_path}, {audio_path}, {text_path}")
            except Exception as e:
                logger.error(f"Ошибка при удалении файлов: {e}")

        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}")
            return f"Произошла непредвиденная ошибка: {e}. Пожалуйста, попробуйте позже.", 500

        return redirect(url_for('download'))
    return render_template('index.html')


@app.route('/download')
def download():
    output_dir = os.path.join(BASE_DIR, 'output')
    files = os.listdir(output_dir)
    return render_template('download.html', files=files)


@app.route('/download/<filename>')
def download_file(filename):
    output_dir = os.path.join(BASE_DIR, 'output')
    file_path = os.path.join(output_dir, filename)

    if not os.path.exists(file_path):
        logger.error(f"Файл не найден: {file_path}")
        abort(404)

    return send_file(file_path, as_attachment=True)


@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    output_dir = os.path.join(BASE_DIR, 'output')
    file_path = os.path.join(output_dir, filename)

    if not os.path.exists(file_path):
        logger.error(f"Файл не найден: {file_path}")
        return jsonify({"error": "Файл не найден"}), 404

    try:
        os.remove(file_path)
        logger.info(f"Удален файл: {file_path}")
        return jsonify({"success": "Файл удален"}), 200
    except Exception as e:
        logger.error(f"Ошибка при удалении файла: {e}")
        return jsonify({"error": "Ошибка при удалении файла"}), 500


if __name__ == '__main__':
    uploads_dir = os.path.join(BASE_DIR, 'uploads')
    output_dir = os.path.join(BASE_DIR, 'output')
    logs_dir = os.path.join(BASE_DIR, 'logs')

    os.makedirs(uploads_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)

    logger.info("Запуск Flask приложения")
    app.run(debug=True)
