document.addEventListener("DOMContentLoaded", function () {
    console.log("comments.js loaded successfully!");

    // Sorting function: Redirect to a new URL based on sort selection.
    const sortDropdown = document.getElementById("sort-comments");
    if (sortDropdown) {
        sortDropdown.addEventListener("change", function () {
            window.location.href = "?sort=" + this.value;
        });
    }

    // Retrieve the article ID from the article detail container.
    const articleDetail = document.querySelector('.article-detail');
    const article_id = articleDetail ? articleDetail.getAttribute('data-article-id') : null;

    // Use event delegation on the comments list to handle vote and reply actions.
    const commentsList = document.getElementById("comments-list");
    if (commentsList) {
        commentsList.addEventListener("click", function (event) {
            if (event.target.classList.contains("vote-btn")) {
                const action = event.target.dataset.action;
                const commentId = event.target.dataset.commentId;
                voteComment(commentId, action, event.target);
            } else if (event.target.classList.contains("reply-btn")) {
                const parentId = event.target.dataset.parentId;
                showReplyForm(parentId);  // Show reply form for the comment
            }
        });
    }

    // Function to show the reply form inline for a given parent comment.
    function showReplyForm(parentId) {
        const parentComment = document.querySelector(`#comment-${parentId}`);
        if (!parentComment) return;

        // Define the reply form HTML (no inline styling here; styling should be in CSS)
        const replyFormHTML = `
            <form class="reply-form">
                <textarea name="content" rows="3" placeholder="Write a reply..." required></textarea>
                <button type="submit" class="btn btn-primary">Submit Reply</button>
                <button type="button" class="btn btn-secondary cancel-reply">Cancel</button>
            </form>
        `;

        // Locate or create a container for the reply form inside the parent comment.
        let replyContainer = parentComment.querySelector(".replies");
        if (!replyContainer) {
            replyContainer = document.createElement("div");
            replyContainer.classList.add("replies");
            parentComment.appendChild(replyContainer);
        }
        replyContainer.innerHTML = replyFormHTML;

        // Attach event listener for reply form submission.
        const replyForm = replyContainer.querySelector(".reply-form");
        replyForm.addEventListener("submit", function (e) {
            e.preventDefault();
            submitReply(replyForm, parentId);
        });

        // Attach event listener for canceling the reply.
        const cancelButton = replyContainer.querySelector(".cancel-reply");
        cancelButton.addEventListener("click", function () {
            replyContainer.innerHTML = '';
        });
    }

    // Submit the reply form via AJAX.
    function submitReply(form, parentId) {
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true;

        const formData = new FormData(form);
        formData.append("parent_comment_id", parentId);

        fetch(`/news/comment/${article_id}/reply/`, {  // Ensure this endpoint matches your Django URL
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

    // AJAX for comment voting (upvote/downvote).
    function voteComment(commentId, action, button) {
        const csrfToken = getCSRFToken();

        fetch(`/news/comment/${commentId}/vote/${action}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
                "X-Requested-With": "XMLHttpRequest",
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update vote counts dynamically.
                const upvoteElem = document.querySelector(`#upvote-count-${commentId}`);
                const downvoteElem = document.querySelector(`#downvote-count-${commentId}`);
                if (upvoteElem) upvoteElem.textContent = data.upvotes;
                if (downvoteElem) downvoteElem.textContent = data.downvotes;
                // Optionally, disable or toggle vote buttons.
                button.disabled = true;
            } else {
                console.error("Failed to vote");
            }
        })
        .catch(err => console.error("Error with voting:", err));
    }

    // Helper function: Update the overall comment count.
    function updateCommentCount() {
        const commentCount = document.getElementById("comment-count");
        if (commentCount) {
            const currentCount = parseInt(commentCount.textContent, 10);
            commentCount.textContent = currentCount + 1;
        }
    }

    // Helper function: Retrieve CSRF token from cookies.
    function getCSRFToken() {
        const cookie = document.cookie.split("; ").find(row => row.startsWith("csrftoken="));
        return cookie ? cookie.split("=")[1] : "";
    }

    // Handle main comment form submission via AJAX.
    const commentForm = document.getElementById("comment-form");
    if (commentForm) {
        commentForm.addEventListener("submit", function (e) {
            e.preventDefault();  // Prevent page reload.
            const formData = new FormData(commentForm);

            fetch(commentForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCSRFToken()
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

    // Render new comment after successful submission.
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
            </div>
        `;
        commentList.insertAdjacentHTML("beforeend", newCommentHTML);
    }
});
