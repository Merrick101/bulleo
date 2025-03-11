document.addEventListener("DOMContentLoaded", function () {
    console.log("comments.js loaded successfully!");

    // ------------------------------------------------------
    // 1) Sorting
    // ------------------------------------------------------
    const sortDropdown = document.getElementById("sort-comments");
    let sortOrder = "newest";  // default
    if (sortDropdown) {
        sortOrder = sortDropdown.value;
        sortDropdown.addEventListener("change", function () {
            window.location.href = "?sort=" + this.value;
        });
    }

    // ------------------------------------------------------
    // 2) Global Setup
    // ------------------------------------------------------
    const articleDetail = document.querySelector(".article-detail");
    const article_id = articleDetail ? articleDetail.getAttribute("data-article-id") : null;
    const commentsList = document.getElementById("comments-list");

    // ------------------------------------------------------
    // 3) Event Delegation
    // ------------------------------------------------------
    if (commentsList) {
        commentsList.addEventListener("click", function (event) {
            const target = event.target;
            if (target.classList.contains("vote-btn")) {
                voteComment(target.dataset.commentId, target.dataset.action);
            } else if (target.classList.contains("reply-btn")) {
                showReplyForm(target.dataset.parentId);
            } else if (target.classList.contains("report-btn")) {
                if (confirm("Are you sure you want to report this comment?")) {
                    reportComment(target.dataset.commentId, target);
                }
            } else if (target.classList.contains("edit-btn")) {
                showEditForm(target.dataset.commentId);
            } else if (target.classList.contains("delete-btn")) {
                if (confirm("Are you sure you want to delete this comment?")) {
                    deleteComment(target.dataset.commentId);
                }
            } else if (target.classList.contains("toggle-replies")) {
                toggleReplies(target);
            }
        });
    }

    // ------------------------------------------------------
    // 4) Vote
    // ------------------------------------------------------
    function voteComment(commentId, action) {
        fetch(`/news/comment/${commentId}/vote/${action}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(res => res.json())
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

    // ------------------------------------------------------
    // 5) Reply
    // ------------------------------------------------------
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
            replyContainer.innerHTML = "";
        });
    }

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
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // 1) Render the new reply
                renderNewComment(data);

                // 2) Clear the reply form
                const parentComment = document.querySelector(`#comment-${parentId}`);
                if (parentComment) {
                    const replyContainer = parentComment.querySelector(".replies");
                    if (replyContainer) {
                        replyContainer.innerHTML = "";
                        // Make sure the container is visible so the new reply is shown
                        replyContainer.style.display = "block";
                    }
                    // 3) Add or update the parent's toggle if needed
                    ensureToggleForParent(parentComment);
                }

                // 4) Update the comment count from the server
                if (data.comment_count !== undefined) {
                    document.getElementById("comment-count").textContent = data.comment_count;
                }
            } else {
                alert("Failed to submit reply.");
            }
        })
        .catch(err => console.error("Error submitting reply:", err))
        .finally(() => {
            submitButton.disabled = false;
        });
    }

    // ------------------------------------------------------
    // 6) Ensure Parent Has a Toggle
    // ------------------------------------------------------
    function ensureToggleForParent(parentCommentDiv) {
        // The parent comment's .replies container
        const repliesContainer = parentCommentDiv.querySelector(".replies");
        if (!repliesContainer) return;

        // If there's at least one .comment inside .replies, we want a toggle
        const childComments = repliesContainer.querySelectorAll(".comment");
        if (childComments.length > 0) {
            // Check if there's already a toggle
            let toggleBtn = parentCommentDiv.querySelector(".toggle-replies");
            if (!toggleBtn) {
                // Insert a toggle button that says "Hide Replies"
                // because we are forcing the container to be visible now
                const toggleHTML = `<button class="btn btn-link toggle-replies">Hide Replies</button>`;
                repliesContainer.insertAdjacentHTML("beforebegin", toggleHTML);
            } else {
                // If a toggle already exists, ensure it says "Hide Replies" 
                // because we are showing them after adding a new reply
                toggleBtn.textContent = "Hide Replies";
            }
        }
    }

    // ------------------------------------------------------
    // 7) Report
    // ------------------------------------------------------
    function reportComment(commentId, button) {
        fetch(`/news/comment/${commentId}/report/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(res => res.json())
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

    // ------------------------------------------------------
    // 8) Edit
    // ------------------------------------------------------
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
        .then(res => res.json())
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
        .catch(err => console.error("Error editing comment:", err))
        .finally(() => {
            submitButton.disabled = false;
        });
    }

    // ------------------------------------------------------
    // 9) Delete
    // ------------------------------------------------------
    function deleteComment(commentId) {
        fetch(`/news/comment/${commentId}/delete/`, {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCSRFToken()
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const commentDiv = document.getElementById(`comment-${data.comment_id}`);
                if (commentDiv) {
                    // Mark as deleted but keep nested replies
                    commentDiv.classList.add("deleted-comment");

                    // Update header to show "Deleted" and a timestamp
                    const header = commentDiv.querySelector(".comment-header");
                    if (header) {
                        header.innerHTML = `
                            <p>
                                <strong>Deleted</strong>
                                <small>${new Date().toLocaleString()}</small>
                            </p>
                        `;
                    }

                    // Update body with deletion notice
                    const body = commentDiv.querySelector(".comment-body");
                    if (body) {
                        body.innerHTML = `
                            <p class="deleted-content">[Deleted]</p>
                            <small class="deleted-note">Actions disabled for deleted comments</small>
                        `;
                    }

                    // Remove action buttons
                    const actions = commentDiv.querySelector(".comment-actions");
                    if (actions) {
                        actions.remove();
                    }
                }

                // Update comment count if provided by the server
                if (data.comment_count !== undefined) {
                    document.getElementById("comment-count").textContent = data.comment_count;
                }
            } else {
                alert("Failed to delete the comment.");
            }
        })
        .catch(err => console.error("Error deleting comment:", err));
    }

    // ------------------------------------------------------
    // 10) Main Comment Form
    // ------------------------------------------------------
    const commentForm = document.getElementById("comment-form");
    if (commentForm) {
        commentForm.addEventListener("submit", function(e) {
            e.preventDefault();
            const formData = new FormData(commentForm);

            fetch(commentForm.action, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": getCSRFToken()
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // Render the new top-level comment
                    renderNewComment(data);
                    commentForm.reset();

                    // Update comment count from the server
                    if (data.comment_count !== undefined) {
                        document.getElementById("comment-count").textContent = data.comment_count;
                    }
                } else {
                    alert("There was an error posting your comment.");
                }
            })
            .catch(err => console.error("Error submitting comment:", err));
        });
    }

    // ------------------------------------------------------
    // 11) Render New Comment
    // ------------------------------------------------------
    function renderNewComment(data) {
        const noCommentsMsg = document.getElementById("no-comments-msg");
        if (noCommentsMsg) noCommentsMsg.remove();

        // Build action buttons based on ownership
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
            <div class="comment mb-3"
                 id="comment-${data.comment_id}"
                 data-comment-id="${data.comment_id}"
                 data-level="${data.parent_comment_id ? 1 : 0}">
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
                <div class="replies"></div>
            </div>
        `;

        if (data.parent_comment_id) {
            const parentRepliesContainer = document.querySelector(`#comment-${data.parent_comment_id} .replies`);
            if (parentRepliesContainer) {
                // Show the container
                parentRepliesContainer.style.display = "block";
                parentRepliesContainer.insertAdjacentHTML("beforeend", newCommentHTML);

                // Also ensure the parent has a toggle
                const parentDiv = document.querySelector(`#comment-${data.parent_comment_id}`);
                if (parentDiv) ensureToggleForParent(parentDiv);
            }
        } else {
            if (sortOrder === "newest") {
                commentsList.insertAdjacentHTML("afterbegin", newCommentHTML);
            } else {
                commentsList.insertAdjacentHTML("beforeend", newCommentHTML);
            }
        }

        updateIndentation();
    }

    // ------------------------------------------------------
    // 12) Toggle Replies
    // ------------------------------------------------------
    function toggleReplies(button) {
        const repliesContainer = button.nextElementSibling;
        if (!repliesContainer) return;

        if (repliesContainer.style.display === "none" || repliesContainer.style.display === "") {
            repliesContainer.style.display = "block";
            button.textContent = "Hide Replies";
        } else {
            repliesContainer.style.display = "none";
            button.textContent = "Show Replies";
        }
    }

    // ------------------------------------------------------
    // 13) Indentation
    // ------------------------------------------------------
    function updateIndentation() {
        const comments = document.querySelectorAll("#comments-list .comment");
        comments.forEach(comment => {
            const level = parseInt(comment.getAttribute("data-level")) || 0;
            comment.style.marginLeft = (level * 20) + "px";
        });
    }

    // ------------------------------------------------------
    // 14) CSRF Token Helper
    // ------------------------------------------------------
    function getCSRFToken() {
        const cookie = document.cookie.split("; ").find(row => row.startsWith("csrftoken="));
        return cookie ? cookie.split("=")[1] : "";
    }
});
