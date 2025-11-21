const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('audioFile');
const transcribeBtn = document.getElementById('transcribeBtn');
const loading = document.getElementById('loading');
const resultsSection = document.getElementById('resultsSection');
const error = document.getElementById('error');
const fileInfo = document.getElementById('fileInfo');
const originalText = document.getElementById('originalText');
const correctedText = document.getElementById('correctedText');

let selectedFile = null;

uploadArea.addEventListener('click', () => fileInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragging');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragging');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragging');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

function handleFileSelect(file) {
    selectedFile = file;
    const sizeMB = (file.size / 1024 / 1024).toFixed(2);
    fileInfo.innerHTML = `<strong>📁 Arquivo:</strong> ${file.name} | <strong>📊 Tamanho:</strong> ${sizeMB} MB`;
    fileInfo.classList.add('show');
    transcribeBtn.disabled = false;
    resultsSection.classList.remove('show');
    error.classList.remove('show');
}

transcribeBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('audio', selectedFile);

    transcribeBtn.disabled = true;
    loading.classList.add('show');
    resultsSection.classList.remove('show');
    error.classList.remove('show');

    try {
        const response = await fetch('http://localhost:8000/api/transcribe/', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            originalText.textContent = data.transcription;
            correctedText.textContent = data.corrected_text;
            resultsSection.classList.add('show');
        } else {
            error.textContent = `❌ Erro: ${data.error || 'Erro desconhecido ao processar o áudio'}`;
            error.classList.add('show');
        }
    } catch (err) {
        error.textContent = `❌ Erro de conexão: ${err.message}. Verifique se o servidor está rodando.`;
        error.classList.add('show');
    } finally {
        loading.classList.remove('show');
        transcribeBtn.disabled = false;
    }
});

function copyText(elementId) {
    const text = document.getElementById(elementId).textContent;
    navigator.clipboard.writeText(text).then(() => {
        alert('✅ Texto copiado para a área de transferência!');
    });
}
