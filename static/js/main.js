// Freebase — search + sidebar filter + mobile toggle
(function () {
  const search = document.getElementById("search");
  const grid = document.getElementById("grid");
  const empty = document.getElementById("empty");
  const sidebar = document.getElementById("sidebar");
  const sidebarToggle = document.getElementById("sidebar-toggle");
  const sidebarClose = document.getElementById("sidebar-close");
  const cards = Array.from(grid.querySelectorAll(".card"));

  let activeCat = "All";
  let query = "";

  function apply() {
    let visible = 0;
    cards.forEach((card) => {
      const cat = card.dataset.category || "";
      const categories = cat.split(',');
      const haystack = `${card.dataset.name} ${card.dataset.desc}`;
      
      const matchCat = activeCat === "All" || categories.includes(activeCat);
      const matchQuery = !query || haystack.includes(query);
      const show = matchCat && matchQuery;
      
      card.classList.toggle("hidden", !show);
      if (show) visible++;
    });
    empty.hidden = visible > 0;
  }

  // Search
  search.addEventListener("input", (e) => {
    query = e.target.value.trim().toLowerCase();
    apply();
  });

  // Sidebar Filter
  sidebar.addEventListener("click", (e) => {
    const btn = e.target.closest(".side-chip");
    if (!btn) return;
    
    sidebar.querySelectorAll(".side-chip").forEach((c) => c.classList.remove("active"));
    btn.classList.add("active");
    activeCat = btn.dataset.cat;
    apply();

    // Close sidebar on mobile after selecting a category
    if (window.innerWidth <= 1024) {
      sidebar.classList.remove("open");
    }
  });

  // Mobile Toggle
  if (sidebarToggle) {
    sidebarToggle.addEventListener("click", () => {
      sidebar.classList.add("open");
    });
  }
  if (sidebarClose) {
    sidebarClose.addEventListener("click", () => {
      sidebar.classList.remove("open");
    });
  }

  // ⌘K / Ctrl+K to focus search
  document.addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      search.focus();
    }
  });
})();
