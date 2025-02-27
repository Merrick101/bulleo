// jQuery to trigger modal
$(document).ready(function() {
  // Trigger modal for Google login
  $('#google-login-btn').click(function() {
      $('#google-login-modal').modal('show');
  });

  // Handle Google login redirection inside modal
  $('#google-signin-btn').click(function() {
      window.location.href = '/accounts/google/login/';
      $('#google-login-modal').modal('hide');  // Close modal after redirecting
  });

  // Trigger modal for Google sign-up
  $('#google-signup-btn').click(function() {
      $('#google-signup-modal').modal('show');
  });

  // Handle Google sign-up redirection inside modal
  $('#google-signup-btn').click(function() {
      window.location.href = '/accounts/google/login/';
      $('#google-signup-modal').modal('hide');  // Close modal after redirecting
  });
});
