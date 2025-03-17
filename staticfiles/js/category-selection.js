document.addEventListener("DOMContentLoaded", () => {
  const cards = document.querySelectorAll('.category-card');
  const clearBtn = document.getElementById('clear-selection');
  const hiddenInput = document.getElementById('selected-categories');
  const skipBtn = document.getElementById('skip-selection');

  // Update hidden input with a comma-separated list of selected category IDs
  const updateHiddenInput = () => {
    const selectedIds = Array.from(document.querySelectorAll('.category-card.selected'))
      .map(card => card.getAttribute('data-id'));
    hiddenInput.value = selectedIds.join(',');
  };

  // Toggle selected class on each card when clicked
  cards.forEach(card => {
    card.addEventListener("click", () => {
      card.classList.toggle("selected");
      updateHiddenInput();
    });
  });

  // Clear all selections when the clear button is clicked
  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      cards.forEach(card => card.classList.remove("selected"));
      updateHiddenInput();
    });
  }

  // If a skip button exists, redirect to the designated page (here, the homepage)
  if (skipBtn) {
    skipBtn.addEventListener("click", () => {
      window.location.href = '/';
    });
  }
});
