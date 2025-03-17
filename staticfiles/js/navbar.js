document.addEventListener("DOMContentLoaded", function () {
  console.log("✅ navbar.js loaded");

  // ========== MENU TOGGLE (OFFCANVAS) ==========
  const menuToggle = document.getElementById("menuToggle");
  const offcanvasMenu = document.getElementById("mainMenuOffcanvas");

  if (menuToggle && offcanvasMenu) {
    menuToggle.addEventListener("click", function () {
      // Show the offcanvas menu (Bootstrap's built-in method)
      let offcanvas = new bootstrap.Offcanvas(offcanvasMenu);
      offcanvas.show();
    });
  }

  // ========== SEARCH TOGGLE ==========
  const searchToggle = document.getElementById("searchToggle");
  const searchForm = document.getElementById("searchForm");
  const searchClose = document.getElementById("searchClose");

  if (searchToggle && searchForm && searchClose) {
    // When user clicks the search icon:
    searchToggle.addEventListener("click", function () {
      // Hide the search icon
      searchToggle.classList.add("d-none");
      // Show the search form
      searchForm.classList.remove("d-none");
      // Optionally focus on the input
      const inputEl = searchForm.querySelector("input[name='q']");
      if (inputEl) {
        inputEl.focus();
      }
    });

    // When user clicks the close (X) icon:
    searchClose.addEventListener("click", function (event) {
      event.preventDefault();
      // Hide the search form
      searchForm.classList.add("d-none");
      // Show the search icon again
      searchToggle.classList.remove("d-none");
    });
  }
});
