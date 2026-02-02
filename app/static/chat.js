const sendBtn = document.getElementById('send-btn');
const msgInput = document.getElementById('msg-input');
const chatLog = document.getElementById('chat-log');

function appendMessage(text, cls, suggestions = null) {
  const div = document.createElement('div');
  div.className = `message ${cls}`;
  div.innerText = text;
  chatLog.appendChild(div);

  if (Array.isArray(suggestions) && suggestions.length) {
    const chips = document.createElement('div');
    chips.className = 'suggestions';
    suggestions.forEach(label => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'suggestion-chip';
      btn.innerText = label;
      btn.addEventListener('click', () => sendMessage(label));
      chips.appendChild(btn);
    });
    chatLog.appendChild(chips);
  }

  chatLog.scrollTop = chatLog.scrollHeight;
}

async function postMessage(msg) {
  const res = await fetch('/api/get', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: msg })
  });
  return res.json();
}

async function sendMessage(messageOverride = null) {
  const msg = (messageOverride ?? msgInput.value).trim();
  if (!msg) return;

  appendMessage(msg, 'user');
  msgInput.value = '';

  try {
    const data = await postMessage(msg);
    appendMessage(data.response, 'bot', data.suggestions || null);
  } catch (err) {
    appendMessage("Sorry - something went wrong on the server. Please try again.", 'bot');
  }
}

sendBtn.addEventListener('click', () => sendMessage());
msgInput.addEventListener('keypress', e => { if (e.key === 'Enter') sendMessage(); });

// Sidebar quick actions (buttons already have data-intent tags)
document.querySelectorAll('button[data-intent]').forEach(btn => {
  btn.addEventListener('click', () => {
    const intent = btn.getAttribute('data-intent');

    // Send a short phrase that matches existing patterns in intents.json
    const quickPrompts = {
      directions_parking_info: "Parking info",
      visiting_hours: "Visiting hours",
      faq_billing_insurance_cafeteria: "Billing",
      emergency_contact: "Emergency contact",
      appointment_booking: "Book an appointment"
    };

    sendMessage(quickPrompts[intent] || "Hello");
  });
});
