document.addEventListener('DOMContentLoaded', function() {
  const notificationsToggle = document.getElementById('notificationsToggle');
  if (notificationsToggle) {
    notificationsToggle.addEventListener('change', function() {
      const enabled = notificationsToggle.checked;
      const url = '/users/toggle_notifications/';

      fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCSRFToken(),
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ enabled: enabled })
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          showToast(data.notifications_enabled ? "Notifications enabled" : "Notifications disabled", "success");
        } else {
          showToast("Error updating notification settings", "danger");
        }
      })
      .catch(() => showToast("Error updating notification settings", "danger"));
    });
  }

  const navbarMarkAll = document.getElementById("navbar-mark-all-read");
  if (navbarMarkAll) {
    navbarMarkAll.addEventListener("click", function () {
      fetch("/users/notifications/mark_all_read/", {
        method: "POST",
        headers: {
          "X-CSRFToken": getCSRFToken(),
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest"
        },
        body: JSON.stringify({})
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          showToast("All notifications marked as read", "success");

          const previewContainer = document.querySelector("#notification-preview");
          if (previewContainer) {
            fetch("/users/notifications/preview/", {
              headers: { "X-Requested-With": "XMLHttpRequest" }
            })
            .then(response => response.json())
            .then(data => {
              if (data.success) previewContainer.innerHTML = data.html;
            });
          }

          const countSpan = document.getElementById("notification-count");
          if (countSpan) countSpan.remove();
        } else {
          showToast("Failed to mark all as read", "danger");
        }
      });
    });
  }

  const markAllReadBtn = document.getElementById('markAllReadBtn');
  if (markAllReadBtn) {
    markAllReadBtn.addEventListener('click', function(e) {
      e.preventDefault();
      fetch('/users/notifications/mark_all_read/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCSRFToken(),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          showToast("All notifications marked as read", "success");
          setTimeout(() => location.reload(), 750);
        } else {
          showToast("Error marking all notifications as read", "danger");
        }
      })
      .catch(() => showToast("Error marking all notifications as read", "danger"));
    });
  }

  const markReadButtons = document.querySelectorAll(".mark-read-btn");
  markReadButtons.forEach(button => {
    button.addEventListener("click", function () {
      const notificationId = this.getAttribute("data-id");
      fetch("/users/notifications/mark_read/", {
        method: "POST",
        headers: {
          "X-CSRFToken": getCSRFToken(),
          "Content-Type": "application/x-www-form-urlencoded",
          "X-Requested-With": "XMLHttpRequest"
        },
        body: `id=${notificationId}`
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          showToast("Notification marked as read", "success");
          button.closest("li").classList.remove("fw-bold");
          button.remove();
        } else {
          showToast("Error marking notification as read", "danger");
        }
      })
      .catch(() => showToast("Error marking notification as read", "danger"));
    });
  });
});
