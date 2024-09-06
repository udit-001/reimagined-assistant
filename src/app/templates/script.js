const micButton = document.getElementById('micButton');
const stopButton = document.getElementById('stopButton');

let mediaRecorder;
let audioChunks = [];
let currentAudio = null;
let stream = null;
let persona = document.querySelector("#agentSelect option[selected]").value;

function aiSpeaking() {
    const imageContainer = document.querySelector(".image-container")
    imageContainer.classList.add("blinking-border")
}

function showErrorMessage(show, msg) {
    const errorMessage = document.querySelector(".error-message")
    if (show == true) {
        errorMessage.classList.add("show")
        errorMessage.textContent = msg;
    }
    else {
        errorMessage.classList.remove("show")
    }
}

function aiNotSpeaking() {
    const imageContainer = document.querySelector(".image-container")
    imageContainer.classList.remove("blinking-border")
}

function updateProfile(selectedValue) {
    const options = document.querySelectorAll('#agentSelect option');
    const selectedOption = Array.from(options).find(option => option.value === selectedValue);

    if (selectedOption) {
        const avatar = selectedOption.dataset.image;
        persona = selectedOption.value;
        document.querySelector('.profile-photo').src = avatar;
    }
}

document.getElementById('agentSelect').addEventListener('change', function () {
    updateProfile(this.value);
});

function showLoadingMessage(show, msg = "Thinking...") {
    const loadingMessage = document.getElementById('loadingMessage');
    loadingMessage.textContent = msg;

    if (show) {
        loadingMessage.classList.add('show');
    } else {
        loadingMessage.classList.remove('show');
    }
}

function sendChunkToServer(chunk) {
    const formData = new FormData();
    formData.append('audio', chunk);

    showLoadingMessage(true);
    fetch('/api/upload_stream?persona=' + persona, {
        method: 'POST',
        body: formData
    })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const audio = document.createElement('audio');
            audio.src = url;
            audio.controls = false;

            if (currentAudio) {
                currentAudio.pause();
                currentAudio.currentTime = 0;
                aiNotSpeaking()
            }
            currentAudio = audio;

            aiSpeaking();
            audio.play();

            showLoadingMessage(false);


            audio.addEventListener('ended', () => {
                aiNotSpeaking();
            });
        })
        .catch(error => {
            console.error('Error uploading chunk:', error)
            aiNotSpeaking();
            showLoadingMessage(false);
            showErrorMessage(true, "Unable to reach the server, try after some time. 😔")
        });
}

micButton.addEventListener('click', async () => {
    const micIcon = document.querySelector("#micIcon")
    if (micButton.dataset.state === 'off') {
        micButton.dataset.state = "on"
        micIcon.src = "mic-on.svg"
        if (currentAudio) {
            currentAudio.pause();
            currentAudio.currentTime = 0;
            currentAudio = null;
            aiNotSpeaking();
        }

        await startRecording()
    } else {
        await stopRecording()
        micButton.dataset.state = "off"
        micIcon.src = "mic-off.svg"

    }
});

async function stopRecording() {
    if (mediaRecorder) {
        mediaRecorder.stop();

        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            console.log("Microphone stopped");
        }
    }
}

async function startRecording() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
            sendChunkToServer(event.data);
        };

        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            audioChunks = [];
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
        };

        mediaRecorder.start();
    } catch (error) {
        console.error('Error accessing the microphone', error);
        alert('Microphone access is required to record audio. Please allow microphone access in your browser settings.');
    }
}
