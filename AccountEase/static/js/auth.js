/* Password Toggle */
function togglePassword(inputId = "password", iconId = "eyeIcon") {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);

    if (!input || !icon) return;

    if (input.type === "password") {
        input.type = "text";
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
    } else {
        input.type = "password";
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
    }
}

/* Login Form specific submit (Spinner inside button) */
function handleLoginSubmit(form) {
    const btn = document.getElementById("loginBtn");
    const text = document.getElementById("btnText");
    const spinner = document.getElementById("spinner");

    if (btn) btn.disabled = true;
    if (text) text.textContent = "Logging in...";
    if (spinner) spinner.classList.remove("hidden");
}

/* Generic Submit (Disable button, change text, show loading div) */
function lockButton(btnId, loadingText = "Processing...", loadingDivId = "loading") {
    const btn = document.getElementById(btnId);
    const loadingDiv = document.getElementById(loadingDivId);

    if (btn) {
        btn.disabled = true;
        btn.innerText = loadingText;
    }
    if (loadingDiv) {
        loadingDiv.classList.remove("hidden");
    }
}
