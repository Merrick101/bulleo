document.addEventListener("DOMContentLoaded", function () {
    console.log("comments.js loaded successfully!");

    // Sorting function
    const sortDropdown = document.getElementById("sort-comments");
    if (sortDropdown) {
        sortDropdown.addEventListener("change", function () {
            window.location.href = `?sort=${this.value}`;
        });
    }

    // AJAX for Comment Submission (Top-Level & Replies)
    document.getElementById("comment-form").addEventListener("submit", function (event) {
        event.preventDefault();
        submitComment(this);
    });

    function submitComment(form) {
        const formData = new FormData(form);
        fetch(form.action, {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                renderNewComment(data);
                form.reset();
            } else {
                alert("Failed to submit comment.");
            }
        })
        .catch(error => console.error("Error submitting comment:", error));
    }

    function renderNewComment(data) {
        const commentList = document.getElementById("comments-list");
        const parentCommentId = data.parent_comment_id;

        const newComment = document.createElement("div");
        newComment.classList.add("comment", "border", "rounded", "p-3", "my-3");
        newComment.dataset.commentId = data.comment_id;
        newComment.innerHTML = `
            <p><strong>${data.username}</strong> - ${data.created_at}</p>
            <p class="comment-content">${data.content}</p>
            <div class="d-flex align-items-center">
                <button class="btn btn-sm btn-outline-primary reply-btn" data-parent-id="${data.comment_id}">Reply</button>
                <button class="btn btn-sm btn-outline-success vote-btn" data-action="upvote" data-comment-id="${data.comment_id}">👍</button>
                <span class="upvote-count" id="upvote-count-${data.comment_id}">0</span>
                <button class="btn btn-sm btn-outline-danger vote-btn" data-action="downvote" data-comment-id="${data.comment_id}">👎</button>
                <span class="downvote-count" id="downvote-count-${data.comment_id}">0</span>
                <button class="btn btn-sm btn-outline-primary edit-btn" data-comment-id="${data.comment_id}">✏️ Edit</button>
                <button class="btn btn-sm btn-outline-danger delete-btn" data-comment-id="${data.comment_id}">🗑️ Delete</button>
            </div>
            <div class="replies ms-4"></div>
        `;

        if (parentCommentId) {
            document.querySelector(`#comment-${parentCommentId} .replies`).appendChild(newComment);
        } else {
            commentList.prepend(newComment);
        }

        document.getElementById("comment-count").textContent++;
    }

    // Handle Reply Button Clicks
    document.getElementById("comments-list").addEventListener("click", function (event) {
        if (event.target.classList.contains("reply-btn")) {
            const parentId = event.target.dataset.parentId;
            showReplyForm(parentId, event.target);
        }
    });

    function showReplyForm(parentId, replyButton) {
        if (document.querySelector(`#reply-form-${parentId}`)) return;

        const replyForm = document.createElement("form");
        replyForm.classList.add("reply-form", "mt-2");
        replyForm.id = `reply-form-${parentId}`;
        replyForm.innerHTML = `
            <textarea name="content" class="form-control" rows="2" required placeholder="Write a reply..."></textarea>
            <input type="hidden" name="parent_comment_id" value="${parentId}">
            <button type="submit" class="btn btn-sm btn-success mt-2">Post Reply</button>
        `;

        replyButton.insertAdjacentElement("afterend", replyForm);

        replyForm.addEventListener("submit", function (e) {
            e.preventDefault();
            submitComment(replyForm);
        });
    }

    // AJAX for Editing Comments
    document.getElementById("comments-list").addEventListener("click", function (event) {
        if (event.target.classList.contains("edit-btn")) {
            const commentDiv = event.target.closest(".comment");
            const commentId = event.target.dataset.commentId;
            const contentElement = commentDiv.querySelector(".comment-content");

            const editForm = document.createElement("form");
            editForm.innerHTML = `
                <textarea class="form-control" id="edit-content-${commentId}">${contentElement.textContent.trim()}</textarea>
                <button type="submit" class="btn btn-sm btn-success mt-2">Save</button>
                <button type="button" class="btn btn-sm btn-secondary mt-2 cancel-edit">Cancel</button>
            `;

            commentDiv.replaceChild(editForm, contentElement);

            editForm.querySelector(".cancel-edit").addEventListener("click", function () {
                commentDiv.replaceChild(contentElement, editForm);
            });

            editForm.addEventListener("submit", function (event) {
                event.preventDefault();
                const newContent = document.getElementById(`edit-content-${commentId}`).value.trim();

                fetch(`/news/comment/${commentId}/edit/`, {
                    method: "POST",
                    body: new URLSearchParams({"content": newContent}),
                    headers: { 
                        "X-Requested-With": "XMLHttpRequest", 
                        "X-CSRFToken": getCSRFToken() 
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        contentElement.textContent = data.updated_content;
                        commentDiv.replaceChild(contentElement, editForm);
                    } else {
                        alert("Error updating comment.");
                    }
                })
                .catch(error => console.error("Error updating comment:", error));
            });
        }
    });

    // AJAX for Deleting Comments
    document.getElementById("comments-list").addEventListener("click", function (event) {
        if (event.target.classList.contains("delete-btn")) {
            const commentDiv = event.target.closest(".comment");
            const commentId = event.target.dataset.commentId;

            if (!confirm("Are you sure you want to delete this comment?")) return;

            fetch(`/news/comment/${commentId}/delete/`, {
                method: "POST",
                headers: { 
                    "X-Requested-With": "XMLHttpRequest", 
                    "X-CSRFToken": getCSRFToken() 
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    commentDiv.remove();
                    document.getElementById("comment-count").textContent--;
                } else {
                    alert("Error deleting comment.");
                }
            })
            .catch(error => console.error("Error deleting comment:", error));
        }
    });

    // AJAX for Upvote/Downvote
    document.getElementById("comments-list").addEventListener("click", function (event) {
        if (event.target.classList.contains("vote-btn")) {
            const commentId = event.target.dataset.commentId;
            const action = event.target.dataset.action;

            fetch(`/news/comment/${commentId}/vote/${action}/`, {
                method: "POST",
                headers: { 
                    "X-Requested-With": "XMLHttpRequest", 
                    "X-CSRFToken": getCSRFToken() 
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById(`upvote-count-${commentId}`).textContent = data.upvotes;
                    document.getElementById(`downvote-count-${commentId}`).textContent = data.downvotes;
                }
            })
            .catch(error => console.error("Error processing vote:", error));
        }
    });

    // Helper function to get CSRF token
    function getCSRFToken() {
        return document.cookie.split("; ")
            .find(row => row.startsWith("csrftoken="))
            ?.split("=")[1];
    }
});
