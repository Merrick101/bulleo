document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ login-signup.js loaded");

    // Initialize modals if they exist
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

    // Modal toggle buttons
    const loginBtn = document.getElementById("open-login-modal");
    const signupBtn = document.getElementById("open-signup-modal");
    const logoutBtn = document.getElementById("logout-btn");
    const switchToSignup = document.getElementById("switch-to-signup");
    const switchToLogin = document.getElementById("switch-to-login");

    if (loginBtn && loginModal) {
        loginBtn.addEventListener("click", function () {
            loginModal.show();
        });
    }
    if (signupBtn && signupModal) {
        signupBtn.addEventListener("click", function () {
            signupModal.show();
        });
    }
    if (logoutBtn && logoutModal) {
        logoutBtn.addEventListener("click", function () {
            logoutModal.show();
        });
    }
    if (switchToSignup && loginModal && signupModal) {
        switchToSignup.addEventListener("click", function (event) {
            event.preventDefault();
            loginModal.hide();
            setTimeout(() => signupModal.show(), 400);
        });
    }
    if (switchToLogin && loginModal && signupModal) {
        switchToLogin.addEventListener("click", function (event) {
            event.preventDefault();
            signupModal.hide();
            setTimeout(() => loginModal.show(), 400);
        });
    }

    // Function to get CSRF token from the form
    function getCSRFToken() {
        const csrfInput = document.querySelector("[name=csrfmiddlewaretoken]");
        if (csrfInput) {
            return csrfInput.value;
        } else {
            console.error("⚠️ CSRF token not found!");
            return "";
        }
    }

    // Handle signup form submission using AJAX
    const signupForm = document.querySelector("#signup-modal form");
    if (signupForm) {
        signupForm.addEventListener("submit", function (event) {
            event.preventDefault();  // Prevent default form submission
            const formData = new FormData(signupForm);
            const csrfToken = getCSRFToken();
            if (!csrfToken) {
                alert("CSRF token missing! Please refresh the page.");
                return;
            }
            fetch(signupForm.action, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => { throw data; });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    window.location.href = data.redirect_url;
                }
            })
            .catch(errorData => {
                // Display errors within the modal
                let errorContainer = document.getElementById("signup-errors");
                if (!errorContainer) {
                    errorContainer = document.createElement("div");
                    errorContainer.id = "signup-errors";
                    signupForm.prepend(errorContainer);
                }
                errorContainer.innerHTML = ""; // Clear any previous errors
                for (const [field, errors] of Object.entries(errorData.errors)) {
                    errors.forEach(errObj => {
                        const p = document.createElement("p");
                        p.classList.add("text-danger");
                        p.textContent = `${field}: ${errObj.message}`;
                        errorContainer.appendChild(p);
                    });
                }
            });
        });
    }

    // Login form submission remains as before (non-AJAX)
    const loginForm = document.querySelector("#login-modal form");
    if (loginForm) {
        loginForm.addEventListener("submit", function () {
            // A delay to allow for session update; optionally, AJAX could be implemented here as well.
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        });
    }

    // Handle logout action to refresh the page
    const logoutLink = document.querySelector(".dropdown-item.text-danger");
    if (logoutLink) {
        logoutLink.addEventListener("click", function () {
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        });
    }
});
