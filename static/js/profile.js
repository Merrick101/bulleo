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

// Show toast notification
function showToast(message, variant = "success") {
    const toast = document.createElement("div");
    toast.className = `toast align-items-center text-white bg-${variant} border-0 position-fixed bottom-0 end-0 m-4 show`;
    toast.style.zIndex = "9999";
    toast.setAttribute("role", "alert");
    toast.setAttribute("aria-live", "assertive");
    toast.setAttribute("aria-atomic", "true");

    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    document.body.appendChild(toast);

    // Auto-remove after 5 seconds
    setTimeout(() => toast.remove(), 5000);
}

document.addEventListener("DOMContentLoaded", function () {
    console.log("profile.js loaded successfully!");
    // --- AJAX: Username, Email, Password Forms ---
    function handleFormSubmit(formId, feedbackId) {
        const form = document.getElementById(formId);
        if (form) {
            form.addEventListener("submit", function (event) {
                event.preventDefault();
                
                // Check if the user confirms the action
                if (!confirm("Are you sure you want to save your changes?")) {
                    return;
                }

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
                    if (data.success) {
                        showToast(data.message);  // Toast on success
                        feedback.innerHTML = "";  // Clear inline feedback
                    } else {
                        feedback.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                    }
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

    // --- AJAX: News Preferences ---
    const preferencesForm = document.getElementById("news-feed-preferences-form");
    if (preferencesForm) {
        preferencesForm.addEventListener("submit", function (event) {
            event.preventDefault();

            // Show confirmation prompt
            if (!confirm("Are you sure you want to save your preferences?")) {
                return;
            }

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
                if (data.success) {
                    feedback.innerHTML = "";
                    showToast(data.message);
                    // Update profile preferences display dynamically
                    const displayEl = document.getElementById("user-preferences-display");
                    if (displayEl) {
                        const checkedBoxes = preferencesForm.querySelectorAll('input[type="checkbox"]:checked');

                        if (checkedBoxes.length === 0) {
                            displayEl.innerHTML = '<span class="text-muted">None selected.</span>';
                        } else {
                            const newBadges = Array.from(checkedBoxes).map(input => {
                                const labelEl = input.closest(".form-check")?.querySelector("label");
                                const label = labelEl ? labelEl.textContent.trim() : "Unknown";
                                return `<span class="badge bg-secondary me-1">${label}</span>`;
                            }).join(" ");
                            displayEl.innerHTML = newBadges;
                        }
                    }
                } else {
                    feedback.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                }
            })
                    .catch(error => {
                        console.error("Error:", error);
                        document.getElementById("preferences-feedback").innerHTML = `<div class="alert alert-danger">An error occurred. Please try again.</div>`;
                    });
            });
    }

    // Attach event handlers to remove individual items dynamically
    function setupRemoveHandler(selector, endpoint, toastMessage) {
        document.querySelectorAll(selector).forEach(button => {
            button.addEventListener("click", function () {
                if (!confirm("Are you sure you want to remove this item?")) return;

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
                    if (data.success) {
                        this.closest("li").remove();
                        showToast(toastMessage);
                    }
                })
                .catch(err => console.error("Error:", err));
            });
        });
    }

    // --- AJAX: Remove Saved/Upvoted Articles and Comments ---
    document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener("shown.bs.tab", function (event) {
            const tabId = event.target.getAttribute("data-bs-target");

            // Delay slightly to ensure content renders
            setTimeout(() => {
                if (tabId === "#saved") {
                    setupRemoveHandler(".remove-saved", "/users/remove-saved-article/", "Saved article removed.");
                } else if (tabId === "#upvoted") {
                    setupRemoveHandler(".remove-upvote", "/users/remove-upvoted-article/", "Upvoted article removed.");
                } else if (tabId === "#comments") {
                    setupRemoveHandler(".remove-comment", "/users/remove-comment/", "Comment removed.");
                }
            }, 100);
        });
    });

    function setupClearAllButton(buttonId, endpoint, listId, emptyMessage, toastMessage) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.addEventListener("click", function () {
                if (!confirm("Are you sure you want to remove all items?")) return;

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
                        showToast(toastMessage);
                    }
                })
                .catch(err => console.error("Error:", err));
            });
        }
    }

    setupClearAllButton("clear-saved", "/users/clear-saved-articles/", "saved-articles-list", "No saved articles.", "All saved articles removed.");
    setupClearAllButton("clear-upvoted", "/users/clear-upvoted-articles/", "upvoted-articles-list", "No upvoted articles.", "All upvoted articles removed.");

    // --- Clear All Comments ---
    const clearCommentsButton = document.getElementById("clear-comments-btn");
    if (clearCommentsButton) {
        clearCommentsButton.addEventListener("click", function () {
            if (!confirm("Are you sure you want to remove all your comments?")) return;

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
                    // Handle both comment list or fallback message
                    const commentList = document.getElementById("comment-history-list");
                    const msgData = document.getElementById("empty-comments-message");
                    const fallbackMessage = msgData ? msgData.dataset.message : "No comments posted.";

                    if (commentList) {
                        commentList.outerHTML = `<p class="text-muted" id="empty-comments-message" data-message="${fallbackMessage}">${fallbackMessage}</p>`;
                    } else if (!msgData) {
                        // If neither exists, inject the message
                        const commentsTab = document.getElementById("comments");
                        if (commentsTab) {
                            commentsTab.innerHTML = `<p class="text-muted" id="empty-comments-message" data-message="${fallbackMessage}">${fallbackMessage}</p>`;
                        }
                    }

                    showToast("All comments removed.");
                    clearCommentsButton.remove();
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
