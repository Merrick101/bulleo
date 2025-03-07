document.addEventListener("DOMContentLoaded", function () {
    console.log("comments.js loaded successfully!");

    // Sorting function
    const sortDropdown = document.getElementById("sort-comments");
    if (sortDropdown) {
        sortDropdown.addEventListener("change", function () {
            window.location.href = `?sort=${this.value}`;
        });
    }

    // Get the article_id from the DOM
    const articleDetail = document.querySelector('.article-detail');
    const article_id = articleDetail ? articleDetail.getAttribute('data-article-id') : null;

    // AJAX for Comment Submission (Top-Level & Replies)
    document.getElementById("comment-form").addEventListener("submit", function (event) {
        event.preventDefault();
        submitComment(this);
    });

    function submitComment(form) {
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true;  // Disable the submit button to prevent multiple submissions

        const formData = new FormData(form);
        fetch(form.action, {
            method: "POST",
            body: formData,
            headers: { 
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCSRFToken()  // Ensure CSRF token is sent
            }
        })
        .then(response => {
            // Debugging: Check if the response is HTML or JSON
            if (!response.ok) {
                return response.text().then(text => {
                    console.error("Server returned an error page:", text);
                    throw new Error("Server returned an error page.");
                });
            }
            // Attempt to parse the response as JSON
            return response.json().catch(err => {
                console.error("Failed to parse JSON:", err);
                throw new Error("Failed to parse JSON response.");
            });
        })
        .then(data => {
            if (data.success) {
                renderNewComment(data);
                form.reset();
            } else {
                alert("Failed to submit comment.");
            }
        })
        .catch(function(error) {
            console.error("Error submitting comment:", error);
        })
        .finally(() => {
            submitButton.disabled = false;  // Re-enable the submit button after the process
        });
    }       

    function renderNewComment(data) {
        const commentList = document.getElementById("comments-list");
    
        // Check if commentList exists
        if (!commentList) {
            console.error("Element with ID 'comments-list' not found.");
            return; // Exit the function if the element is not found
        }
    
        // Create the new comment element
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
    
        // Check if parentCommentId exists and append to the correct parent
        if (data.parent_comment_id) {
            const parentComment = document.querySelector(`#comment-${data.parent_comment_id}`);
            if (parentComment) {
                let repliesContainer = parentComment.querySelector(".replies");
                if (!repliesContainer) {
                    repliesContainer = document.createElement("div");
                    repliesContainer.classList.add("replies");
                    parentComment.appendChild(repliesContainer);
                }
                repliesContainer.appendChild(newComment);  // Append the new reply to the parent comment's replies section
            } else {
                console.error(`Parent comment with ID ${data.parent_comment_id} not found.`);
            }
        } else {
            commentList.prepend(newComment);  // For top-level comments
        }
    
        // Update comment count
        const commentCount = document.getElementById("comment-count");
        if (commentCount) {
            commentCount.textContent = parseInt(commentCount.textContent) + 1;
        }
    }             

    // Handle Reply Button Clicks
    document.getElementById("comments-list").addEventListener("click", function (event) {
        if (event.target.classList.contains("reply-btn")) {
            const parentId = event.target.dataset.parentId;
            showReplyForm(parentId, event.target);
        }
    });

    function showReplyForm(parentId, replyButton) {
        // Check if reply form already exists
        if (document.querySelector(`#reply-form-${parentId}`)) return;

        // Create reply form
        const replyForm = document.createElement("form");
        replyForm.classList.add("reply-form", "mt-2");
        replyForm.id = `reply-form-${parentId}`;
        replyForm.action = `/news/article/${article_id}/comment/`;  // Ensure this points to the right URL
        replyForm.method = "POST";

        // Add the textarea and the hidden parent_comment_id input dynamically
        replyForm.innerHTML = `
            <textarea name="content" class="form-control" rows="2" required placeholder="Write a reply..."></textarea>
            <input type="hidden" name="parent_comment_id" value="${parentId}">
            <button type="submit" class="btn btn-sm btn-success mt-2">Post Reply</button>
        `;

        // Insert the reply form after the reply button
        replyButton.insertAdjacentElement("afterend", replyForm);

        // Attach an event listener for the reply form submission
        replyForm.addEventListener("submit", function (e) {
            e.preventDefault();
            submitComment(replyForm);  // Submit the reply
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

    // Function to retrieve CSRF token from cookies
    function getCSRFToken() {
        const cookie = document.cookie
            .split("; ")
            .find(row => row.startsWith("csrftoken="));
        return cookie ? cookie.split("=")[1] : "";
    }
});
