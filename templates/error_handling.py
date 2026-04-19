"""
TitanForge — Friendly Error Handling System
=============================================
Replaces raw stack traces and alert() boxes with user-friendly inline error banners.
Include ERROR_CSS + ERROR_JS in any page to upgrade error handling.

Server-side: use friendly_error() to wrap handler exceptions.
Client-side: call tfError(msg, detail) instead of alert().
"""


# ─────────────────────────────────────────────
# ERROR MESSAGE MAPPING
# ─────────────────────────────────────────────
# Maps common error patterns to friendly messages

ERROR_MAP = {
    "KeyError": {
        "friendly": "A required field is missing from the form.",
        "hint": "Check that all fields are filled in and try again."
    },
    "ValueError": {
        "friendly": "One of the values you entered isn't in the right format.",
        "hint": "Check for typos in number fields — make sure you didn't include letters or special characters."
    },
    "ZeroDivisionError": {
        "friendly": "The calculation hit a divide-by-zero error.",
        "hint": "Check that bay spacing, column count, and other dimensions are greater than zero."
    },
    "FileNotFoundError": {
        "friendly": "The project or file couldn't be found.",
        "hint": "It may have been moved, renamed, or deleted. Try going back to the project list."
    },
    "PermissionError": {
        "friendly": "You don't have permission to do this.",
        "hint": "This action requires a higher access level. Ask your admin to update your role."
    },
    "json.decoder.JSONDecodeError": {
        "friendly": "The data couldn't be read — it may be corrupted.",
        "hint": "Try refreshing the page. If the problem continues, the project file may need to be restored from backup."
    },
    "ConnectionError": {
        "friendly": "Couldn't connect to the server.",
        "hint": "Check your network connection and try again."
    },
    "Timeout": {
        "friendly": "The request took too long.",
        "hint": "The server might be busy with a large calculation. Wait a moment and try again."
    },
    "Not authenticated": {
        "friendly": "You need to log in first.",
        "hint": "Your session may have expired. Please log in again."
    },
    "Insufficient permissions": {
        "friendly": "Your account doesn't have access to this feature.",
        "hint": "This requires Admin, Estimator, or Shop Floor access. Contact your supervisor if you need access."
    },
}


def friendly_error(exception: Exception, context: str = "") -> dict:
    """
    Convert a Python exception into a user-friendly error response.
    Returns dict with: ok, error (friendly), hint, detail (for admins), context.
    """
    error_type = type(exception).__name__
    error_str = str(exception)

    # Try to match by type first, then by string content
    match = ERROR_MAP.get(error_type)
    if not match:
        for key, val in ERROR_MAP.items():
            if key.lower() in error_str.lower():
                match = val
                break

    if match:
        friendly = match["friendly"]
        hint = match["hint"]
    else:
        friendly = "Something went wrong while processing your request."
        hint = "Try refreshing the page. If this keeps happening, let your admin know."

    return {
        "ok": False,
        "error": friendly,
        "hint": hint,
        "error_code": error_type,
        "detail": error_str,  # Only show to admins
        "context": context,
    }


# ─────────────────────────────────────────────
# CSS for inline error banners
# ─────────────────────────────────────────────

ERROR_CSS = """
/* ── TitanForge Error Banner System ── */
.tf-error-banner {
  display: none; position: fixed; top: 16px; left: 50%;
  transform: translateX(-50%); z-index: 99990;
  max-width: 520px; width: calc(100% - 32px);
  background: #1E293B; border: 1px solid #DC2626;
  border-radius: 12px; padding: 16px 20px;
  box-shadow: 0 8px 30px rgba(220,38,38,0.2);
  animation: tfErrIn 0.3s ease;
  font-size: 14px; color: #FEE2E2;
}
.tf-error-banner.visible { display: block; }
.tf-error-banner.warning { border-color: #F59E0B; }
.tf-error-banner.warning .tfeb-icon { color: #F59E0B; }
.tf-error-banner.info { border-color: #3B82F6; }
.tf-error-banner.info .tfeb-icon { color: #3B82F6; }
@keyframes tfErrIn { from { opacity:0; transform:translateX(-50%) translateY(-12px); }
  to { opacity:1; transform:translateX(-50%) translateY(0); } }

.tfeb-row { display: flex; gap: 12px; align-items: flex-start; }
.tfeb-icon { font-size: 20px; color: #DC2626; flex-shrink: 0; margin-top: 2px; }
.tfeb-content { flex: 1; }
.tfeb-msg { font-weight: 600; color: #FFF; margin-bottom: 4px; font-size: 14px; }
.tfeb-hint { color: #94A3B8; font-size: 13px; line-height: 1.5; }
.tfeb-detail {
  display: none; margin-top: 8px; padding: 8px 10px;
  background: #0F172A; border-radius: 6px;
  font-family: monospace; font-size: 11px; color: #64748B;
  max-height: 120px; overflow-y: auto; word-break: break-all;
}
.tfeb-detail.visible { display: block; }
.tfeb-actions { display: flex; gap: 8px; margin-top: 10px; }
.tfeb-btn {
  padding: 6px 14px; border-radius: 6px; border: none;
  font-size: 12px; font-weight: 600; cursor: pointer;
  transition: all 0.2s;
}
.tfeb-btn.retry { background: #1E40AF; color: #FFF; }
.tfeb-btn.retry:hover { background: #2563EB; }
.tfeb-btn.dismiss { background: #334155; color: #94A3B8; }
.tfeb-btn.dismiss:hover { background: #475569; color: #FFF; }
.tfeb-btn.details { background: transparent; color: #64748B; border: 1px solid #334155; }
.tfeb-btn.details:hover { color: #94A3B8; border-color: #94A3B8; }
.tfeb-close {
  position: absolute; top: 10px; right: 12px;
  background: none; border: none; color: #94A3B8; font-size: 18px;
  cursor: pointer; padding: 0 4px;
}
.tfeb-close:hover { color: #94A3B8; }

/* Success toast */
.tf-success-toast {
  display: none; position: fixed; bottom: 20px; left: 50%;
  transform: translateX(-50%); z-index: 99990;
  padding: 12px 24px; background: #166534; border: 1px solid #22C55E;
  border-radius: 10px; color: #BBF7D0; font-size: 14px; font-weight: 600;
  box-shadow: 0 4px 20px rgba(22,101,52,0.3);
  animation: tfErrIn 0.3s ease;
}
.tf-success-toast.visible { display: block; }
"""


# ─────────────────────────────────────────────
# JS for error handling (replaces alert())
# ─────────────────────────────────────────────

ERROR_JS = r"""
<script>
(function() {
  // ── Create error banner ──
  var banner = document.createElement('div');
  banner.className = 'tf-error-banner';
  banner.innerHTML = '<button class="tfeb-close" onclick="tfDismissError()">&times;</button>'
    + '<div class="tfeb-row">'
    + '  <div class="tfeb-icon">&#x26A0;&#xFE0F;</div>'
    + '  <div class="tfeb-content">'
    + '    <div class="tfeb-msg" id="tfErrMsg"></div>'
    + '    <div class="tfeb-hint" id="tfErrHint"></div>'
    + '    <div class="tfeb-detail" id="tfErrDetail"></div>'
    + '    <div class="tfeb-actions">'
    + '      <button class="tfeb-btn retry" id="tfErrRetry" onclick="tfRetryLast()" style="display:none">Try Again</button>'
    + '      <button class="tfeb-btn details" onclick="document.getElementById(\\\'tfErrDetail\\\').classList.toggle(\\\'visible\\\')" style="display:none" id="tfErrDetailsBtn">Technical Details</button>'
    + '      <button class="tfeb-btn dismiss" onclick="tfDismissError()">Dismiss</button>'
    + '    </div>'
    + '  </div>'
    + '</div>';
  document.body.appendChild(banner);

  // ── Success toast ──
  var successToast = document.createElement('div');
  successToast.className = 'tf-success-toast';
  successToast.id = 'tfSuccessToast';
  document.body.appendChild(successToast);

  var autoHideTimer = null;
  var lastRetryFn = null;

  // ── Error display function (replaces alert()) ──
  window.tfError = function(msg, hint, detail, retryFn) {
    document.getElementById('tfErrMsg').textContent = msg || 'Something went wrong.';
    document.getElementById('tfErrHint').textContent = hint || 'Try refreshing the page.';

    var detailEl = document.getElementById('tfErrDetail');
    var detailBtn = document.getElementById('tfErrDetailsBtn');
    if (detail) {
      detailEl.textContent = detail;
      detailBtn.style.display = '';
    } else {
      detailEl.textContent = '';
      detailBtn.style.display = 'none';
    }
    detailEl.classList.remove('visible');

    var retryBtn = document.getElementById('tfErrRetry');
    if (retryFn) {
      lastRetryFn = retryFn;
      retryBtn.style.display = '';
    } else {
      lastRetryFn = null;
      retryBtn.style.display = 'none';
    }

    banner.classList.add('visible');
    if (autoHideTimer) clearTimeout(autoHideTimer);
    autoHideTimer = setTimeout(function() { banner.classList.remove('visible'); }, 15000);
  };

  window.tfDismissError = function() {
    banner.classList.remove('visible');
    if (autoHideTimer) clearTimeout(autoHideTimer);
  };

  window.tfRetryLast = function() {
    tfDismissError();
    if (lastRetryFn) lastRetryFn();
  };

  // ── Success toast ──
  window.tfSuccess = function(msg) {
    var toast = document.getElementById('tfSuccessToast');
    toast.textContent = msg;
    toast.classList.add('visible');
    setTimeout(function() { toast.classList.remove('visible'); }, 3000);
  };

  // ── Smart fetch wrapper ──
  window.tfFetch = function(url, options) {
    options = options || {};
    return fetch(url, options)
      .then(function(resp) {
        if (!resp.ok) {
          return resp.json().then(function(data) {
            tfError(
              data.error || 'Request failed (HTTP ' + resp.status + ')',
              data.hint || 'Check the URL and try again.',
              data.detail || null,
              function() { tfFetch(url, options); }
            );
            return Promise.reject(data);
          }).catch(function() {
            tfError('Server returned an error (HTTP ' + resp.status + ')',
              'The server might be down or overloaded. Try again in a moment.',
              null,
              function() { tfFetch(url, options); }
            );
            return Promise.reject(new Error('HTTP ' + resp.status));
          });
        }
        return resp.json();
      })
      .then(function(data) {
        if (data && data.ok === false) {
          tfError(
            data.error || 'The operation did not complete successfully.',
            data.hint || 'Check your input and try again.',
            data.detail || null
          );
          return Promise.reject(data);
        }
        return data;
      })
      .catch(function(err) {
        if (err && err.ok === false) return Promise.reject(err);
        if (err instanceof TypeError && err.message.indexOf('fetch') >= 0) {
          tfError('Cannot reach the server.',
            'Check your network connection. The server may be restarting.',
            err.message,
            function() { tfFetch(url, options); }
          );
        }
        return Promise.reject(err);
      });
  };

  // ── Override window.alert to use friendly errors ──
  var _origAlert = window.alert;
  window.alert = function(msg) {
    if (typeof msg === 'string' && (msg.toLowerCase().indexOf('error') >= 0 || msg.toLowerCase().indexOf('failed') >= 0)) {
      tfError(msg);
    } else {
      // For non-error alerts, still show as a banner but in info style
      document.getElementById('tfErrMsg').textContent = msg;
      document.getElementById('tfErrHint').textContent = '';
      document.getElementById('tfErrDetail').textContent = '';
      document.getElementById('tfErrDetailsBtn').style.display = 'none';
      document.getElementById('tfErrRetry').style.display = 'none';
      banner.className = 'tf-error-banner info visible';
      if (autoHideTimer) clearTimeout(autoHideTimer);
      autoHideTimer = setTimeout(function() { banner.classList.remove('visible'); banner.className = 'tf-error-banner'; }, 8000);
    }
  };

})();
</script>
"""


def get_error_bundle() -> str:
    """Returns the complete CSS + JS for error handling."""
    return f"<style>{ERROR_CSS}</style>\n{ERROR_JS}"
