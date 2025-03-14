// Helper function to retrieve the CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Check if this cookie string begins with the name we want.
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() {
    // --- Profile Picture Preview ---
    const profilePictureInput = document.getElementById('profile-picture-upload');
    const profilePictureImage = document.getElementById('profile-picture');
    if (profilePictureInput && profilePictureImage) {
        profilePictureInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    profilePictureImage.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // --- Global Reset & Cancel Buttons ---
    // For Account Details
    const cancelAccountBtn = document.getElementById('cancel-account-changes-btn');
    const resetAccountBtn = document.getElementById('reset-account-changes-btn');
    if (cancelAccountBtn) {
        cancelAccountBtn.addEventListener('click', function() { location.reload(); });
    }
    if (resetAccountBtn) {
        resetAccountBtn.addEventListener('click', function() { location.reload(); });
    }
    // For News Feed Preferences
    const cancelPreferencesBtn = document.getElementById('cancel-preferences-btn');
    const resetPreferencesBtn = document.getElementById('reset-preferences-btn');
    if (cancelPreferencesBtn) {
        cancelPreferencesBtn.addEventListener('click', function() { location.reload(); });
    }
    if (resetPreferencesBtn) {
        resetPreferencesBtn.addEventListener('click', function() { location.reload(); });
    }

    // --- AJAX Handlers for "Edit Account Details" Mini-Forms ---

    // Username Update Handler (with navbar update)
    const usernameForm = document.getElementById('update-username-form');
    if (usernameForm) {
        usernameForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(usernameForm);
            fetch(usernameForm.action, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                const feedback = document.getElementById('username-feedback');
                if (data.success) {
                    feedback.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
                    const navbarUsername = document.getElementById('navbar-username');
                    if (navbarUsername && data.new_username) {
                        navbarUsername.textContent = data.new_username;
                    }
                } else {
                    feedback.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('username-feedback').innerHTML = `<div class="alert alert-danger">An error occurred. Please try again.</div>`;
            });
        });
    }
    // Discard Button for Username
    const discardUsernameBtn = document.querySelector('.discard-username-btn');
    if (discardUsernameBtn) {
        discardUsernameBtn.addEventListener('click', function() {
            const usernameField = document.getElementById('username_field');
            usernameField.value = usernameField.getAttribute('data-original-value');
            const feedback = document.getElementById('username-feedback');
            if (feedback) { feedback.innerHTML = ''; }
        });
    }

    // Email Update Handler
    const emailForm = document.getElementById('update-email-form');
    if (emailForm) {
        emailForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(emailForm);
            fetch(emailForm.action, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                const feedback = document.getElementById('email-feedback');
                if (data.success) {
                    feedback.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
                } else {
                    feedback.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('email-feedback').innerHTML = `<div class="alert alert-danger">An error occurred. Please try again.</div>`;
            });
        });
    }
    // Discard Button for Email
    const discardEmailBtn = document.querySelector('.discard-email-btn');
    if (discardEmailBtn) {
        discardEmailBtn.addEventListener('click', function() {
            const emailField = document.getElementById('email_field');
            emailField.value = emailField.getAttribute('data-original-value');
            const feedback = document.getElementById('email-feedback');
            if (feedback) { feedback.innerHTML = ''; }
        });
    }

    // Password Update Handler
    const passwordForm = document.getElementById('update-password-form');
    if (passwordForm) {
        passwordForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(passwordForm);
            fetch(passwordForm.action, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                const feedback = document.getElementById('password-feedback');
                if (data.success) {
                    feedback.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
                    passwordForm.reset();
                } else {
                    feedback.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('password-feedback').innerHTML = `<div class="alert alert-danger">An error occurred. Please try again.</div>`;
            });
        });
    }
    // Discard Button for Password Fields
    const discardPasswordBtn = document.querySelector('.discard-password-btn');
    if (discardPasswordBtn) {
        discardPasswordBtn.addEventListener('click', function() {
            document.getElementById('current_password_field').value = '';
            document.getElementById('new_password_field').value = '';
            document.getElementById('confirm_new_password_field').value = '';
            const feedback = document.getElementById('password-feedback');
            if (feedback) { feedback.innerHTML = ''; }
        });
    }

    // --- AJAX Handler for News Feed Preferences ---
    const preferencesForm = document.getElementById('news-feed-preferences-form');
    if (preferencesForm) {
        preferencesForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(preferencesForm);
            fetch(preferencesForm.action, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                const feedback = document.getElementById('preferences-feedback');
                if (data.success) {
                    feedback.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
                } else {
                    feedback.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('preferences-feedback').innerHTML = `<div class="alert alert-danger">An error occurred. Please try again.</div>`;
            });
        });
    }
});
