// Define the function at top-level so it can be imported
export function toggleReplies(button) {
    const repliesContainer = button.parentElement.nextElementSibling;
    if (!repliesContainer) return;
  
    if (repliesContainer.style.display === "none") {
      repliesContainer.style.display = "block";
      button.textContent = "Hide Replies";
    } else {
      repliesContainer.style.display = "none";
      button.textContent = "Show More Replies";
    }
  }

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
    // 4) Voting
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
            // Set the container visible by default (show all replies)
            replyContainer.style.display = "block";
            parentComment.appendChild(replyContainer);
        } else {
            // Ensure it's visible
            replyContainer.style.display = "block";
        }
        replyContainer.innerHTML = replyFormHTML;
    
        const replyForm = replyContainer.querySelector(".reply-form");
        replyForm.addEventListener("submit", function (e) {
            e.preventDefault();
            submitReply(replyForm, parentId);
        });
    
        const cancelButton = replyContainer.querySelector(".cancel-reply");
        cancelButton.addEventListener("click", function () {
            // Clear the reply form, but leave existing replies visible.
            replyContainer.innerHTML = "";
            // Ensure toggle is updated.
            ensureToggleForParent(parentComment);
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
                // Force a full page reload after a reply is submitted successfully
                window.location.reload();
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
    // 6) Ensure Parent Has a Toggle Button
    // ------------------------------------------------------
    function ensureToggleForParent(parentCommentDiv) {
        let repliesContainer = parentCommentDiv.querySelector(".replies");
        if (!repliesContainer) return;
    
        // Since we want replies visible by default, force display to block.
        repliesContainer.style.display = "block";
    
        // Check if there is at least one child comment in the container.
        const childComments = repliesContainer.querySelectorAll(".comment");
        if (childComments.length > 0) {
            let toggleBtn = parentCommentDiv.querySelector(".toggle-replies");
            if (!toggleBtn) {
                // Insert a toggle button above the replies container
                const toggleHTML = `<button class="btn btn-link toggle-replies">Hide Replies</button>`;
                repliesContainer.insertAdjacentHTML("beforebegin", toggleHTML);
            } else {
                // Update the toggle text based on container state:
                toggleBtn.textContent = (repliesContainer.style.display === "block")
                    ? "Hide Replies"
                    : "Show More Replies";
            }
        } else {
            // No child comments: remove toggle if it exists
            let toggleBtn = parentCommentDiv.querySelector(".toggle-replies");
            if (toggleBtn) {
                toggleBtn.remove();
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

        const contentParagraph = commentDiv.querySelector(".my-comment-body p");
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
                const contentParagraph = commentDiv.querySelector(".my-comment-body p");
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
                    commentDiv.classList.add("deleted-comment");
                    const topRow = commentDiv.querySelector(".my-comment-top");
                    if (topRow) {
                        topRow.innerHTML = `
                            <p>
                                <strong>Deleted</strong>
                                <small>${new Date().toLocaleString()}</small>
                            </p>
                        `;
                    }
                    const bodyRow = commentDiv.querySelector(".my-comment-body");
                    if (bodyRow) {
                        bodyRow.innerHTML = `
                            <p class="deleted-content">[Deleted]</p>
                            <small class="deleted-note">Actions disabled for deleted comments</small>
                        `;
                    }
                    const actionsRow = commentDiv.querySelector(".my-comment-actions");
                    if (actionsRow) {
                        actionsRow.remove();
                    }
                }
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
    // 10) Main Comment Form Submission
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
                    renderNewComment(data);
                    commentForm.reset();
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

        let dropdownHTML = "";
        if (data.is_authenticated) {
            dropdownHTML = `
                <div class="dropdown my-comment-more-actions">
                <button class="btn btn-link dropdown-toggle my-ellipsis-btn" 
                        type="button" 
                        id="dropdownMenuButton-${data.comment_id}" 
                        data-bs-toggle="dropdown" 
                        aria-expanded="false">
                    …
                </button>
                <ul class="dropdown-menu" aria-labelledby="dropdownMenuButton-${data.comment_id}">
                    ${
                    data.is_owner
                        ? `
                        <li><a class="dropdown-item edit-btn" data-comment-id="${data.comment_id}" href="#">Edit</a></li>
                        <li><a class="dropdown-item delete-btn" data-comment-id="${data.comment_id}" href="#">Delete</a></li>
                        `
                        : `
                        <li><a class="dropdown-item report-btn" data-comment-id="${data.comment_id}" href="#">Report</a></li>
                        `
                    }
                </ul>
                </div>
            `;
        }
        
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

        // Build the main HTML for the new comment (4-row layout)
        const newCommentHTML = `
            <div class="comment mb-3 my-comment" 
                id="comment-${data.comment_id}" 
                data-comment-id="${data.comment_id}"
                data-level="${data.parent_comment_id ? 1 : 0}">
            
            <!-- Row 1: Top (User Info & More Actions) -->
            <div class="my-comment-top d-flex justify-content-between align-items-center">
                <div class="my-comment-user-info">
                <strong>${data.username}</strong>
                <span class="comment-separator"> · </span>
                <span class="my-comment-date">${data.created_at}</span>
                </div>
                ${dropdownHTML}
            </div>

            <!-- Row 2: Comment Body -->
            <div class="my-comment-body">
                <p>${data.content}</p>
            </div>

            <!-- Row 3: Voting & Reply Buttons -->
            ${
                data.is_authenticated
                ? `
                    <div class="my-comment-actions d-flex align-items-center">
                    <div class="my-vote-section me-3">
                        <button class="btn btn-sm btn-outline-success vote-btn" 
                                data-action="upvote" 
                                data-comment-id="${data.comment_id}">👍</button>
                        <span class="upvote-count" id="upvote-count-${data.comment_id}">0</span>
                        <button class="btn btn-sm btn-outline-danger vote-btn" 
                                data-action="downvote" 
                                data-comment-id="${data.comment_id}">👎</button>
                        <span class="downvote-count" id="downvote-count-${data.comment_id}">0</span>
                    </div>
                    <div class="my-reply-section">
                        <button class="btn btn-sm btn-outline-primary reply-btn" 
                                data-parent-id="${data.comment_id}">Reply</button>
                    </div>
                    </div>
                `
                : ``
        }

        <!-- Row 4: Toggle Replies & Replies Container -->
        <div class="my-comment-toggle">
            <button class="btn btn-link toggle-replies">Hide Replies</button>
        </div>
        <div class="replies"></div>
        </div>
    `;

    // Insert the new comment into the DOM
    const parentRepliesContainer = data.parent_comment_id
        ? document.querySelector(`#comment-${data.parent_comment_id} .replies`)
        : document.getElementById("comments-list");

    if (parentRepliesContainer) {
        // Insert at the top if newest sort, else append
        if (data.parent_comment_id) {
        parentRepliesContainer.insertAdjacentHTML("beforeend", newCommentHTML);
        } else {
        if (sortOrder === "newest") {
            parentRepliesContainer.insertAdjacentHTML("afterbegin", newCommentHTML);
        } else {
            parentRepliesContainer.insertAdjacentHTML("beforeend", newCommentHTML);
        }
        }
    }

    // Re-apply indentation logic
    updateIndentation();
    }

    // ------------------------------------------------------
    // 12) Toggle Replies
    // ------------------------------------------------------
    function toggleReplies(button) {
        const repliesContainer = button.parentElement.nextElementSibling;
        if (!repliesContainer) return;
    
        if (repliesContainer.style.display === "none") {
            repliesContainer.style.display = "block";
            button.textContent = "Hide Replies";
        } else {
            repliesContainer.style.display = "none";
            button.textContent = "Show More Replies";
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
