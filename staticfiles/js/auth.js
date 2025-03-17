document.addEventListener('DOMContentLoaded', function () {
  const toggleIcons = document.querySelectorAll('.toggle-password');
  toggleIcons.forEach(function(icon) {
    // Set the default icon to eye-slash (indicating the password is hidden)
    icon.innerHTML = '<i class="fas fa-eye-slash"></i>';
    icon.addEventListener('click', function() {
      const targetSelector = this.getAttribute('data-target');
      const passwordField = document.querySelector(targetSelector);
      if (passwordField) {
        if (passwordField.type === 'password') {
          // Change to text and update icon to eye (password is now visible)
          passwordField.type = 'text';
          this.innerHTML = '<i class="fas fa-eye"></i>';
        } else {
          // Change back to password and update icon to eye-slash
          passwordField.type = 'password';
          this.innerHTML = '<i class="fas fa-eye-slash"></i>';
        }
      }
    });
  });
});
