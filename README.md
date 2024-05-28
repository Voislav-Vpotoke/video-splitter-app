# video-splitter-app
# Приложение для Разделения Видео

Этот проект представляет собой веб-приложение на основе Flask, которое позволяет загружать видео, аудиофайл и текстовый файл. Приложение разделяет видео на куски по 15 секунд, накладывает на каждый кусок аудиофайл и добавляет текст из предоставленного текстового файла.

## Возможности

- Загрузка видео, аудиофайлов и текстовых файлов через веб-интерфейс.
- Предварительный просмотр и редактирование текстового файла перед загрузкой.
- Предварительный просмотр видео и аудио файлов перед загрузкой.
- Разделение видео на куски по 15 секунд.
- Наложение аудиофайла на каждый кусок видео.
- Добавление текста из предоставленного текстового файла к каждому куску видео.
- Скачивание и проигрывание обработанных кусков видео.

## Установка

Клонируйте репозиторий:

```bash
git clone https://github.com/Voislav-Vpotoke/video-splitter-app.git
cd video-splitter-app

Создайте виртуальное окружение:

bash

python -m venv venv

Активируйте виртуальное окружение:

    В Windows:

bash

venv\Scripts\activate

    В macOS и Linux:

bash

source venv/bin/activate

Установите зависимости:

bash

pip install -r requirements.txt

Деплой

Для деплоя приложения на сервере, например, с использованием Gunicorn и Nginx, выполните следующие шаги:
Настройка Gunicorn

Установите Gunicorn:

bash

pip install gunicorn

Запустите приложение с помощью Gunicorn:

bash

gunicorn -w 4 app:app

Здесь -w 4 указывает на использование 4 рабочих процессов.
Настройка Nginx

Установите Nginx (если он еще не установлен):

bash

sudo apt update
sudo apt install nginx

Настройте конфигурацию Nginx для вашего приложения. Откройте конфигурационный файл Nginx:

bash

sudo nano /etc/nginx/sites-available/video-splitter-app

Добавьте следующую конфигурацию:

nginx

server {
    listen 80;
    server_name your_domain_or_IP;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path_to_your_project/static/;
    }
}

Активируйте конфигурацию, создав символическую ссылку:

bash

sudo ln -s /etc/nginx/sites-available/video-splitter-app /etc/nginx/sites-enabled

Перезапустите Nginx, чтобы применить изменения:

bash

sudo systemctl restart nginx

Настройка systemd для Gunicorn

Создайте файл службы systemd:

bash

sudo nano /etc/systemd/system/video-splitter-app.service

Добавьте следующую конфигурацию:

ini

[Unit]
Description=Gunicorn instance to serve video-splitter-app
After=network.target

[Service]
User=your_user
Group=www-data
WorkingDirectory=/path_to_your_project
Environment="PATH=/path_to_your_project/venv/bin"
ExecStart=/path_to_your_project/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app

[Install]
WantedBy=multi-user.target

Перезапустите systemd, чтобы учесть новый файл службы:

bash

sudo systemctl daemon-reload

Запустите службу и настройте ее на автозапуск:

bash

sudo systemctl start video-splitter-app
sudo systemctl enable video-splitter-app

Теперь ваше приложение должно быть доступно по вашему доменному имени или IP-адресу.
Структура файлов

    app.py: Основной файл приложения Flask.
    templates/index.html: HTML-шаблон для страницы загрузки.
    templates/download.html: HTML-шаблон для страницы загрузки обработанных видео.
    static/scripts.js: JavaScript файл для обработки логики на клиентской стороне.
    uploads/: Директория для хранения загруженных файлов.
    output/: Директория для хранения обработанных кусков видео.
    logs/: Директория для хранения логов.

Зависимости

    Flask
    moviepy
    loguru

Добавление текстов

Текстовый файл должен содержать текст для каждого куска, разделенный по строкам. Каждая строка соответствует 15-секундному куску видео. Например:

Текст для первого куска
Текст для второго куска
Текст для третьего куска

Логирование

Логи генерируются с использованием библиотеки loguru и сохраняются в файлы general.log и critical.log. Логи включают информацию о загрузке файлов, этапах обработки и любых возникающих ошибках.
Лицензия

Этот проект лицензирован под MIT License. См. файл LICENSE для получения дополнительной информации.
