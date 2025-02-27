// Wait for document to be ready
$(document).ready(function() {

  // Open Login Modal
  $('#open-login-modal').click(function() {
      $('#login-modal').modal('show');
  });

  // Open Signup Modal
  $('#open-signup-modal').click(function() {
      $('#signup-modal').modal('show');
  });

  // Open OAuth popup instead of full redirect
  function openOAuthPopup(url) {
      let popup = window.open(url, "GoogleAuthPopup", "width=500,height=600");

      // Monitor popup close event
      let timer = setInterval(function() {
          if (popup.closed) {
              clearInterval(timer);
              window.location.reload();
          }
      }, 1000);
  }

  // Handle Google login in popup
  $('#google-login-btn').click(function(e) {
      e.preventDefault();
      openOAuthPopup('/accounts/google/login/');
  });

  // Handle Google signup in popup
  $('#google-signup-btn').click(function(e) {
      e.preventDefault();
      openOAuthPopup('/accounts/google/login/');
  });

});
