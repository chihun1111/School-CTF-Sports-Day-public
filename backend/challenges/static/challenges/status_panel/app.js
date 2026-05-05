async function loadStatus() {
  const response = await fetch('/api/status');
  const data = await response.json();

  document.querySelector('#status').innerText = data.message;
}

loadStatus();

// Development-only test API
// Remove before deployment: /api/debug
