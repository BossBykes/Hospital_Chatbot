const sendBtn = document.getElementById('send-btn');
const msgInput = document.getElementById('msg-input');
const chatLog = document.getElementById('chat-log');

function appendMessage(text, cls) {
  const div = document.createElement('div');
  div.className = `message ${cls}`;
  div.innerText = text;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
}

async function sendMessage() {
  const msg = msgInput.value.trim();
  if (!msg) return;
  appendMessage(msg, 'user');
  msgInput.value = '';

  const res = await fetch('/api/get', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: msg })
  });
  const data = await res.json();
  appendMessage(data.response, 'bot');
}

sendBtn.addEventListener('click', sendMessage);
msgInput.addEventListener('keypress', e => { if (e.key === 'Enter') sendMessage(); });