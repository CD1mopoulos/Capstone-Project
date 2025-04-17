function handleOAuthLogin(provider, type) {
    let authUrl = "";

    if (provider === "google") {
        authUrl = window.googleLoginUrl;
        authUrl += (authUrl.includes('?') ? '&' : '?') + 'prompt=none';
    //} else if (provider === "facebook") {
        // ✅ Ensure `facebookLoginUrl` is available
    //    if (typeof window.facebookLoginUrl === "undefined" || !window.facebookLoginUrl) {
    //        console.error("❌ Facebook login URL not found in the document.");
    //        alert("⚠️ Facebook login is currently unavailable. Please refresh and try again.");
    //        return;
    //    }
    //    authUrl = window.facebookLoginUrl;
    }

    if (!authUrl) {
        console.error(`❌ ${provider} login URL is missing.`);
        alert(`⚠️ ${provider} login is unavailable. Try again.`);
        return;
    }

    console.log(`🔗 Redirecting to OAuth ${type}: ${authUrl}`);
    window.location.href = authUrl;
}

// ✅ Ensure DOM is fully loaded before attaching event listeners
document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ DOM fully loaded, attaching event listeners.");

    const googleButtons = document.querySelectorAll(".btn-google");
    //const facebookButtons = document.querySelectorAll(".btn-facebook");

    function attachLoginHandler(buttons, provider) {
        buttons.forEach(button => {
            button.addEventListener("click", function (event) {
                event.preventDefault();
                const type = button.closest("#loginModal") ? "login" : "signup";
                handleOAuthLogin(provider, type);
            });
        });
    }

    attachLoginHandler(googleButtons, "google");
    //attachLoginHandler(facebookButtons, "facebook");
});
