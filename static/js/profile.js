document.addEventListener('DOMContentLoaded', function() {
  // Preview profile picture upon file selection
  const profilePictureInput = document.getElementById('profile-picture-upload');
  const profilePictureImage = document.getElementById('profile-picture');
  if (profilePictureInput && profilePictureImage) {
      profilePictureInput.addEventListener('change', function() {
          const file = this.files[0];
          if (file) {
              const reader = new FileReader();
              reader.onload = function(e) {
                  profilePictureImage.src = e.target.result;
              };
              reader.readAsDataURL(file);
          }
      });
  }

  // Global Reset & Cancel Buttons for Account Details
  const cancelAccountBtn = document.getElementById('cancel-account-changes-btn');
  const resetAccountBtn = document.getElementById('reset-account-changes-btn');
  if (cancelAccountBtn) {
      cancelAccountBtn.addEventListener('click', function() {
          // Reload the page to cancel unsaved changes
          location.reload();
      });
  }
  if (resetAccountBtn) {
      resetAccountBtn.addEventListener('click', function() {
          // Reload the page to reset the form values
          location.reload();
      });
  }

  // Global Reset & Cancel Buttons for News Feed Preferences
  const cancelPreferencesBtn = document.getElementById('cancel-preferences-btn');
  const resetPreferencesBtn = document.getElementById('reset-preferences-btn');
  if (cancelPreferencesBtn) {
      cancelPreferencesBtn.addEventListener('click', function() {
          location.reload();
      });
  }
  if (resetPreferencesBtn) {
      resetPreferencesBtn.addEventListener('click', function() {
          location.reload();
      });
  }

  // --- AJAX Handlers for "Edit Account Details" Mini-Forms ---

  // Username Update Handler
  const usernameForm = document.getElementById('update-username-form');
  if (usernameForm) {
      usernameForm.addEventListener('submit', function(event) {
          event.preventDefault();
          const formData = new FormData(usernameForm);
          fetch(usernameForm.action, {
              method: 'POST',
              body: formData,
              headers: {
                  'X-Requested-With': 'XMLHttpRequest'
              }
          })
          .then(response => response.json())
          .then(data => {
              const feedback = document.getElementById('username-feedback');
              if (data.success) {
                  feedback.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
              } else {
                  feedback.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
              }
          })
          .catch(error => {
              console.error('Error:', error);
              document.getElementById('username-feedback').innerHTML = `<div class="alert alert-danger">An error occurred. Please try again.</div>`;
          });
      });
  }

  // Email Update Handler
  const emailForm = document.getElementById('update-email-form');
  if (emailForm) {
      emailForm.addEventListener('submit', function(event) {
          event.preventDefault();
          const formData = new FormData(emailForm);
          fetch(emailForm.action, {
              method: 'POST',
              body: formData,
              headers: {
                  'X-Requested-With': 'XMLHttpRequest'
              }
          })
          .then(response => response.json())
          .then(data => {
              const feedback = document.getElementById('email-feedback');
              if (data.success) {
                  feedback.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
              } else {
                  feedback.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
              }
          })
          .catch(error => {
              console.error('Error:', error);
              document.getElementById('email-feedback').innerHTML = `<div class="alert alert-danger">An error occurred. Please try again.</div>`;
          });
      });
  }

  // Password Update Handler
  const passwordForm = document.getElementById('update-password-form');
  if (passwordForm) {
      passwordForm.addEventListener('submit', function(event) {
          event.preventDefault();
          const formData = new FormData(passwordForm);
          fetch(passwordForm.action, {
              method: 'POST',
              body: formData,
              headers: {
                  'X-Requested-With': 'XMLHttpRequest'
              }
          })
          .then(response => response.json())
          .then(data => {
              const feedback = document.getElementById('password-feedback');
              if (data.success) {
                  feedback.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
                  // Optionally, clear the password fields after success
                  passwordForm.reset();
              } else {
                  feedback.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
              }
          })
          .catch(error => {
              console.error('Error:', error);
              document.getElementById('password-feedback').innerHTML = `<div class="alert alert-danger">An error occurred. Please try again.</div>`;
          });
      });
  }

  // Notifications Update Handler
  const notificationsForm = document.getElementById('update-notifications-form');
  if (notificationsForm) {
      notificationsForm.addEventListener('submit', function(event) {
          event.preventDefault();
          const formData = new FormData(notificationsForm);
          fetch(notificationsForm.action, {
              method: 'POST',
              body: formData,
              headers: {
                  'X-Requested-With': 'XMLHttpRequest'
              }
          })
          .then(response => response.json())
          .then(data => {
              const feedback = document.getElementById('notifications-feedback');
              if (data.success) {
                  feedback.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
              } else {
                  feedback.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
              }
          })
          .catch(error => {
              console.error('Error:', error);
              document.getElementById('notifications-feedback').innerHTML = `<div class="alert alert-danger">An error occurred. Please try again.</div>`;
          });
      });
  }
});
