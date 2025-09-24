const loginForm = document.getElementById('login-form');

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const res = await fetch('http://localhost:3000/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await res.json();

        if (data.success) {
            // Save username in sessionStorage for logout
            sessionStorage.setItem('username', data.username);
            window.location.href = '/home';
        } else {
            alert(data.message || 'Login failed');
        }
    } catch (err) {
        alert('Error connecting to server');
    }
});
