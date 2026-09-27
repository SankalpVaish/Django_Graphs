/* ==========================================================================
   Graphs — interface behaviour
   Every block guards for absent elements so this file runs on all pages.
   ========================================================================== */

(function () {
  "use strict";

  /* ------------------------------------------------------------------
     Chart builder: a histogram takes one axis, everything else takes two
     ------------------------------------------------------------------ */

  var graphSelect = document.querySelector("#graph");
  var yAxisField = document.querySelector("#opt2");

  function syncAxisFields() {
    yAxisField.hidden = graphSelect.value === "histogram";
  }

  if (graphSelect && yAxisField) {
    graphSelect.addEventListener("change", syncAxisFields);
    syncAxisFields();
  }

  /* ------------------------------------------------------------------
     Train/test split slider
     ------------------------------------------------------------------ */

  var splitSlider = document.querySelector("#splitSlider");
  var splitValue = document.querySelector("#splitValue");

  if (splitSlider && splitValue) {
    splitSlider.addEventListener("input", function () {
      splitValue.textContent = splitSlider.value + "%";
    });
  }

  /* ------------------------------------------------------------------
     Scaler selection
     ------------------------------------------------------------------ */

  var scalerCards = document.querySelectorAll("[data-scaler]");
  var selectedScaler = "minmax";

  scalerCards.forEach(function (card) {
    if (card.classList.contains("is-active")) {
      selectedScaler = card.dataset.scaler;
    }

    card.addEventListener("click", function () {
      scalerCards.forEach(function (other) {
        other.classList.remove("is-active");
        other.setAttribute("aria-pressed", "false");
      });

      card.classList.add("is-active");
      card.setAttribute("aria-pressed", "true");
      selectedScaler = card.dataset.scaler;
    });
  });

  /* ------------------------------------------------------------------
     Model picker: carry the chosen split and scaler into the URL
     ------------------------------------------------------------------ */

  document.querySelectorAll("[data-model]").forEach(function (link) {
    link.addEventListener("click", function (event) {
      event.preventDefault();

      var split = splitSlider ? splitSlider.value : 20;
      var target = link.dataset.url.replace(
        "DUMMY",
        encodeURIComponent(link.dataset.model)
      );

      window.location.href =
        target + "?split=" + split + "&scaler=" + selectedScaler;
    });
  });

  /* ------------------------------------------------------------------
     Expand / collapse a grid of small multiples.
     Each button only ever touches the grid it is paired with.
     ------------------------------------------------------------------ */

  document.querySelectorAll("[data-expand]").forEach(function (button) {
    var grid = document.getElementById(button.dataset.expand);

    if (!grid) {
      return;
    }

    var hidden = grid.children.length - 2;

    if (hidden < 1) {
      button.closest(".chart-expand").hidden = true;
      grid.classList.remove("is-collapsed");
      return;
    }

    var label = button.querySelector("[data-expand-label]") || button;
    label.textContent = "Show " + hidden + " more";

    button.addEventListener("click", function () {
      var expanded = grid.classList.toggle("is-collapsed") === false;

      button.setAttribute("aria-expanded", String(expanded));
      label.textContent = expanded ? "Show fewer" : "Show " + hidden + " more";
    });
  });

  /* ------------------------------------------------------------------
     Reveal-on-scroll, once per element
     ------------------------------------------------------------------ */

  var revealTargets = document.querySelectorAll(".reveal");

  if (!("IntersectionObserver" in window)) {
    revealTargets.forEach(function (el) {
      el.classList.add("is-visible");
    });
    return;
  }

  var revealObserver = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) {
          return;
        }

        entry.target.classList.add("is-visible");
        revealObserver.unobserve(entry.target);
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
  );

  revealTargets.forEach(function (el) {
    revealObserver.observe(el);
  });
})();
