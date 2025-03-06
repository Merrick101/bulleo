document.addEventListener("DOMContentLoaded", function () {
    console.log("Comments.js loaded successfully!");

    // Sorting function
    const sortDropdown = document.getElementById("sort-comments");
    if (sortDropdown) {
        sortDropdown.addEventListener("change", function () {
            window.location.href = `?sort=${this.value}`;
        });
    }

    // AJAX for Comment Submission
    const commentForm = document.getElementById("comment-form");
    if (commentForm) {
        commentForm.addEventListener("submit", function (event) {
            event.preventDefault();  // Prevent full-page reload

            const formData = new FormData(commentForm);
            fetch(commentForm.action, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const commentList = document.getElementById("comments-list");
                    const newComment = document.createElement("div");
                    newComment.classList.add("comment", "border", "rounded", "p-3", "my-3");
                    newComment.dataset.commentId = data.comment_id;
                    newComment.innerHTML = `
                        <p><strong>${data.username}</strong> - ${data.created_at}</p>
                        <p>${data.content}</p>
                        <div class="d-flex align-items-center">
                            <button class="btn btn-sm btn-outline-success vote-btn" data-action="upvote">👍</button>
                            <span class="upvote-count" id="upvote-count-${data.comment_id}">0</span>
                            <button class="btn btn-sm btn-outline-danger vote-btn" data-action="downvote">👎</button>
                            <span class="downvote-count" id="downvote-count-${data.comment_id}">0</span>
                        </div>
                    `;
                    commentList.prepend(newComment);

                    document.getElementById("comment-count").textContent++;
                    const noComments = document.getElementById("no-comments");
                    if (noComments) noComments.style.display = "none";

                    commentForm.reset();
                } else {
                    alert("Failed to submit comment.");
                }
            })
            .catch(error => console.error("Error submitting comment:", error));
        });
    }

    // AJAX for Upvote/Downvote
    document.getElementById("comments-list").addEventListener("click", function (event) {
        if (event.target.classList.contains("vote-btn")) {
            const commentDiv = event.target.closest(".comment");
            const commentId = commentDiv.dataset.commentId;
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
                    commentDiv.querySelector(".upvote-count").textContent = data.upvotes;
                    commentDiv.querySelector(".downvote-count").textContent = data.downvotes;
                }
            })
            .catch(error => console.error("Error processing vote:", error));
        }
    });
});

// Helper function to get CSRF token
function getCSRFToken() {
    return document.cookie.split("; ")
        .find(row => row.startsWith("csrftoken="))
        ?.split("=")[1];
}
