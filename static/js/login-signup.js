document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ login-signup.js loaded");

    // Selecting modal elements
    const loginModal = new bootstrap.Modal(document.getElementById("login-modal"));
    const signupModal = new bootstrap.Modal(document.getElementById("signup-modal"));
    const logoutModal = new bootstrap.Modal(document.getElementById("logout-modal"));

    // Selecting modal toggle buttons
    const loginBtn = document.getElementById("open-login-modal");
    const signupBtn = document.getElementById("open-signup-modal");
    const logoutBtn = document.getElementById("logout-btn");

    const googleLoginButton = document.getElementById("google-login-btn");
    const googleSignupButton = document.getElementById("google-signup-btn");

    // Switching between login and signup modals
    const switchToSignup = document.getElementById("switch-to-signup");
    const switchToLogin = document.getElementById("switch-to-login");

    // Open login modal
    if (loginBtn) {
        loginBtn.addEventListener("click", function () {
            loginModal.show();
        });
    }

    // Open signup modal
    if (signupBtn) {
        signupBtn.addEventListener("click", function () {
            signupModal.show();
        });
    }

    // Open logout confirmation modal
    if (logoutBtn) {
        logoutBtn.addEventListener("click", function () {
            logoutModal.show();
        });
    }

    // Switch from login to signup modal
    if (switchToSignup) {
        switchToSignup.addEventListener("click", function (event) {
            event.preventDefault();
            loginModal.hide();
            signupModal.show();
        });
    }

    // Switch from signup to login modal
    if (switchToLogin) {
        switchToLogin.addEventListener("click", function (event) {
            event.preventDefault();
            signupModal.hide();
            loginModal.show();
        });
    }

    // Handle OAuth popup
    function handleGoogleAuth(button, url) {
        if (!button) return;

        button.addEventListener("click", function (event) {
            event.preventDefault();
            console.log("🔵 Google login/signup button clicked");

            window.oauthWindow = window.open(
                url,
                "oauthWindow",
                "width=500,height=600,top=200,left=500"
            );

            if (!window.oauthWindow) {
                console.error("🚨 Failed to open OAuth window. Check popup blocker settings.");
                return;
            }

            console.log("✅ OAuth popup opened successfully.");

            let checkPopupClosed = setInterval(function () {
                if (window.oauthWindow.closed) {
                    console.log("🔴 Popup closed. Checking login status...");
                    clearInterval(checkPopupClosed);
                    checkLoginStatus();
                }
            }, 1000);
        });
    }

    handleGoogleAuth(googleLoginButton, "/accounts/google/login/");
    handleGoogleAuth(googleSignupButton, "/accounts/google/login/");

    // OAuth Callback Listener
    window.addEventListener("message", function (event) {
        console.log("📩 Received message from OAuth popup:", event.data);

        if (event.origin !== window.location.origin) {
            console.warn("⚠️ Ignored message from untrusted origin:", event.origin);
            return;
        }

        if (event.data === "google-login-success") {
            console.log("✅ OAuth login successful! Closing popup and reloading main page...");
            
            // Close the OAuth popup window if it's still open
            if (window.oauthWindow && !window.oauthWindow.closed) {
                window.oauthWindow.close();
                console.log("✅ OAuth popup closed from main window.");
            }

            // Reload main page after a brief delay
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        }
    });

    // Check for localStorage fallback (if postMessage fails)
    if (localStorage.getItem("googleLoginSuccess") === "true") {
        console.log("✅ OAuth login detected via localStorage. Reloading...");
        localStorage.removeItem("googleLoginSuccess");
        window.location.reload();
    }

    // Function to check login status
    function checkLoginStatus(retryCount = 3) {
        fetch("/users/check-login-status/")
            .then(response => response.json())
            .then(data => {
                if (data.is_authenticated) {
                    console.log("✅ User is authenticated. Closing popup & reloading...");
                    
                    // Attempt to close popup from the main window
                    if (window.oauthWindow && !window.oauthWindow.closed) {
                        window.oauthWindow.close();
                        console.log("✅ OAuth popup closed from checkLoginStatus.");
                    }

                    window.location.reload();
                } else if (retryCount > 0) {
                    console.log(`⏳ User is not authenticated after OAuth process. Retrying... (${retryCount} attempts left)`);
                    setTimeout(() => checkLoginStatus(retryCount - 1), 2000);
                } else {
                    console.log("❌ User is not authenticated after multiple attempts.");
                }
            })
            .catch(error => console.error("❌ Error checking login status:", error));
    }
});
