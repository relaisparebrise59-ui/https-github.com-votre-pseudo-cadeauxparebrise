(function () {
  "use strict";

  /* Mobile nav toggle */
  var navToggle = document.getElementById("navToggle");
  var mainNav = document.getElementById("main-nav");
  if (navToggle && mainNav) {
    navToggle.addEventListener("click", function () {
      var isOpen = mainNav.classList.toggle("open");
      navToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });
    mainNav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        mainNav.classList.remove("open");
        navToggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* FAQ-style accordions, external links etc. rely on native <details> — nothing to wire up. */

  /* Conversion tracking helper — no-ops until gtag/fbq are actually loaded (see partials/tracking.html) */
  function track(eventName, params) {
    params = params || {};
    if (typeof window.gtag === "function") {
      window.gtag("event", eventName, params);
    }
    if (typeof window.fbq === "function") {
      window.fbq("trackCustom", eventName, params);
    }
  }

  /* Ad-attribution capture (utm_*, gclid, fbclid) so it travels with every lead, on every page */
  function captureAttribution() {
    var keys = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid", "fbclid"];
    var params = new URLSearchParams(window.location.search);
    var data = {};
    var found = false;
    keys.forEach(function (key) {
      var value = params.get(key);
      if (value) {
        data[key] = value;
        found = true;
      }
    });
    if (found) {
      try { sessionStorage.setItem("cpb_attribution", JSON.stringify(data)); } catch (err) {}
    } else {
      try {
        var stored = sessionStorage.getItem("cpb_attribution");
        if (stored) data = JSON.parse(stored);
      } catch (err) {}
    }
    return data;
  }

  var attribution = captureAttribution();
  var PHONE_RE = /^0[1-9][0-9]{8}$/;

  var STEP_NAMES = {
    1: "code_postal",
    2: "vitrage",
    3: "assurance",
    4: "coordonnees",
    loading: "verification_eligibilite",
    success: "confirmation"
  };

  /* Wires up one instance of the multi-step lead form (there can be several per page:
     the homepage hero embed, plus the site-wide modal). Each instance tracks its own
     step state independently. */
  function initQuoteForm(form) {
    var formCard = form.closest(".form-card");
    var steps = Array.prototype.slice.call(form.querySelectorAll(".form-step"));
    var indicators = formCard ? Array.prototype.slice.call(formCard.querySelectorAll(".progress-step")) : [];
    var numberedSteps = steps.filter(function (s) { return !isNaN(Number(s.dataset.step)); });
    var totalSteps = numberedSteps.length;
    var currentStep = 1;
    var formData = { cp: "", vitrage: "", assurance: "", nom: "", tel: "" };

    Object.keys(attribution).forEach(function (key) {
      var field = form.querySelector('[name="' + key + '"]');
      if (field) field.value = attribution[key];
    });
    var pageUrlField = form.querySelector('[name="page_url"]');
    if (pageUrlField) pageUrlField.value = window.location.href;

    function showStep(step) {
      steps.forEach(function (stepEl) {
        stepEl.classList.toggle("active", stepEl.dataset.step == step);
      });
      indicators.forEach(function (ind) {
        var n = Number(ind.dataset.stepIndicator);
        if (step === "loading" || step === "success") {
          ind.classList.add("done");
          ind.classList.remove("active");
        } else {
          ind.classList.toggle("active", n === step);
          ind.classList.toggle("done", n < step);
        }
      });
      currentStep = step;
      track("funnel_step_view", { step_number: typeof step === "number" ? step : 0, step_name: STEP_NAMES[step] || String(step) });
    }

    form.addEventListener("click", function (e) {
      var nextBtn = e.target.closest("[data-next]");
      var prevBtn = e.target.closest("[data-prev]");
      var choiceBtn = e.target.closest(".choice-btn");

      if (choiceBtn) {
        var group = choiceBtn.closest(".choice-grid");
        group.querySelectorAll(".choice-btn").forEach(function (b) {
          b.classList.remove("selected");
        });
        choiceBtn.classList.add("selected");
        if (choiceBtn.dataset.field === "vitrage") {
          formData.vitrage = choiceBtn.dataset.value;
        }
        window.setTimeout(function () {
          if (currentStep < totalSteps) showStep(currentStep + 1);
        }, 200);
        return;
      }

      if (nextBtn) {
        var activeStep = form.querySelector('.form-step[data-step="' + currentStep + '"]');
        var requiredFields = activeStep.querySelectorAll("[required]");
        var valid = true;
        requiredFields.forEach(function (field) {
          if (!field.checkValidity()) {
            field.reportValidity();
            valid = false;
          }
        });
        if (!valid) return;

        if (currentStep === 1) formData.cp = form.querySelector('[name="cp"]').value.trim();
        if (currentStep === 3) formData.assurance = form.querySelector('[name="assurance"]').value;

        if (currentStep < totalSteps) showStep(currentStep + 1);
      }

      if (prevBtn) {
        if (typeof currentStep === "number" && currentStep > 1) showStep(currentStep - 1);
      }
    });

    var telField = form.querySelector('[name="tel"]');
    if (telField) {
      telField.addEventListener("input", function () {
        telField.setCustomValidity("");
      });
    }

    form.addEventListener("submit", function (e) {
      e.preventDefault();

      if (telField) {
        var digitsOnly = telField.value.replace(/[\s.\-]/g, "");
        if (!PHONE_RE.test(digitsOnly)) {
          telField.setCustomValidity("Merci d'indiquer un numéro de téléphone français valide (ex : 06 12 34 56 78).");
        } else {
          telField.setCustomValidity("");
          telField.value = digitsOnly;
        }
      }

      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }

      formData.nom = form.querySelector('[name="nom"]').value.trim();
      formData.tel = telField ? telField.value.trim() : "";

      var loadingText = form.querySelector(".loading-text, #loadingText");
      if (loadingText) {
        loadingText.textContent = formData.assurance
          ? "Vérification de votre éligibilité auprès de " + formData.assurance + "…"
          : "Vérification de votre éligibilité…";
      }

      showStep("loading");

      window.setTimeout(function () {
        form.querySelectorAll('[data-recap="cp"]').forEach(function (el) { el.textContent = formData.cp || "—"; });
        form.querySelectorAll('[data-recap="vitrage"]').forEach(function (el) { el.textContent = formData.vitrage || "—"; });
        form.querySelectorAll('[data-recap="assurance"]').forEach(function (el) { el.textContent = formData.assurance || "—"; });

        showStep("success");

        track("generate_lead", { value: 1, currency: "EUR", vitrage: formData.vitrage, assurance: formData.assurance });
        if (typeof window.fbq === "function") {
          window.fbq("track", "Lead", { value: 1, currency: "EUR" });
        }
      }, 1600);
    });

    showStep(1);
  }

  document.querySelectorAll(".quote-form").forEach(initQuoteForm);

  /* Site-wide tunnel modal — any [data-open-tunnel] element opens it, from any page */
  var tunnelModal = document.getElementById("tunnelModal");
  if (tunnelModal) {
    var openTunnel = function () {
      tunnelModal.classList.add("open");
      tunnelModal.setAttribute("aria-hidden", "false");
      document.body.classList.add("tunnel-lock");
      var firstField = tunnelModal.querySelector("input, select");
      if (firstField) window.setTimeout(function () { firstField.focus(); }, 50);
      track("tunnel_modal_open", {});
    };
    var closeTunnel = function () {
      tunnelModal.classList.remove("open");
      tunnelModal.setAttribute("aria-hidden", "true");
      document.body.classList.remove("tunnel-lock");
    };

    document.addEventListener("click", function (e) {
      if (e.target.closest("[data-open-tunnel]")) {
        e.preventDefault();
        openTunnel();
      }
      if (e.target.closest("[data-close-tunnel]")) {
        closeTunnel();
      }
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && tunnelModal.classList.contains("open")) {
        closeTunnel();
      }
    });

    /* Exit-intent: on desktop, if a visitor never opened the tunnel and moves the
       cursor to leave the viewport upward (toward the tab bar), offer it once per
       session instead of letting them leave without ever seeing the form. */
    var hasOpenedTunnel = false;
    document.addEventListener("click", function (e) {
      if (e.target.closest("[data-open-tunnel]")) hasOpenedTunnel = true;
    });

    var exitIntentEligible = window.matchMedia("(min-width: 900px)").matches;
    try {
      if (sessionStorage.getItem("cpb_exit_intent_shown") === "1") exitIntentEligible = false;
    } catch (err) {}

    if (exitIntentEligible) {
      document.addEventListener("mouseout", function (e) {
        if (!exitIntentEligible || hasOpenedTunnel) return;
        if (e.clientY > 0 || e.relatedTarget) return;
        exitIntentEligible = false;
        try { sessionStorage.setItem("cpb_exit_intent_shown", "1"); } catch (err) {}
        openTunnel();
        track("exit_intent_shown", {});
      });
    }
  }
})();
