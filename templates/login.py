LOGIN_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TitanForge - Sign In</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #0F172A 0%, #1a2744 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #e5e7eb;
        }

        .login-container {
            width: 100%;
            max-width: 400px;
            padding: 20px;
        }

        .login-card {
            background: rgba(30, 41, 59, 0.95);
            border: 1px solid #1E40AF;
            border-radius: 8px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(10px);
        }

        .logo-section {
            text-align: center;
            margin-bottom: 30px;
        }

        .logo {
            font-size: 24px;
            font-weight: 900;
            letter-spacing: 2px;
            color: #F59E0B;
            margin-bottom: 8px;
            text-transform: uppercase;
        }

        .tagline {
            font-size: 12px;
            color: #9ca3af;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            font-size: 14px;
            font-weight: 500;
            color: #d1d5db;
            margin-bottom: 8px;
        }

        .form-group input {
            width: 100%;
            padding: 12px 14px;
            border: 1px solid #374151;
            border-radius: 6px;
            background: rgba(15, 23, 42, 0.8);
            color: #f3f4f6;
            font-size: 14px;
            transition: all 0.3s ease;
        }

        .form-group input:focus {
            outline: none;
            border-color: #1E40AF;
            background: rgba(15, 23, 42, 0.95);
            box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
        }

        .form-group input::placeholder {
            color: #6b7280;
        }

        .error-message {
            display: none;
            background: #dc2626;
            color: #fee2e2;
            padding: 12px 14px;
            border-radius: 6px;
            font-size: 13px;
            margin-bottom: 20px;
            border-left: 4px solid #991b1b;
        }

        .error-message.show {
            display: block;
        }

        .sign-in-btn {
            width: 100%;
            padding: 12px;
            background: #1E40AF;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .sign-in-btn:hover {
            background: #1e3a8a;
            box-shadow: 0 4px 12px rgba(30, 64, 175, 0.3);
        }

        .sign-in-btn:active {
            background: #1e3a8a;
            transform: scale(0.98);
        }

        .sign-in-btn:disabled {
            background: #4b5563;
            cursor: not-allowed;
            opacity: 0.6;
        }

        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #1f2937;
            font-size: 11px;
            color: #6b7280;
            letter-spacing: 0.5px;
        }

        .footer span {
            margin: 0 8px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-card">
            <div class="logo-section">
                <div class="logo">TITANFORGE</div>
                <div class="tagline">Steel Fabrication Management</div>
            </div>

            <div class="error-message" id="errorMessage"></div>

            <form id="loginForm">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input
                        type="text"
                        id="username"
                        name="username"
                        placeholder="Enter your username"
                        required
                        autocomplete="username"
                    >
                </div>

                <div class="form-group">
                    <label for="password">Password</label>
                    <input
                        type="password"
                        id="password"
                        name="password"
                        placeholder="Enter your password"
                        required
                        autocomplete="current-password"
                    >
                </div>

                <button type="submit" class="sign-in-btn" id="signInBtn">Sign In</button>
            </form>

            <div class="footer">
                <span>Internal use only</span>
                <span>·</span>
                <span>v3.0</span>
            </div>
        </div>
    </div>

    <script>
        const loginForm = document.getElementById('loginForm');
        const signInBtn = document.getElementById('signInBtn');
        const errorMessage = document.getElementById('errorMessage');
        const usernameInput = document.getElementById('username');
        const passwordInput = document.getElementById('password');

        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            doLogin();
        });

        function doLogin() {
            const username = usernameInput.value.trim();
            const password = passwordInput.value;

            if (!username || !password) {
                showError('Please enter both username and password.');
                return;
            }

            signInBtn.disabled = true;
            signInBtn.textContent = 'Signing In...';

            fetch('/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.error || 'Login failed');
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.redirect) {
                    window.location.href = data.redirect;
                } else {
                    window.location.href = '/';
                }
            })
            .catch(error => {
                showError(error.message || 'Login failed. Please try again.');
                signInBtn.disabled = false;
                signInBtn.textContent = 'Sign In';
                passwordInput.value = '';
            });
        }

        function showError(message) {
            errorMessage.textContent = message;
            errorMessage.classList.add('show');
        }

        function clearError() {
            errorMessage.textContent = '';
            errorMessage.classList.remove('show');
        }

        usernameInput.addEventListener('focus', clearError);
        passwordInput.addEventListener('focus', clearError);
    </script>
</body>
</html>
"""
