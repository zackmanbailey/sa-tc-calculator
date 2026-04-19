REGISTER_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TitanForge - Request Access</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #0F172A 0%, #1a2744 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #e5e7eb;
        }
        .register-container { width: 100%; max-width: 480px; padding: 20px; }
        .register-card {
            background: rgba(30, 41, 59, 0.95);
            border: 1px solid #1E40AF;
            border-radius: 8px;
            padding: 36px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }
        .logo-section { text-align: center; margin-bottom: 24px; }
        .logo { font-size: 24px; font-weight: 900; letter-spacing: 2px; color: #F59E0B; text-transform: uppercase; }
        .tagline { font-size: 12px; color: #9ca3af; letter-spacing: 1px; text-transform: uppercase; margin-top: 4px; }
        .subtitle { font-size: 14px; color: #94a3b8; text-align: center; margin-bottom: 24px; line-height: 1.5; }
        .form-group { margin-bottom: 16px; }
        .form-group label {
            display: block; font-size: 12px; font-weight: 600; color: #d1d5db;
            margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px;
        }
        .form-group label .required { color: #ef4444; }
        .form-group input, .form-group textarea {
            width: 100%; padding: 10px 12px;
            border: 1px solid #374151; border-radius: 6px;
            background: rgba(15, 23, 42, 0.8); color: #f3f4f6;
            font-size: 14px; font-family: inherit; transition: all 0.3s ease;
        }
        .form-group input:focus, .form-group textarea:focus {
            outline: none; border-color: #1E40AF;
            background: rgba(15, 23, 42, 0.95);
            box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
        }
        .form-group input::placeholder, .form-group textarea::placeholder { color: #6b7280; }
        .form-group textarea { min-height: 60px; resize: vertical; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
        .pw-requirements {
            font-size: 11px; color: #6b7280; margin-top: 6px; line-height: 1.6;
        }
        .pw-requirements span { display: block; }
        .pw-requirements span.met { color: #22c55e; }
        .error-message, .success-message {
            display: none; padding: 12px 14px; border-radius: 6px;
            font-size: 13px; margin-bottom: 16px;
        }
        .error-message { background: rgba(220,38,38,0.15); color: #fca5a5; border: 1px solid #dc2626; }
        .error-message.show, .success-message.show { display: block; }
        .success-message { background: rgba(34,197,94,0.15); color: #86efac; border: 1px solid #22c55e; }
        .submit-btn {
            width: 100%; padding: 12px; background: #1E40AF; color: white;
            border: none; border-radius: 6px; font-size: 15px; font-weight: 600;
            cursor: pointer; transition: all 0.3s ease; text-transform: uppercase;
            letter-spacing: 0.5px; margin-top: 8px;
        }
        .submit-btn:hover { background: #1e3a8a; box-shadow: 0 4px 12px rgba(30,64,175,0.3); }
        .submit-btn:disabled { background: #4b5563; cursor: not-allowed; opacity: 0.6; }
        .footer-links {
            text-align: center; margin-top: 20px; padding-top: 16px;
            border-top: 1px solid #1f2937;
        }
        .footer-links a {
            color: #60a5fa; text-decoration: none; font-size: 13px;
            transition: color 0.2s;
        }
        .footer-links a:hover { color: #93bbfd; }
        @media (max-width: 500px) { .form-row { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="register-container">
        <div class="register-card">
            <div class="logo-section">
                <div class="logo">TITANFORGE</div>
                <div class="tagline">Steel Fabrication Management</div>
            </div>
            <div class="subtitle">
                Request access to the system. An administrator will review and approve your account.
            </div>

            <div class="error-message" id="errorMsg"></div>
            <div class="success-message" id="successMsg"></div>

            <form id="registerForm">
                <div class="form-row">
                    <div class="form-group">
                        <label>Username <span class="required">*</span></label>
                        <input type="text" id="regUsername" placeholder="e.g. jsmith" required autocomplete="username" maxlength="50">
                    </div>
                    <div class="form-group">
                        <label>Full Name <span class="required">*</span></label>
                        <input type="text" id="regDisplayName" placeholder="e.g. John Smith" required maxlength="100">
                    </div>
                </div>

                <div class="form-group">
                    <label>Email</label>
                    <input type="email" id="regEmail" placeholder="you@company.com" maxlength="254">
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label>Phone Number</label>
                        <input type="tel" id="regPhone" placeholder="(555) 123-4567" maxlength="20">
                    </div>
                    <div class="form-group">
                        <label>Your Role at the Company</label>
                        <input type="text" id="regCompanyRole" placeholder="e.g. Shop Foreman" maxlength="100">
                    </div>
                </div>

                <div class="form-group">
                    <label>Address</label>
                    <textarea id="regAddress" placeholder="Street address, city, state, zip" maxlength="300"></textarea>
                </div>

                <div class="form-group">
                    <label>Password <span class="required">*</span></label>
                    <input type="password" id="regPassword" placeholder="Create a password" required autocomplete="new-password">
                    <div class="pw-requirements" id="pwReqs">
                        <span id="pwLen">Min 8 characters</span>
                        <span id="pwUpper">At least one uppercase letter</span>
                        <span id="pwLower">At least one lowercase letter</span>
                        <span id="pwNum">At least one number</span>
                    </div>
                </div>

                <div class="form-group">
                    <label>Confirm Password <span class="required">*</span></label>
                    <input type="password" id="regPasswordConfirm" placeholder="Re-enter password" required autocomplete="new-password">
                </div>

                <button type="submit" class="submit-btn" id="submitBtn">Request Access</button>
            </form>

            <div class="footer-links">
                <a href="/auth/login">Already have an account? Sign in</a>
            </div>
        </div>
    </div>

    <script>
        const form = document.getElementById('registerForm');
        const pw = document.getElementById('regPassword');
        const pwConfirm = document.getElementById('regPasswordConfirm');

        // Live password strength feedback
        pw.addEventListener('input', function() {
            const v = pw.value;
            document.getElementById('pwLen').className = v.length >= 8 ? 'met' : '';
            document.getElementById('pwUpper').className = /[A-Z]/.test(v) ? 'met' : '';
            document.getElementById('pwLower').className = /[a-z]/.test(v) ? 'met' : '';
            document.getElementById('pwNum').className = /[0-9]/.test(v) ? 'met' : '';
        });

        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const errorDiv = document.getElementById('errorMsg');
            const successDiv = document.getElementById('successMsg');
            errorDiv.classList.remove('show');
            successDiv.classList.remove('show');

            const password = pw.value;
            if (password !== pwConfirm.value) {
                errorDiv.textContent = 'Passwords do not match.';
                errorDiv.classList.add('show');
                return;
            }

            const btn = document.getElementById('submitBtn');
            btn.disabled = true;
            btn.textContent = 'Submitting...';

            fetch('/auth/register/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: document.getElementById('regUsername').value.trim(),
                    display_name: document.getElementById('regDisplayName').value.trim(),
                    email: document.getElementById('regEmail').value.trim(),
                    phone: document.getElementById('regPhone').value.trim(),
                    address: document.getElementById('regAddress').value.trim(),
                    company_role: document.getElementById('regCompanyRole').value.trim(),
                    password: password,
                })
            })
            .then(r => r.json())
            .then(data => {
                if (data.ok) {
                    successDiv.textContent = data.message;
                    successDiv.classList.add('show');
                    form.reset();
                    document.querySelectorAll('.pw-requirements span').forEach(s => s.className = '');
                } else {
                    errorDiv.textContent = data.error || 'Registration failed.';
                    errorDiv.classList.add('show');
                }
            })
            .catch(err => {
                errorDiv.textContent = 'Network error. Please try again.';
                errorDiv.classList.add('show');
            })
            .finally(() => {
                btn.disabled = false;
                btn.textContent = 'Request Access';
            });
        });
    </script>
</body>
</html>
"""
