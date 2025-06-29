document.addEventListener("DOMContentLoaded", function () {
  console.log("✅ navbar.js loaded");

  // ========== SEARCH TOGGLE ==========
  const searchToggle = document.getElementById("searchToggle");
  const searchForm = document.getElementById("searchForm");
  const searchClose = document.getElementById("searchClose");

  if (searchToggle && searchForm && searchClose) {
    searchToggle.addEventListener("click", function () {
      searchToggle.classList.add("d-none");
      searchForm.classList.remove("d-none");
      const inputEl = searchForm.querySelector("input[name='q']");
      if (inputEl) {
        inputEl.focus();
      }
    });

    searchClose.addEventListener("click", function (event) {
      event.preventDefault();
      searchForm.classList.add("d-none");
      searchToggle.classList.remove("d-none");
    });
  }
});
