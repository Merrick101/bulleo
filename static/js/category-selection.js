document.addEventListener("DOMContentLoaded", function () {
  const categoryOptions = document.querySelectorAll(".category-option input[type='checkbox']");

  categoryOptions.forEach(function(checkbox) {
      checkbox.addEventListener("change", function () {
          // Toggle a "selected" class on the parent div for visual feedback
          if (checkbox.checked) {
              checkbox.parentElement.classList.add("selected");
          } else {
              checkbox.parentElement.classList.remove("selected");
          }
      });
  });
});
