let stopwatchInterval;
let stopwatchTime = 0;
let stopwatchRunning = false;

function startStopwatch() {
    if (!stopwatchRunning) {
        stopwatchRunning = true;
        stopwatchInterval = setInterval(() => {
            stopwatchTime++;
            document.getElementById('stopwatch-display').innerText = formatTime(stopwatchTime);
        }, 1000);
    }
}

function stopStopwatch() {
    if (stopwatchRunning) {
        clearInterval(stopwatchInterval);
        stopwatchRunning = false;
    }
}

function resetStopwatch() {
    clearInterval(stopwatchInterval);
    stopwatchTime = 0;
    document.getElementById('stopwatch-display').innerText = formatTime(stopwatchTime);
    stopwatchRunning = false;
}



let timerInterval;
let timerTime = 0;

function startTimer() {
    const minutes = parseInt(document.getElementById('timer-minutes').value) || 0;
    const seconds = parseInt(document.getElementById('timer-seconds').value) || 0;
    timerTime = (minutes * 60) + seconds;

    if (isNaN(timerTime) || timerTime <= 0) {
        alert('Please enter a valid number of minutes and/or seconds');
        return;
    }

    timerInterval = setInterval(() => {
        if (timerTime <= 0) {
            clearInterval(timerInterval);
            playAlarm();
            alert('Time is up!');
            stopAlarm();
        } else {
            timerTime--;
            document.getElementById('timer-display').innerText = formatTime(timerTime);
        }
    }, 1000);
}

function stopTimer() {
    clearInterval(timerInterval);
    stopAlarm();
}

function resetTimer() {
    clearInterval(timerInterval);
    timerTime = 0;
    document.getElementById('timer-display').innerText = formatTime(timerTime);
    document.getElementById('timer-minutes').value = '';
    document.getElementById('timer-seconds').value = '';
    stopAlarm();
}

function playAlarm() {
    const alarmSound = document.getElementById('alarm-sound');
    alarmSound.play().catch(error => {
        console.error('Error playing the audio:', error);
    });
}

function stopAlarm() {
    const alarmSound = document.getElementById('alarm-sound');
    alarmSound.pause();
    alarmSound.currentTime = 0; 
}

function formatTime(seconds) {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${pad(hrs)}:${pad(mins)}:${pad(secs)}`;
}

function pad(number) {
    return number < 10 ? '0' + number : number;
}