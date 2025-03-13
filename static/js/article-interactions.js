document.addEventListener('DOMContentLoaded', function() {
  // Function to get a cookie by name (to retrieve the CSRF token)
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Check if this cookie string begins with the name we want.
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  const csrftoken = getCookie('csrftoken');

  // Handle Like Button Clicks
  document.querySelectorAll('.like-btn').forEach(function(button) {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      const articleId = this.dataset.articleId; // Ensure your button has data-article-id attribute
      const url = `/articles/${articleId}/toggle_like/`; // Adjust URL if needed

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
          // Update UI: change icon/color, update like count
          this.innerHTML = `<i class="fas fa-thumbs-up"></i> ${data.likes_count}`;
        } else {
          console.error('Error toggling like:', data.error);
        }
      })
      .catch(error => console.error('Error:', error));
    });
  });

  // Handle Save Button Clicks
  document.querySelectorAll('.save-btn').forEach(function(button) {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      const articleId = this.dataset.articleId;
      const url = `/articles/${articleId}/toggle_save/`; // Adjust URL if needed

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
          // Update UI: change icon/color, update save count
          this.innerHTML = `<i class="fas fa-bookmark"></i> ${data.saves_count}`;
        } else {
          console.error('Error toggling save:', data.error);
        }
      })
      .catch(error => console.error('Error:', error));
    });
  });
});
