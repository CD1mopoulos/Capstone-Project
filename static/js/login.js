document.addEventListener("DOMContentLoaded", async function () {
    console.log("✅ login.js is now loaded");

    // Handle Login Submit
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", handleLogin);
    }

    function handleLogin(event) {
        event.preventDefault();

        clearErrors();

        const data = {
            username: document.getElementById("loginUsername").value.trim(),
            password: document.getElementById("loginPassword").value.trim(),
            remember_me: document.getElementById("rememberMe").checked
        };

        console.log("🔍 Collected user data:", data);

        getUserLocation((locationData) => {
            if (locationData) {
                data.location = locationData;
            }
            sendLoginRequest(data);
        });
    }

    async function sendLoginRequest(data) {
        console.log("🔄 Sending login request with data:", data);

        const loginBtn = document.querySelector("#loginForm button[type='submit']");
        loginBtn.disabled = true;
        loginBtn.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            Logging in...
        `;

        try {
            const response = await fetch("/platform_db/login/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                console.log("✅ Login successful");

                const loginModal = document.getElementById("loginModal");
                if (loginModal) {
                    const modalInstance = bootstrap.Modal.getInstance(loginModal) || new bootstrap.Modal(loginModal);
                    modalInstance.hide();
                }

                const toastEl = document.getElementById("loginToast");
                if (toastEl) {
                    const toast = new bootstrap.Toast(toastEl);
                    toast.show();
                }

                setTimeout(() => {
                    if (result.redirect_url) {
                        window.location.href = result.redirect_url;
                    } else {
                        console.warn("⚠️ No redirect_url provided. Going to homepage.");
                        window.location.href = "/";
                    }
                }, 1200);

            } else {
                console.error("❌ Login failed:", result.error);
                showError("usernameError", "⚠️ Incorrect username or password.");
                showError("passwordError", "⚠️ Incorrect username or password.");
                resetLoginButton();
            }

        } catch (error) {
            console.error("❌ Error sending login request:", error);
            showError("usernameError", "❌ Something went wrong. Please try again.");
            resetLoginButton();
        }
    }

    function resetLoginButton() {
        const loginBtn = document.querySelector("#loginForm button[type='submit']");
        loginBtn.disabled = false;
        loginBtn.innerHTML = "Login";
    }

    function showError(elementId, message) {
        const errorElement = document.getElementById(elementId);
        if (errorElement) {
            errorElement.innerText = message;
        }
    }

    function clearErrors() {
        ["usernameError", "passwordError"].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.innerText = "";
        });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            document.cookie.split(';').forEach(cookie => {
                cookie = cookie.trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                }
            });
        }
        return cookieValue;
    }
});
