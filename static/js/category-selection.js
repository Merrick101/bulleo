document.addEventListener("DOMContentLoaded", function () {
    const cards = document.querySelectorAll('.category-card');
    const clearBtn = document.getElementById('clear-selection');
    const hiddenInput = document.getElementById('selected-categories');
  
    // Update hidden input with a comma-separated list of selected category IDs
    function updateHiddenInput() {
      const selectedCards = document.querySelectorAll('.category-card.selected');
      const selectedIds = Array.from(selectedCards).map(card => card.getAttribute('data-id'));
      hiddenInput.value = selectedIds.join(',');
    }
  
    // Toggle selected class on each card when clicked
    cards.forEach(function (card) {
      card.addEventListener("click", function () {
        card.classList.toggle("selected");
        updateHiddenInput();
      });
    });
  
    // Clear all selections when clear button is clicked
    clearBtn.addEventListener("click", function () {
      cards.forEach(function (card) {
        card.classList.remove("selected");
      });
      updateHiddenInput();
    });
  });
  