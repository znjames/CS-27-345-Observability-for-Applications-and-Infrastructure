async function fetchBalance() {
    const token = localStorage.getItem('authToken');
    if (!token) {
        window.location.href = 'index.html';
        return;
    }

    try {
        const response = await fetch('/api/banking/balance', {
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

async function makeTransaction(type) {
    const token = localStorage.getItem('authToken');
    const amount = parseFloat(document.getElementById('amount').value);
    const message = document.getElementById('message');

    if (!amount || amount <= 0 || !Number.isFinite(amount)) {
        message.textContent = 'Please enter a valid amount.';
        return;
    }

    try {
        const response = await fetch(`/api/banking/${type}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ amount: amount })
        });

        const data = await response.json();

        if (response.ok) {
            message.textContent = data.message;
            document.getElementById('amount').value = '';

            await accountDetail();

        } else {
            message.textContent = 'Error: ' + data.message;
        }
    } catch (err) {
        message.textContent = 'Network error.';
    }

}

async function fetchHistory() {
    const token = localStorage.getItem('authToken');
    if (!token) return;

    try {
        const response = await fetch('/api/banking/transactions', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) return;
        const rows = await response.json();

        const body = document.getElementById('history-body');
        body.replaceChildren();

        document.getElementById('no-history').style.display = rows.length ? 'none' : 'block';
        document.getElementById('history').style.display = rows.length ? '' : 'none';

        for (const tx of rows) {
            const tr = document.createElement('tr');
            const sign = tx.type === 'deposit' ? '+' : '-';
            const cells = [
                tx.created_at,
                tx.type.charAt(0).toUpperCase() + tx.type.slice(1),
                `${sign}$${tx.amount}`,
                `$${tx.balance_after}`,
            ];
            for (const text of cells) {
                const td = document.createElement('td');
                td.textContent = text;
                tr.appendChild(td);
            }
            body.appendChild(tr);
        }
    } catch (err) {
      
    }
}

function accountDetail()
{
    fetchBalance();
    fetchHistory();
}

document.addEventListener('DOMContentLoaded', accountDetail);