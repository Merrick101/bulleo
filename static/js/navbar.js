document.addEventListener("DOMContentLoaded", function () {
  // Menu Toggle => Offcanvas
  const menuToggle = document.getElementById("menuToggle");
  const offcanvasEl = document.getElementById("mainMenuOffcanvas");

  if (menuToggle && offcanvasEl) {
    menuToggle.addEventListener("click", function () {
      // Show the offcanvas using Bootstrap's JS API
      let offcanvas = new bootstrap.Offcanvas(offcanvasEl);
      offcanvas.show();
    });
  }

  // Search Toggle => Inline Search Field
  const searchToggle = document.getElementById("searchToggle");
  const searchClose = document.getElementById("searchClose");
  const searchForm = document.getElementById("searchForm");

  if (searchToggle && searchClose && searchForm) {
    // When the search icon is clicked, show the search form and the close icon, hide the search icon.
    searchToggle.addEventListener("click", function () {
      searchForm.classList.remove("d-none");
      searchToggle.classList.add("d-none");
      searchClose.classList.remove("d-none");
      // Focus on the search input after it expands.
      searchForm.querySelector("input[type='search']").focus();
    });

    // When the close icon is clicked, hide the search form and the close icon, show the search icon.
    searchClose.addEventListener("click", function () {
      searchForm.classList.add("d-none");
      searchToggle.classList.remove("d-none");
      searchClose.classList.add("d-none");
    });
  }
});
