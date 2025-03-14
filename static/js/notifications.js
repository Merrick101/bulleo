document.addEventListener('DOMContentLoaded', function() {
  const notificationsToggle = document.getElementById('notificationsToggle');
  if (notificationsToggle) {
    notificationsToggle.addEventListener('change', function() {
      const enabled = notificationsToggle.checked;
      const url = '/users/toggle_notifications/';  // Ensure this URL matches your configuration

      fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ enabled: enabled })
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          console.log("Notifications toggled:", data.notifications_enabled);
          showToast(data.notifications_enabled ? "Notifications enabled" : "Notifications disabled");
        } else {
          console.error("Error toggling notifications:", data.error);
          showToast("Error updating notification settings");
        }
      })
      .catch(error => {
        console.error("Error:", error);
        showToast("Error updating notification settings");
      });
    });
  }

  // Event listener for marking all notifications as read (with automatic page reload)
  const markAllReadBtn = document.getElementById('markAllReadBtn');
  if (markAllReadBtn) {
    markAllReadBtn.addEventListener('click', function(e) {
      e.preventDefault();
      const url = '/users/notifications/mark_all_read/';  // Ensure this URL is correct
      fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          showToast("All notifications marked as read");
          // Reload the page after a short delay to reflect changes
          setTimeout(function() {
            location.reload();
          }, 1000);
        } else {
          console.error("Error marking all notifications as read:", data.error);
          showToast("Error marking all notifications as read");
        }
      })
      .catch(error => {
        console.error("Error:", error);
        showToast("Error marking all notifications as read");
      });
    });
  }
});

// Helper: Get a cookie by name
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

// Helper: Show a toast notification using Bootstrap Toast
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
