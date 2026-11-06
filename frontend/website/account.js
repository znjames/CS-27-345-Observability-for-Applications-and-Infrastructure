async function fetchBalance() {
    const token = localStorage.getItem('authToken');
    if (!token) {
        window.location.href = 'index.html';
        return;
    }

    try {
        const response = await fetch('/api/balance', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        if (response.ok) {
            document.getElementById('balance').textContent = `$${data.balance.toFixed(2)}`;
        } else {
            document.getElementById('balance').textContent = 'Error: ' + data.message;
            localStorage.removeItem('authToken');
        }
    } catch (err) {
        document.getElementById('balance').textContent = 'Network error';
    }
}

document.addEventListener('DOMContentLoaded', fetchBalance);