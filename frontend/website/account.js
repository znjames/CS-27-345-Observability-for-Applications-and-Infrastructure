async function fetchBalance() {
    const token = localStorage.getItem('authToken');
    if (!token) {
        window.location.href = 'index.html';
        return;
    }

    try {
        const response = await fetch('/api/auth/balance', {
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

async function deposit() {
    await makeTransaction('deposit');
}

async function withdraw() {
    await makeTransaction('withdraw');
}

async function makeTransaction() {
    const token = localStorage.getItem('authToken');
    const amount = parseFloat(document.getElementById('amount').value);
    const message = document.getElementById('message');

    if (!amount || amount <= 0 || !Number.isFinite(amount)) {
        message.textContent = 'Please enter a valid amount.';
        return;
    }

    try {
        const response = await fetch('/api/auth/balance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ${token}'
            },
            body: JSON.stringify({ amount: amount })
        });

        const data = await response.json();

        if (response.ok) {
            message.textContent = data.message;
            document.getElementById('amount').value = '';

            await fetchBalance();
        } else {
            message.textContent = 'Error: ' + data.message;
        }
    } catch (err) {
        message.textContent = 'Network error.';
    }

}

document.addEventListener('DOMContentLoaded', fetchBalance);