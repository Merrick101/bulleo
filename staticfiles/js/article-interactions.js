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
    var bsToast = new bootstrap.Toast(toast, { delay: 3000 });
    bsToast.show();

    toast.addEventListener('hidden.bs.toast', function () {
      toast.remove();
    });
  }

  // === Event Listeners for Article Card Buttons ===
  document.querySelectorAll('.like-btn').forEach(function(button) {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      const articleId = this.dataset.articleId;
      const url = `/news/articles/${articleId}/toggle_like/`; // Ensure leading slash
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
          this.innerHTML = `<i class="fas fa-thumbs-up"></i> ${data.likes_count}`;
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

  document.querySelectorAll('.save-btn').forEach(function(button) {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      const articleId = this.dataset.articleId;
      const url = `/news/articles/${articleId}/toggle_save/`; // Ensure leading slash
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

  // === Event Listeners for Article Detail Page Buttons (Unique Classes) ===
  document.querySelectorAll('.detail-like-btn').forEach(function(button) {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      const articleId = this.dataset.articleId;
      const url = `/news/articles/${articleId}/toggle_like/`; // Must match URL pattern
      fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'Content-Type': 'application/json'
        }
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          this.innerHTML = `<i class="fas fa-thumbs-up"></i> Like (${data.likes_count})`;
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

  document.querySelectorAll('.detail-save-btn').forEach(function(button) {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      const articleId = this.dataset.articleId;
      const url = `/news/articles/${articleId}/toggle_save/`; // Must match URL pattern
      fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'Content-Type': 'application/json'
        }
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          this.innerHTML = `<i class="fas fa-bookmark"></i> Save (${data.saves_count})`;
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
