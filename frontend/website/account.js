async function fetchBalance() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'account.html';
        return;
    }

    try {
        const response = await fetch('/api/balance', {
            headers: { 'Authorization': token }
        });
        const data = await response.json();
        if (response.ok) {
            document.getElementById('balance').textContent = `$${data.balance.toFixed(2)}`;
        } else {
            document.getElementById('balance').textContent = 'Error: ' + data.message;
            localStorage.removeItem('token');
        }
    } catch (err) {
        document.getElementById('balance').textContent = 'Network error';
    }
}

document.addEventListener('DOMContentLoaded', fetchBalance);