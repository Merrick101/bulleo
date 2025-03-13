document.addEventListener('DOMContentLoaded', function() {
  // Helper: Get a cookie by name (to retrieve the CSRF token)
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  const csrftoken = getCookie('csrftoken');

  // Helper: Show a toast notification
  function showToast(message) {
    // Create a toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.id = 'toast-container';
      toastContainer.style.position = 'fixed';
      toastContainer.style.bottom = '1rem';
      toastContainer.style.right = '1rem';
      toastContainer.style.zIndex = 1055;
      document.body.appendChild(toastContainer);
    }

    // Create the toast element
    const toast = document.createElement('div');
    toast.className = 'toast align-items-center text-white bg-success border-0';
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.style.minWidth = '200px';
    toast.innerHTML = `
      <div class="d-flex">
        <div class="toast-body">
          ${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    `;
    toastContainer.appendChild(toast);
    // Initialize and show the toast (using Bootstrap Toast)
    var bsToast = new bootstrap.Toast(toast, { delay: 3000 });
    bsToast.show();

    // Remove toast after it hides
    toast.addEventListener('hidden.bs.toast', function () {
      toast.remove();
    });
  }

  // Handle Like Button Clicks
  document.querySelectorAll('.like-btn').forEach(function(button) {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      const articleId = this.dataset.articleId; // Ensure your button has data-article-id attribute
      const url = `news/articles/${articleId}/toggle_like/`; // Adjust URL if needed

      fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // Update the like button count
          this.innerHTML = `<i class="fas fa-thumbs-up"></i> ${data.likes_count}`;
          // Show confirmation toast message
          const message = data.liked ? "Article liked!" : "Article unliked!";
          showToast(message);
        } else {
          console.error('Error toggling like:', data.error);
          showToast("Error processing like action.");
        }
      })
      .catch(error => {
        console.error('Error:', error);
        showToast("Error processing like action.");
      });
    });
  });

  // Handle Save Button Clicks
  document.querySelectorAll('.save-btn').forEach(function(button) {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      const articleId = this.dataset.articleId;
      const url = `news/articles/${articleId}/toggle_save/`; // Adjust URL if needed

      fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          this.innerHTML = `<i class="fas fa-bookmark"></i> ${data.saves_count}`;
          const message = data.saved ? "Article saved!" : "Article unsaved!";
          showToast(message);
        } else {
          console.error('Error toggling save:', data.error);
          showToast("Error processing save action.");
        }
      })
      .catch(error => {
        console.error('Error:', error);
        showToast("Error processing save action.");
      });
    });
  });
});
