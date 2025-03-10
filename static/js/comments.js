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

    // Event delegation for vote, reply, report, edit, and delete
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
                reportComment(commentId, event.target);
            } else if (event.target.classList.contains("edit-btn")) {
                const commentId = event.target.dataset.commentId;
                showEditForm(commentId);
            } else if (event.target.classList.contains("delete-btn")) {
                const commentId = event.target.dataset.commentId;
                if (confirm("Are you sure you want to delete this comment?")) {
                    deleteComment(commentId);
                }
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

    // 2) Reply
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
            replyContainer.innerHTML = '';
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
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                renderNewComment(data);
                form.reset();
                updateCommentCount();
            } else {
                alert("Failed to submit reply.");
            }
        })
        .catch(function(error) {
            console.error("Error submitting reply:", error);
        })
        .finally(() => {
            submitButton.disabled = false;
        });
    }

    // 3) Report
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

    // 4) Edit
    function showEditForm(commentId) {
        const commentDiv = document.querySelector(`#comment-${commentId}`);
        if (!commentDiv) return;

        // Get the existing content from the <p> tag
        const contentParagraph = commentDiv.querySelector("p:nth-of-type(2)"); // second <p> inside
        if (!contentParagraph) return;

        const oldContent = contentParagraph.textContent.trim();

        // Create an inline form
        const editFormHTML = `
            <form class="edit-form">
                <textarea name="content" rows="3" required>${oldContent}</textarea>
                <button type="submit" class="btn btn-primary">Save</button>
                <button type="button" class="btn btn-secondary cancel-edit">Cancel</button>
            </form>
        `;
        // Replace the content with the form
        contentParagraph.innerHTML = editFormHTML;

        // Attach event listeners
        const editForm = contentParagraph.querySelector(".edit-form");
        const cancelEditButton = contentParagraph.querySelector(".cancel-edit");

        editForm.addEventListener("submit", function(e) {
            e.preventDefault();
            submitEditForm(commentId, editForm);
        });

        cancelEditButton.addEventListener("click", function() {
            // restore original text if canceled
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
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update the comment content on the page
                const commentDiv = document.querySelector(`#comment-${data.comment_id}`);
                const contentParagraph = commentDiv.querySelector("p:nth-of-type(2)");
                contentParagraph.textContent = data.updated_content;
            } else {
                alert("Failed to edit comment. " + (data.error || ""));
            }
        })
        .catch(error => console.error("Error editing comment:", error))
        .finally(() => {
            submitButton.disabled = false;
        });
    }

    // 5) Delete
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
                // Remove the comment from the DOM
                const commentDiv = document.getElementById(`comment-${data.comment_id}`);
                if (commentDiv) {
                    commentDiv.remove();
                }
            } else {
                alert("Failed to delete the comment.");
            }
        })
        .catch(err => console.error("Error deleting comment:", err));
    }

    // 6) Update Comment Count
    function updateCommentCount() {
        const commentCount = document.getElementById("comment-count");
        if (commentCount) {
            const currentCount = parseInt(commentCount.textContent, 10);
            commentCount.textContent = currentCount + 1;
        }
    }

    // 7) Get CSRF Token
    function getCSRFToken() {
        const cookie = document.cookie.split("; ").find(row => row.startsWith("csrftoken="));
        return cookie ? cookie.split("=")[1] : "";
    }

    // 8) Handle main comment form submission via AJAX
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

    // 9) Render new comment after successful submission
    function renderNewComment(data) {
        const commentList = document.getElementById("comments-list");
        const newCommentHTML = `
            <div class="comment" id="comment-${data.comment_id}" data-comment-id="${data.comment_id}">
                <p><strong>${data.username}</strong> - ${data.created_at}</p>
                <p>${data.content}</p>
                <button class="btn btn-sm btn-outline-success vote-btn" data-action="upvote" data-comment-id="${data.comment_id}">👍</button>
                <span class="upvote-count" id="upvote-count-${data.comment_id}">0</span>
                <button class="btn btn-sm btn-outline-danger vote-btn" data-action="downvote" data-comment-id="${data.comment_id}">👎</button>
                <span class="downvote-count" id="downvote-count-${data.comment_id}">0</span>
                <button class="btn btn-sm btn-outline-primary reply-btn" data-parent-id="${data.comment_id}">Reply</button>
                <button class="btn btn-sm btn-outline-warning edit-btn" data-comment-id="${data.comment_id}">Edit</button>
                <button class="btn btn-sm btn-outline-danger delete-btn" data-comment-id="${data.comment_id}">Delete</button>
                <button class="btn btn-sm btn-outline-danger report-btn" data-comment-id="${data.comment_id}">Report</button>
            </div>
        `;
        commentList.insertAdjacentHTML("beforeend", newCommentHTML);
    }
});
