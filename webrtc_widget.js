const ws = new WebSocket('ws://localhost:8000/ws');
let recorder;
let transcriptDiv = document.createElement('div');
document.body.appendChild(transcriptDiv);

function start() {
  navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
    recorder = new MediaRecorder(stream);
    recorder.ondataavailable = e => ws.send(e.data);
    recorder.start(250);
  });
}

function stop() {
  recorder.stop();
  ws.send('__end__');
}

ws.onmessage = evt => {
  transcriptDiv.textContent = evt.data;
};

const startBtn = document.createElement('button');
startBtn.textContent = 'Start';
startBtn.onclick = start;
document.body.appendChild(startBtn);

const stopBtn = document.createElement('button');
stopBtn.textContent = 'Stop';
stopBtn.onclick = stop;
document.body.appendChild(stopBtn);
