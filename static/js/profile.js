// CSRF helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener("DOMContentLoaded", function () {
    // --- AJAX: Username, Email, Password Forms ---
    function handleFormSubmit(formId, feedbackId) {
        const form = document.getElementById(formId);
        if (form) {
            form.addEventListener("submit", function (event) {
                event.preventDefault();

                // Disable all inputs and buttons
                const elements = form.querySelectorAll("input, button");
                elements.forEach(el => el.disabled = true);

                const formData = new URLSearchParams(new FormData(form));

                fetch(form.action, {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": getCookie("csrftoken")
                    }
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
                })
                .finally(() => {
                    // Re-enable form elements after request completes
                    elements.forEach(el => el.disabled = false);
                });
            });
        }
    }

    handleFormSubmit("update-username-form", "username-feedback");
    handleFormSubmit("update-email-form", "email-feedback");
    handleFormSubmit("update-password-form", "password-feedback");

    // --- Discard Buttons ---
    function setupDiscardButton(buttonClass, fieldId, feedbackId) {
        const button = document.querySelector(buttonClass);
        if (button) {
            button.addEventListener("click", function () {
                const field = document.getElementById(fieldId);
                field.value = field.getAttribute("data-original-value");
                const feedback = document.getElementById(feedbackId);
                if (feedback) feedback.innerHTML = "";
            });
        }
    }

    setupDiscardButton(".discard-username-btn", "username_field", "username-feedback");
    setupDiscardButton(".discard-email-btn", "email_field", "email-feedback");

    // --- AJAX: News Preferences ---
    const preferencesForm = document.getElementById("news-feed-preferences-form");
    if (preferencesForm) {
        preferencesForm.addEventListener("submit", function (event) {
            event.preventDefault();
            const formData = new URLSearchParams(new FormData(preferencesForm));

            fetch(preferencesForm.action, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": getCookie("csrftoken")
                }
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

    // --- Remove & Clear Buttons ---
    function setupRemoveHandler(selector, endpoint) {
        document.querySelectorAll(selector).forEach(button => {
            button.addEventListener("click", function () {
                const itemId = this.getAttribute("data-id");
                const paramKey = endpoint.includes("comment") ? "comment_id" : "id";
                fetch(endpoint, {
                    method: "POST",
                    body: new URLSearchParams({ [paramKey]: itemId }),
                    headers: {
                        "X-CSRFToken": getCookie("csrftoken"),
                        "X-Requested-With": "XMLHttpRequest"
                    }
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) this.closest("li").remove();
                })
                .catch(err => console.error("Error:", err));
            });
        });
    }

    setupRemoveHandler(".remove-saved", "/users/remove-saved-article/");
    setupRemoveHandler(".remove-upvote", "/users/remove-upvoted-article/");
    setupRemoveHandler(".remove-comment", "/users/remove-comment/");

    function setupClearAllButton(buttonId, endpoint, listId, emptyMessage) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.addEventListener("click", function () {
                fetch(endpoint, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCookie("csrftoken"),
                        "X-Requested-With": "XMLHttpRequest"
                    }
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById(listId).innerHTML = `<p class="text-muted">${emptyMessage}</p>`;
                    }
                })
                .catch(err => console.error("Error:", err));
            });
        }
    }

    setupClearAllButton("clear-saved", "/users/clear-saved-articles/", "saved-articles-list", "No saved articles.");
    setupClearAllButton("clear-upvoted", "/users/clear-upvoted-articles/", "upvoted-articles-list", "No upvoted articles.");

    // --- Clear All Comments ---
    const clearCommentsButton = document.getElementById("clear-comments-btn");
    if (clearCommentsButton) {
        clearCommentsButton.addEventListener("click", function () {
            fetch("/users/clear-comments/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const msg = document.getElementById("empty-comments-message").dataset.message;
                    document.getElementById("comment-history-list").innerHTML = `<p class="text-muted">${msg}</p>`;
                }
            })
            .catch(err => console.error("Error:", err));
        });
    }

    // --- Account Deletion ---
    const deleteAccountForm = document.getElementById("delete-account-form");
    if (deleteAccountForm) {
        deleteAccountForm.addEventListener("submit", function (event) {
            event.preventDefault();
            if (confirm("Are you sure you want to delete your account? This action is irreversible.")) {
                const formData = new URLSearchParams(new FormData(deleteAccountForm));
                fetch("/users/delete-account/", {
                    method: "POST",
                    body: formData,
                    headers: { "X-CSRFToken": getCookie("csrftoken") }
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        alert("Account deleted successfully.");
                        window.location.href = "/";
                    } else {
                        alert(data.error);
                    }
                })
                .catch(err => console.error("Error:", err));
            }
        });
    }
});
