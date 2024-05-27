function showLoading() {
    document.getElementById('upload-form').style.display = 'none';
    document.getElementById('loading').style.display = 'block';
}

function validateFiles() {
    const videoFile = document.getElementById('video').files[0];
    const audioFile = document.getElementById('audio').files[0];
    const textFile = document.getElementById('texts').files[0];
    const textContent = document.getElementById('text-content').value;

    const allowedVideoTypes = ['video/mp4', 'video/x-matroska'];
    const allowedAudioTypes = ['audio/mpeg', 'audio/wav'];
    const allowedTextTypes = ['text/plain'];

    if (videoFile && !allowedVideoTypes.includes(videoFile.type)) {
        alert('Неверный тип видео файла. Допустимые форматы: mp4, mkv.');
        return false;
    }
    if (audioFile && !allowedAudioTypes.includes(audioFile.type)) {
        alert('Неверный тип аудио файла. Допустимые форматы: mp3, wav.');
        return false;
    }
    if (textFile && !allowedTextTypes.includes(textFile.type)) {
        alert('Неверный тип текстового файла. Допустимый формат: txt.');
        return false;
    }

    // Сохраняем измененный текст в скрытом input
    const hiddenInput = document.createElement('input');
    hiddenInput.type = 'hidden';
    hiddenInput.name = 'modified_text';
    hiddenInput.value = textContent;
    document.getElementById('upload-form').appendChild(hiddenInput);

    showLoading();
    return true;
}

function updateFileLabel(inputId) {
    const input = document.getElementById(inputId);
    const label = document.getElementById(`${inputId}-label`);
    if (input.files.length > 0) {
        label.textContent = input.files[0].name;
    } else {
        label.textContent = 'Файл не выбран';
    }
}

function previewTextFile() {
    const input = document.getElementById('texts');
    const preview = document.getElementById('text-preview');
    const content = document.getElementById('text-content');

    if (input.files.length > 0) {
        const file = input.files[0];
        const reader = new FileReader();

        reader.onload = function(e) {
            content.value = e.target.result;
            preview.style.display = 'block';
        }

        reader.readAsText(file);
    } else {
        preview.style.display = 'none';
        content.value = '';
    }
}

function previewVideoFile() {
    const input = document.getElementById('video');
    const preview = document.getElementById('video-preview');

    if (input.files.length > 0) {
        const file = input.files[0];
        const reader = new FileReader();

        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        }

        reader.readAsDataURL(file);
    } else {
        preview.style.display = 'none';
        preview.src = '';
    }
}

function previewAudioFile() {
    const input = document.getElementById('audio');
    const preview = document.getElementById('audio-preview');

    if (input.files.length > 0) {
        const file = input.files[0];
        const reader = new FileReader();

        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        }

        reader.readAsDataURL(file);
    } else {
        preview.style.display = 'none';
        preview.src = '';
    }
}

function deleteFile(fileName) {
    fetch(`/delete/${fileName}`, {
        method: 'DELETE',
    })
    .then(response => {
        if (response.ok) {
            location.reload();
        } else {
            response.json().then(data => {
                alert(data.error);
            });
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Ошибка при удалении файла');
    });
}