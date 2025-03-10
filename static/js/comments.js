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
            replyContainer.innerHTML = '';  // Remove the reply form
        });
    }    

    function submitReply(form, parentId) {
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true;
    
        const formData = new FormData(form);
        formData.append("parent_comment_id", parentId);
    
        fetch(`/news/article/${article_id}/comment/${parentId}/reply/`, {  // ✅ Ensure `article_id` is included
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
                    }
                }
    
                updateCommentCount();  // Update count
                updateIndentation();   // Update indentation
            } else {
                alert("Failed to submit reply.");
            }
        })
        .catch(error => console.error("Error submitting reply:", error))
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
                const commentDiv = document.getElementById(`comment-${data.comment_id}`);
                if (commentDiv) {
                    commentDiv.querySelector(".comment-body").innerHTML = "<p>[Deleted]</p>";
                }
            } else {
                alert("Failed to delete the comment.");
            }
        })
        .catch(err => console.error("Error deleting comment:", err));
    }    

    // 6) Update Comment Count (Increment)
    function updateCommentCount() {
        const commentCount = document.getElementById("comment-count");
        if (commentCount) {
            const currentCount = parseInt(commentCount.textContent, 10);
            commentCount.textContent = currentCount + 1;
        }
    }

    // Decrement comment count when a comment is deleted
    function decrementCommentCount() {
        const commentCount = document.getElementById("comment-count");
        if (commentCount) {
            const currentCount = parseInt(commentCount.textContent, 10);
            if (currentCount > 0) {
                const newCount = currentCount - 1;
                commentCount.textContent = newCount;
                if (newCount === 0) {
                    insertNoCommentsMsg();
                }
            }
        }
    }

    function insertNoCommentsMsg() {
        const commentList = document.getElementById("comments-list");
        if (commentList) {
            const msg = document.createElement("p");
            msg.id = "no-comments-msg";
            msg.textContent = "No comments yet. Be the first to comment!";
            commentList.appendChild(msg);
        }
    }

    // 7) Get CSRF Token
    function getCSRFToken() {
        const cookie = document.cookie.split("; ").find(row => row.startsWith("csrftoken="));
        return cookie ? cookie.split("=")[1] : "";
    }

    // 8) Main Comment Form Submission via AJAX
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
                    updateIndentation(); // update indentation after new comment
                } else {
                    alert("There was an error posting your comment.");
                }
            })
            .catch(error => console.error("Error submitting comment:", error));
        });
    }

    // 9) Render new comment after successful submission
    function renderNewComment(data) {
        const noCommentsMsg = document.getElementById("no-comments-msg");
        if (noCommentsMsg) {
            noCommentsMsg.remove();  // Remove "No comments yet" message
        }
    
        const newCommentHTML = `
            <div class="comment mb-3" id="comment-${data.comment_id}" data-comment-id="${data.comment_id}" data-level="${data.parent_comment_id ? parseInt(data.parent_level) + 1 : 0}">
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
                    <button class="btn btn-sm btn-outline-success vote-btn" data-action="upvote" data-comment-id="${data.comment_id}">👍</button>
                    <span class="upvote-count" id="upvote-count-${data.comment_id}">0</span>
                    <button class="btn btn-sm btn-outline-danger vote-btn" data-action="downvote" data-comment-id="${data.comment_id}">👎</button>
                    <span class="downvote-count" id="downvote-count-${data.comment_id}">0</span>
                    <button class="btn btn-sm btn-outline-primary reply-btn" data-parent-id="${data.comment_id}">Reply</button>
                </div>
                <div class="replies"></div> <!-- Replies go here -->
            </div>
        `;
    
        if (data.parent_comment_id) {
            const parentComment = document.querySelector(`#comment-${data.parent_comment_id}`);
    
            if (parentComment) {
                let replyContainer = parentComment.querySelector(".replies");
                
                // If .replies doesn't exist, create it
                if (!replyContainer) {
                    replyContainer = document.createElement("div");
                    replyContainer.classList.add("replies");
                    parentComment.appendChild(replyContainer);
                }
                
                replyContainer.insertAdjacentHTML("beforeend", newCommentHTML);
            } else {
                console.error("Parent comment not found in DOM.");
            }
        } else {
            // If it's a top-level comment, append to #comments-list
            document.getElementById("comments-list").insertAdjacentHTML("beforeend", newCommentHTML);
        }
    
        updateIndentation();  // Ensure indentation updates correctly
    }       
    
    // 10) Update indentation dynamically based on data-level
    function updateIndentation() {
        const commentElements = document.querySelectorAll("[data-level]");
        commentElements.forEach(function (elem) {
            const level = elem.getAttribute("data-level");
            // Remove any existing indentation classes that start with "comment-indent-"
            elem.classList.forEach(function(className) {
                if (className.startsWith("comment-indent-")) {
                    elem.classList.remove(className);
                }
            });
            // Add the appropriate indentation class
            elem.classList.add("comment-indent-" + level);
        });
    }

    // Optional: Use MutationObserver to automatically update indentation on DOM changes
    const observer = new MutationObserver(() => {
        updateIndentation();
    });
    const commentsContainer = document.getElementById("comments-list");
    if (commentsContainer) {
        observer.observe(commentsContainer, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ["data-level"]
        });
    }
});
