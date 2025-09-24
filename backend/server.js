const express = require('express');
const path = require('path');
const cors = require('cors');
const mysql = require('mysql2');

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// MySQL connection
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: '123456', // change to your MySQL password
    database: 'Stu'
});

db.connect(err => {
    if (err) console.error('Database connection failed:', err);
    else console.log('Connected to MySQL');
});

// Serve static files
app.use('/login', express.static(path.join(__dirname, '..', 'frontend', 'login')));
app.use('/home', express.static(path.join(__dirname, '..', 'frontend', 'home')));
app.use('/studentprofile', express.static(path.join(__dirname, '..', 'frontend', 'studentprofile')));
app.use('/doc', express.static(path.join(__dirname, '..', 'frontend', 'Document')));

// Login endpoint with 12-hour cooldown
app.post('/api/login', (req, res) => {
    const { username, password } = req.body;

    const sql = 'SELECT * FROM users WHERE username = ? AND password = ?';
    db.query(sql, [username, password], (err, results) => {
        if (err) return res.status(500).json({ success: false, error: err });

        if (results.length > 0) {
            const user = results[0];
            const now = Date.now();
            const cooldown = 12 * 60 * 60 * 1000; // 12 hours in ms

            if (user.lastLogout && now - user.lastLogout < cooldown) {
                const hoursLeft = Math.ceil((cooldown - (now - user.lastLogout)) / (1000 * 60 * 60));
                return res.status(403).json({ success: false, message: `You are logged out. Try again in ${hoursLeft} hour(s).` });
            }

            res.json({ success: true, username: user.username });
        } else {
            res.status(401).json({ success: false, message: 'Invalid credentials' });
        }
    });
});

// Logout endpoint
app.post('/api/logout', (req, res) => {
    const { username } = req.body;
    const now = Date.now();
    const sql = 'UPDATE users SET lastLogout = ? WHERE username = ?';

    db.query(sql, [now, username], (err, result) => {
        if (err) return res.status(500).json({ success: false, error: err });
        res.json({ success: true });
    });
});

// Redirect root to login
app.get('/', (req, res) => {
    res.redirect('/login');
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
