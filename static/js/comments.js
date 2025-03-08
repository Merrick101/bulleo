document.addEventListener("DOMContentLoaded", function () {
    console.log("comments.js loaded successfully!");

    // Sorting function
    const sortDropdown = document.getElementById("sort-comments");
    if (sortDropdown) {
        sortDropdown.addEventListener("change", function () {
            window.location.href = "?sort=" + this.value;
        });
    }

    // Get the article_id from the DOM
    const articleDetail = document.querySelector('.article-detail');
    const article_id = articleDetail ? articleDetail.getAttribute('data-article-id') : null;

    // Handle Comment Voting (Upvote/Downvote)
    document.getElementById("comments-list").addEventListener("click", function (event) {
        if (event.target.classList.contains("vote-btn")) {
            const action = event.target.dataset.action;
            const commentId = event.target.dataset.commentId;
            voteComment(commentId, action, event.target);
        } else if (event.target.classList.contains("reply-btn")) {
            const parentId = event.target.dataset.parentId;
            showReplyForm(parentId);  // Show reply form
        }
    });

    // Show the reply form
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
        const replyContainer = parentComment.querySelector(".replies");
        if (!replyContainer) {
            const newReplyContainer = document.createElement("div");
            newReplyContainer.classList.add("replies");
            parentComment.appendChild(newReplyContainer);
        }
        parentComment.querySelector(".replies").innerHTML = replyFormHTML;

        // Handle reply form submission
        const replyForm = parentComment.querySelector(".reply-form");
        replyForm.addEventListener("submit", function (e) {
            e.preventDefault();
            submitReply(replyForm, parentId);
        });

        // Handle cancel reply
        const cancelButton = parentComment.querySelector(".cancel-reply");
        cancelButton.addEventListener("click", function () {
            parentComment.querySelector(".replies").innerHTML = '';
        });
    }

    // Submit Reply via AJAX
    function submitReply(form, parentId) {
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true;

        const formData = new FormData(form);
        formData.append("parent_comment_id", parentId);
        
        fetch(`/news/comment/${article_id}/reply/`, {  // Ensure this URL exists in your Django URLs
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

    // AJAX for Comment Voting (Upvote/Downvote)
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
                // Update vote counts dynamically
                document.querySelector(`#upvote-count-${commentId}`).textContent = data.upvotes;
                document.querySelector(`#downvote-count-${commentId}`).textContent = data.downvotes;
    
                // Disable the vote buttons after voting
                button.disabled = true;
            } else {
                console.error("Failed to vote");
            }
        })
        .catch(err => console.error("Error with voting:", err));
    }
    
    // Helper Functions
    function updateCommentCount() {
        const commentCount = document.getElementById("comment-count");
        if (commentCount) {
            const currentCount = parseInt(commentCount.textContent);
            commentCount.textContent = currentCount + 1;
        }
    }

    function getCSRFToken() {
        const cookie = document.cookie.split("; ").find(row => row.startsWith("csrftoken="));
        return cookie ? cookie.split("=")[1] : "";
    }

    // Handle comment form submission via AJAX
    const commentForm = document.getElementById("comment-form");
    if (commentForm) {
        commentForm.addEventListener("submit", function (e) {
            e.preventDefault();  // Prevent the default form submission (which would reload the page)
            const formData = new FormData(commentForm);

            // Send the comment data via AJAX
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
                    // Handle success (e.g., update the comment list)
                    renderNewComment(data);  // Add your own function to update the UI
                    commentForm.reset();  // Reset the form after submission
                    updateCommentCount();  // Optionally, update the comment count
                } else {
                    alert("There was an error posting your comment.");
                }
            })
            .catch(error => console.error("Error submitting comment:", error));
        });
    }

    // Render new comment after successful submission
    function renderNewComment(data) {
        const commentList = document.getElementById("comments-list");
        const newCommentHTML = `
            <div class="comment" id="comment-${data.comment_id}" data-comment-id="${data.comment_id}">
                <p><strong>${data.username}</strong> - ${data.created_at}</p>
                <p>${data.content}</p>
                
                <button class="btn btn-sm btn-outline-success vote-btn" data-action="upvote"
                    data-comment-id="${data.comment_id}">👍</button>
                <span class="upvote-count" id="upvote-count-${data.comment_id}">0</span>
                <button class="btn btn-sm btn-outline-danger vote-btn" data-action="downvote"
                    data-comment-id="${data.comment_id}">👎</button>
                <span class="downvote-count" id="downvote-count-${data.comment_id}">0</span>
                
                <button class="btn btn-sm btn-outline-primary reply-btn" data-parent-id="${data.comment_id}">Reply</button>
            </div>
        `;
        commentList.insertAdjacentHTML("beforeend", newCommentHTML);
    }
});
