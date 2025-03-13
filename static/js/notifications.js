document.addEventListener('DOMContentLoaded', function() {
  const notificationsToggle = document.getElementById('notificationsToggle');
  if (notificationsToggle) {
    notificationsToggle.addEventListener('change', function() {
      const enabled = notificationsToggle.checked;
      // Assuming your user URLs are not namespaced in JS; adjust if needed.
      const url = '/users/toggle_notifications/';  
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
          // Optionally display a toast message confirming the update
          console.log("Notifications toggled:", data.notifications_enabled);
        } else {
          console.error("Error toggling notifications:", data.error);
        }
      })
      .catch(error => console.error("Error:", error));
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
