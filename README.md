# video-splitter-app
# Приложение для Разделения Видео

Этот проект представляет собой веб-приложение на основе Flask, которое позволяет загружать видео, аудиофайл и текстовый файл. Приложение разделяет видео на куски по 15 секунд, накладывает на каждый кусок аудиофайл и добавляет текст из предоставленного текстового файла.

## Возможности

- Загрузка видео, аудиофайлов и текстовых файлов через веб-интерфейс.
- Разделение видео на куски по 15 секунд.
- Наложение аудиофайла на каждый кусок видео.
- Добавление текста из предоставленного текстового файла к каждому куску видео.
- Скачивание обработанных кусков видео.

## Установка

1. Клонируйте репозиторий:
    ```sh
    git clone https://github.com/yourusername/video-splitter-app.git
    cd video-splitter-app
    ```

2. Создайте виртуальное окружение:
    ```sh
    python -m venv venv
    ```

3. Активируйте виртуальное окружение:

    - В Windows:
        ```sh
        venv\Scripts\activate
        ```
    - В macOS и Linux:
        ```sh
        source venv/bin/activate
        ```

4. Установите зависимости:
    ```sh
    pip install -r requirements.txt
    ```

## Деплой

Для деплоя приложения на сервере, например, с использованием Gunicorn и Nginx, выполните следующие шаги:

### Настройка Gunicorn

1. Установите Gunicorn:
    ```sh
    pip install gunicorn
    ```

2. Запустите приложение с помощью Gunicorn:
    ```sh
    gunicorn -w 4 app:app
    ```
    Здесь `-w 4` указывает на использование 4 рабочих процессов.

### Настройка Nginx

1. Установите Nginx (если он еще не установлен):
    ```sh
    sudo apt update
    sudo apt install nginx
    ```

2. Настройте конфигурацию Nginx для вашего приложения. Откройте конфигурационный файл Nginx:
    ```sh
    sudo nano /etc/nginx/sites-available/video-splitter-app
    ```

3. Добавьте следующую конфигурацию:
    ```nginx
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
    ```

4. Активируйте конфигурацию, создав символическую ссылку:
    ```sh
    sudo ln -s /etc/nginx/sites-available/video-splitter-app /etc/nginx/sites-enabled
    ```

5. Перезапустите Nginx, чтобы применить изменения:
    ```sh
    sudo systemctl restart nginx
    ```

### Настройка systemd для Gunicorn

1. Создайте файл службы systemd:
    ```sh
    sudo nano /etc/systemd/system/video-splitter-app.service
    ```

2. Добавьте следующую конфигурацию:
    ```ini
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
    ```

3. Перезапустите systemd, чтобы учесть новый файл службы:
    ```sh
    sudo systemctl daemon-reload
    ```

4. Запустите службу и настройте ее на автозапуск:
    ```sh
    sudo systemctl start video-splitter-app
    sudo systemctl enable video-splitter-app
    ```

Теперь ваше приложение должно быть доступно по вашему доменному имени или IP-адресу.

## Структура файлов

- `app.py`: Основной файл приложения Flask.
- `templates/index.html`: HTML-шаблон для страницы загрузки.
- `templates/download.html`: HTML-шаблон для страницы загрузки обработанных видео.
- `uploads/`: Директория для хранения загруженных файлов.
- `output/`: Директория для хранения обработанных кусков видео.

## Зависимости

- Flask
- moviepy
- loguru

## Добавление текстов

Текстовый файл должен содержать текст для каждого куска, разделенный по строкам. Каждая строка соответствует 15-секундному куску видео. Например:

Текст для первого куска
Текст для второго куска
Текст для третьего куска
...

shell


## Пример текстового файла

Добро пожаловать в видео!
Это второй кусок.
Это третий кусок.
...

perl


## Логирование

Логи генерируются с использованием библиотеки `loguru` и сохраняются в файлы `file_{time}.log`. Логи включают информацию о загрузке файлов, этапах обработки и любых возникающих ошибках.

## Вклад

1. Сделайте форк репозитория.
2. Создайте новую ветку:
    ```sh
    git checkout -b feature-branch
    ```
3. Внесите свои изменения:
    ```sh
    git commit -m "Добавление новой функции"
    ```
4. Отправьте изменения в ветку:
    ```sh
    git push origin feature-branch
    ```
5. Создайте pull request.

## Лицензия

Этот проект лицензирован под MIT License. См. файл `LICENSE` для получения дополнительной информации.

