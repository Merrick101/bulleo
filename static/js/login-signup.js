document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ login-signup.js loaded");

    // Ensure modals exist before initializing them
    const loginModalEl = document.getElementById("login-modal");
    const signupModalEl = document.getElementById("signup-modal");
    const logoutModalEl = document.getElementById("logout-modal");

    let loginModal, signupModal, logoutModal;

    if (loginModalEl) {
        loginModal = new bootstrap.Modal(loginModalEl);
    }
    if (signupModalEl) {
        signupModal = new bootstrap.Modal(signupModalEl);
    }
    if (logoutModalEl) {
        logoutModal = new bootstrap.Modal(logoutModalEl);
    }

    // Selecting modal toggle buttons
    const loginBtn = document.getElementById("open-login-modal");
    const signupBtn = document.getElementById("open-signup-modal");
    const logoutBtn = document.getElementById("logout-btn");

    const switchToSignup = document.getElementById("switch-to-signup");
    const switchToLogin = document.getElementById("switch-to-login");

    // Open login modal
    if (loginBtn && loginModal) {
        loginBtn.addEventListener("click", function () {
            loginModal.show();
        });
    }

    // Open signup modal
    if (signupBtn && signupModal) {
        signupBtn.addEventListener("click", function () {
            signupModal.show();
        });
    }

    // Open logout confirmation modal
    if (logoutBtn && logoutModal) {
        logoutBtn.addEventListener("click", function () {
            logoutModal.show();
        });
    }

    // Switch from login to signup modal
    if (switchToSignup && loginModal && signupModal) {
        switchToSignup.addEventListener("click", function (event) {
            event.preventDefault();
            loginModal.hide();
            signupModal.show();
        });
    }

    // Switch from signup to login modal
    if (switchToLogin && loginModal && signupModal) {
        switchToLogin.addEventListener("click", function (event) {
            event.preventDefault();
            signupModal.hide();
            loginModal.show();
        });
    }

    // Handle login form submission
    const loginForm = document.querySelector("#login-modal form");
    if (loginForm) {
        loginForm.addEventListener("submit", function () {
            setTimeout(() => {
                window.location.reload();
            }, 1000); // Short delay to allow session update
        });
    }

    // Handle signup form submission
    const signupForm = document.querySelector("#signup-modal form");
    if (signupForm) {
        signupForm.addEventListener("submit", function () {
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        });
    }

    // Handle logout action to refresh page
    const logoutLink = document.querySelector(".dropdown-item.text-danger"); // Logout link in dropdown
    if (logoutLink) {
        logoutLink.addEventListener("click", function () {
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        });
    }
});
