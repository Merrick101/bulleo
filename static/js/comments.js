document.addEventListener("DOMContentLoaded", function () {
    console.log("comments.js loaded successfully!");

    // Sorting function
    const sortDropdown = document.getElementById("sort-comments");
    if (sortDropdown) {
        sortDropdown.addEventListener("change", function () {
            window.location.href = "?sort=" + this.value;
        });
    }

    // Retrieve the article ID
    const articleDetail = document.querySelector('.article-detail');
    const article_id = articleDetail ? articleDetail.getAttribute('data-article-id') : null;

    // Event delegation for vote, reply, report, edit, and delete actions
    const commentsList = document.getElementById("comments-list");
    if (commentsList) {
        commentsList.addEventListener("click", function (event) {
            if (event.target.classList.contains("vote-btn")) {
                const action = event.target.dataset.action;
                const commentId = event.target.dataset.commentId;
                voteComment(commentId, action);
            } else if (event.target.classList.contains("reply-btn")) {
                const parentId = event.target.dataset.parentId;
                showReplyForm(parentId);
            } else if (event.target.classList.contains("report-btn")) {
                const commentId = event.target.dataset.commentId;
                if (confirm("Are you sure you want to report this comment?")) {
                    reportComment(commentId, event.target);
                }
            } else if (event.target.classList.contains("edit-btn")) {
                const commentId = event.target.dataset.commentId;
                showEditForm(commentId);
            } else if (event.target.classList.contains("delete-btn")) {
                const commentId = event.target.dataset.commentId;
                if (confirm("Are you sure you want to delete this comment?")) {
                    deleteComment(commentId);
                }
            } else if (event.target.classList.contains("toggle-replies")) {
                toggleReplies(event.target);
            }
        });
    }

    // 1) Vote
    function voteComment(commentId, action) {
        fetch(`/news/comment/${commentId}/vote/${action}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const upvoteElem = document.querySelector(`#upvote-count-${commentId}`);
                const downvoteElem = document.querySelector(`#downvote-count-${commentId}`);
                if (upvoteElem) upvoteElem.textContent = data.upvotes;
                if (downvoteElem) downvoteElem.textContent = data.downvotes;
            } else {
                alert("Failed to vote.");
            }
        })
        .catch(err => console.error("Error with voting:", err));
    }

    // 2) Show Reply
    function showReplyForm(parentId) {
        const parentComment = document.querySelector(`#comment-${parentId}`);
        if (!parentComment) return;
    
        const replyFormHTML = `
            <form class="reply-form">
                <textarea name="content" rows="3" placeholder="Write a reply..." required></textarea>
                <button type="submit" class="btn btn-primary">Submit Reply</button>
                <button type="button" class="btn btn-secondary cancel-reply">Cancel</button>
            </form>
        `;
    
        let replyContainer = parentComment.querySelector(".replies");
        if (!replyContainer) {
            replyContainer = document.createElement("div");
            replyContainer.classList.add("replies");
            parentComment.appendChild(replyContainer);
        }
        replyContainer.innerHTML = replyFormHTML;
    
        const replyForm = replyContainer.querySelector(".reply-form");
        replyForm.addEventListener("submit", function (e) {
            e.preventDefault();
            submitReply(replyForm, parentId);
        });
    
        const cancelButton = replyContainer.querySelector(".cancel-reply");
        cancelButton.addEventListener("click", function () {
            replyContainer.innerHTML = '';  // Remove the reply form
        });
    }    

    // 3) Submit Reply
    function submitReply(form, parentId) {
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true;
    
        const formData = new FormData(form);
        formData.append("parent_comment_id", parentId);
    
        fetch(`/news/article/${article_id}/comment/${parentId}/reply/`, {
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
    
                // Clear the reply form after submission
                const parentComment = document.querySelector(`#comment-${parentId}`);
                if (parentComment) {
                    const replyContainer = parentComment.querySelector(".replies");
                    if (replyContainer) {
                        replyContainer.innerHTML = '';
                        // Force the replies container to be visible immediately
                        replyContainer.style.display = "block";
                    }
                }
    
                updateCommentCount();  // Update count
            } else {
                alert("Failed to submit reply.");
            }
        })
        .catch(error => console.error("Error submitting reply:", error))
        .finally(() => {
            submitButton.disabled = false;
        });
    }    

    // 4) Report Comment
    function reportComment(commentId, button) {
        fetch(`/news/comment/${commentId}/report/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Comment reported.");
                button.disabled = true;
            } else {
                alert("Failed to report the comment.");
            }
        })
        .catch(err => console.error("Error reporting comment:", err));
    }

    // 5) Show Edit
    function showEditForm(commentId) {
        const commentDiv = document.querySelector(`#comment-${commentId}`);
        if (!commentDiv) return;
        const contentParagraph = commentDiv.querySelector(".comment-body p");
        if (!contentParagraph) return;

        const oldContent = contentParagraph.textContent.trim();
        const editFormHTML = `
            <form class="edit-form">
                <textarea name="content" rows="3" required>${oldContent}</textarea>
                <button type="submit" class="btn btn-primary">Save</button>
                <button type="button" class="btn btn-secondary cancel-edit">Cancel</button>
            </form>
        `;
        contentParagraph.innerHTML = editFormHTML;

        const editForm = contentParagraph.querySelector(".edit-form");
        const cancelEditButton = contentParagraph.querySelector(".cancel-edit");

        editForm.addEventListener("submit", function(e) {
            e.preventDefault();
            submitEditForm(commentId, editForm);
        });

        cancelEditButton.addEventListener("click", function() {
            contentParagraph.textContent = oldContent;
        });
    }

    // 6) Submit Edit
    function submitEditForm(commentId, form) {
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        const formData = new FormData(form);

        fetch(`/news/comment/${commentId}/edit/`, {
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
                const commentDiv = document.querySelector(`#comment-${data.comment_id}`);
                const contentParagraph = commentDiv.querySelector(".comment-body p");
                if (contentParagraph) {
                    contentParagraph.textContent = data.updated_content;
                }
            } else {
                alert("Failed to edit comment. " + (data.error || ""));
            }
        })
        .catch(error => console.error("Error editing comment:", error))
        .finally(() => {
            submitButton.disabled = false;
        });
    }

    // 7) Delete Comment
    function deleteComment(commentId) {
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
                const commentDiv = document.getElementById(`comment-${data.comment_id}`);
                if (commentDiv) {
                    // Mark comment as deleted without removing nested replies
                    commentDiv.classList.add("deleted-comment");
                    const header = commentDiv.querySelector(".comment-header");
                    if (header) {
                        // Optionally, use data.updated_at if provided by your backend, or display current time
                        header.innerHTML = `<p><strong>Deleted</strong> <small>${new Date().toLocaleString()}</small></p>`;
                    }
                    const body = commentDiv.querySelector(".comment-body");
                    if (body) {
                        body.innerHTML = `<p class="deleted-content">[Deleted]</p><small class="deleted-note">Actions disabled for deleted comments</small>`;
                    }
                    // Remove action buttons so no further interactions occur, but keep replies intact
                    const actions = commentDiv.querySelector(".comment-actions");
                    if (actions) {
                        actions.remove();
                    }
                }
            } else {
                alert("Failed to delete the comment.");
            }
        })
        .catch(err => console.error("Error deleting comment:", err));
    }
    
    function updateCommentCount() {
        const commentsList = document.getElementById("comments-list");
        // Count all elements with class 'comment' (ensure this selector is specific to comments only)
        const commentElements = commentsList.querySelectorAll(".comment");
        document.getElementById("comment-count").textContent = commentElements.length;
    }    

    // Toggle Replies Visibility
    function toggleReplies(button) {
        const repliesContainer = button.nextElementSibling; // The next div is the replies container
        if (repliesContainer.style.display === "none" || repliesContainer.style.display === "") {
            repliesContainer.style.display = "block";
            button.textContent = "Hide Replies";
        } else {
            repliesContainer.style.display = "none";
            button.textContent = "Show Replies";
        }
    }

    // Get CSRF Token
    function getCSRFToken() {
        const cookie = document.cookie.split("; ").find(row => row.startsWith("csrftoken="));
        return cookie ? cookie.split("=")[1] : "";
    }

    // Main Comment Form Submission via AJAX
    const commentForm = document.getElementById("comment-form");
    if (commentForm) {
        commentForm.addEventListener("submit", function (e) {
            e.preventDefault();
            const formData = new FormData(commentForm);
            fetch(commentForm.action, {
                method: 'POST',
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
                    commentForm.reset();
                    updateCommentCount();
                } else {
                    alert("There was an error posting your comment.");
                }
            })
            .catch(error => console.error("Error submitting comment:", error));
        });
    }

    // 8) Render New Comment
    function renderNewComment(data) {
        const noCommentsMsg = document.getElementById("no-comments-msg");
        if (noCommentsMsg) {
            noCommentsMsg.remove();
        }
    
        // Build actions HTML based on ownership
        let actionsHTML = `
            <button class="btn btn-sm btn-outline-success vote-btn" data-action="upvote" data-comment-id="${data.comment_id}">👍</button>
            <span class="upvote-count" id="upvote-count-${data.comment_id}">0</span>
            <button class="btn btn-sm btn-outline-danger vote-btn" data-action="downvote" data-comment-id="${data.comment_id}">👎</button>
            <span class="downvote-count" id="downvote-count-${data.comment_id}">0</span>
            <button class="btn btn-sm btn-outline-primary reply-btn" data-parent-id="${data.comment_id}">Reply</button>
        `;
        if (data.is_owner) {
            actionsHTML += `
                <button class="btn btn-sm btn-outline-warning edit-btn" data-comment-id="${data.comment_id}">Edit</button>
                <button class="btn btn-sm btn-outline-danger delete-btn" data-comment-id="${data.comment_id}">Delete</button>
            `;
        } else {
            actionsHTML += `
                <button class="btn btn-sm btn-outline-danger report-btn" data-comment-id="${data.comment_id}">Report</button>
            `;
        }
    
        const newCommentHTML = `
            <div class="comment mb-3" id="comment-${data.comment_id}" data-comment-id="${data.comment_id}" data-level="${data.parent_comment_id ? 1 : 0}">
                <div class="comment-header">
                    <p>
                        <strong>${data.username}</strong> 
                        <small>${data.created_at}</small>
                    </p>
                </div>
                <div class="comment-body">
                    <p>${data.content}</p>
                </div>
                <div class="comment-actions">
                    ${actionsHTML}
                </div>
                <div class="replies"></div> <!-- Replies go here -->
            </div>
        `;
    
        if (data.parent_comment_id) {
            const parentRepliesContainer = document.querySelector(`#comment-${data.parent_comment_id} .replies`);
            if (parentRepliesContainer) {
                parentRepliesContainer.insertAdjacentHTML("beforeend", newCommentHTML);
                // Force the replies container to be visible immediately
                parentRepliesContainer.style.display = "block";
            }
        } else {
            document.getElementById("comments-list").insertAdjacentHTML("beforeend", newCommentHTML);
        }
    
        updateIndentation();
    }

    // New: updateIndentation function to adjust nested comments
    function updateIndentation() {
        const comments = document.querySelectorAll("#comments-list .comment");
        comments.forEach(comment => {
            const level = parseInt(comment.getAttribute("data-level")) || 0;
            // For example, add a 20px left margin for each level
            comment.style.marginLeft = (level * 20) + "px";
        });
    }
});
