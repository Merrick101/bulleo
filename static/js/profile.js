// Helper function to retrieve the CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener("DOMContentLoaded", function () {

    // --- Profile Picture Upload & Preview (AJAX) ---
    const profilePictureForm = document.getElementById("profile-picture-form");
    const profilePictureInput = document.getElementById("profile-picture-upload");
    const profilePicturePreview = document.getElementById("profile-picture-preview");
    const uploadStatus = document.getElementById("upload-status");

    if (profilePictureForm && profilePictureInput && profilePicturePreview) {
        profilePictureForm.addEventListener("submit", function (event) {
            event.preventDefault();

            const file = profilePictureInput.files[0];
            if (!file) {
                uploadStatus.innerHTML = '<div class="alert alert-warning">Please select an image.</div>';
                return;
            }

            const formData = new FormData();
            formData.append("profile_picture", file);
            formData.append("csrfmiddlewaretoken", getCookie("csrftoken"));

            // Show loading message
            uploadStatus.innerHTML = '<div class="alert alert-info">Uploading...</div>';

            fetch(profilePictureForm.action, {
                method: "POST",
                body: formData,
                headers: { "X-Requested-With": "XMLHttpRequest" }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    profilePicturePreview.src = data.image_url;
                    uploadStatus.innerHTML = '<div class="alert alert-success">Profile picture updated successfully!</div>';
                } else {
                    uploadStatus.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                }
            })
            .catch(error => {
                console.error("Upload error:", error);
                uploadStatus.innerHTML = '<div class="alert alert-danger">An error occurred. Please try again.</div>';
            });
        });

        // Instant preview when selecting a file
        profilePictureInput.addEventListener("change", function () {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    profilePicturePreview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // --- AJAX Handlers for "Edit Account Details" Mini-Forms ---
    function handleFormSubmit(formId, feedbackId) {
        const form = document.getElementById(formId);
        if (form) {
            form.addEventListener("submit", function (event) {
                event.preventDefault();
                const formData = new FormData(form);
                fetch(form.action, {
                    method: "POST",
                    body: formData,
                    headers: { "X-Requested-With": "XMLHttpRequest" }
                })
                .then(response => response.json())
                .then(data => {
                    const feedback = document.getElementById(feedbackId);
                    feedback.innerHTML = data.success 
                        ? `<div class="alert alert-success">${data.message}</div>`
                        : `<div class="alert alert-danger">${data.error}</div>`;
                })
                .catch(error => {
                    console.error("Error:", error);
                    document.getElementById(feedbackId).innerHTML = `<div class="alert alert-danger">An error occurred. Please try again.</div>`;
                });
            });
        }
    }

    handleFormSubmit("update-username-form", "username-feedback");
    handleFormSubmit("update-email-form", "email-feedback");
    handleFormSubmit("update-password-form", "password-feedback");

    // --- Discard Buttons for Form Fields ---
    function setupDiscardButton(buttonClass, fieldId, feedbackId) {
        const button = document.querySelector(buttonClass);
        if (button) {
            button.addEventListener("click", function () {
                const field = document.getElementById(fieldId);
                field.value = field.getAttribute("data-original-value");
                const feedback = document.getElementById(feedbackId);
                if (feedback) { feedback.innerHTML = ""; }
            });
        }
    }

    setupDiscardButton(".discard-username-btn", "username_field", "username-feedback");
    setupDiscardButton(".discard-email-btn", "email_field", "email-feedback");

    // --- AJAX Handler for News Feed Preferences ---
    const preferencesForm = document.getElementById("news-feed-preferences-form");
    if (preferencesForm) {
        preferencesForm.addEventListener("submit", function (event) {
            event.preventDefault();
            const formData = new FormData(preferencesForm);
            fetch(preferencesForm.action, {
                method: "POST",
                body: formData,
                headers: { "X-Requested-With": "XMLHttpRequest" }
            })
            .then(response => response.json())
            .then(data => {
                const feedback = document.getElementById("preferences-feedback");
                feedback.innerHTML = data.success 
                    ? `<div class="alert alert-success">${data.message}</div>`
                    : `<div class="alert alert-danger">${data.error}</div>`;
            })
            .catch(error => {
                console.error("Error:", error);
                document.getElementById("preferences-feedback").innerHTML = `<div class="alert alert-danger">An error occurred. Please try again.</div>`;
            });
        });
    }

    // --- AJAX Handlers for Saved Articles, Upvoted Articles, and Comments ---
    function setupRemoveHandler(selector, endpoint, listId) {
        document.querySelectorAll(selector).forEach(button => {
            button.addEventListener("click", function () {
                const itemId = this.getAttribute("data-id");
                if (!itemId) {
                    console.error("Missing item ID for", selector);
                    return;
                }
                
                fetch(endpoint, {
                    method: "POST",
                    body: new URLSearchParams({ "id": itemId }),
                    headers: {
                        "X-CSRFToken": getCookie("csrftoken"),
                        "X-Requested-With": "XMLHttpRequest"
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Server responded with status ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        this.closest("li").remove();
                    } else {
                        console.error("Error from server:", data.error);
                    }
                })
                .catch(error => console.error("Error:", error));
            });
        });
    }

    setupRemoveHandler(".remove-saved", "/users/remove-saved-article/", "article_id");
    setupRemoveHandler(".remove-upvote", "/users/remove-upvoted-article/", "article_id");
    setupRemoveHandler(".remove-comment", "/users/remove-comment/", "comment_id");


    // --- Clear All Saved/Upvoted Articles ---
    function setupClearAllButton(buttonId, endpoint, listId, emptyMessage) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.addEventListener("click", function () {
                fetch(endpoint, {
                    method: "POST",
                    headers: { "X-CSRFToken": getCookie("csrftoken") }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById(listId).innerHTML = `<p class="text-muted">${emptyMessage}</p>`;
                    }
                })
                .catch(error => console.error("Error:", error));
            });
        }
    }

    setupClearAllButton("clear-saved", "/users/clear-saved-articles/", "article_id", "No saved articles.");
    setupClearAllButton("clear-upvoted", "/users/clear-upvoted-articles/", "article_id", "No upvoted articles.");

    // --- Secure Account Deletion Handler ---
    const deleteAccountForm = document.getElementById("delete-account-form");
    if (deleteAccountForm) {
        deleteAccountForm.addEventListener("submit", function (event) {
            event.preventDefault();
            if (confirm("Are you sure you want to delete your account? This action is irreversible.")) {
                const formData = new FormData(deleteAccountForm);
                fetch("/users/delete-account/", {
                    method: "POST",
                    body: formData,
                    headers: { "X-CSRFToken": getCookie("csrftoken") }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert("Account deleted successfully.");
                        window.location.href = "/";
                    } else {
                        alert(data.error);
                    }
                })
                .catch(error => console.error("Error:", error));
            }
        });
    }
});
