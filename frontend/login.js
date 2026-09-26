document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const uname = document.getElementById('uname').value;
    const passwd = document.getElementById('passwd').value;

    try {
        // Send login information to Authentication endpoint
        const response = await fetch('http://localhost:8080/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ uname, passwd })
   
        });
        const data = await response.json();

        // Parse Response
        if (response.ok) {
            localStorage.setItem('authToken', data.token);
            alert('Login Successful!');
        } else {
            alert(`Login failed: ${data.message}`);
        }
    } catch (err) {
        console.error('Connection error:', err);
    }
});