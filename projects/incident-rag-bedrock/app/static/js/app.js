(() => {
  const MIN_LEN = 3;
  const MAX_LEN = 500;

  const STOP = new Set([
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "for", "with",
    "is", "are", "was", "were", "be", "been", "being", "it", "this", "that",
    "what", "who", "when", "where", "why", "how", "which", "about",
  ]);

  function tokenize(text) {
    return text
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, " ")
      .split(/\s+/)
      .filter((t) => t.length > 1 && !STOP.has(t));
  }

  function validateQuestion(text) {
    const trimmed = (text || "").trim();
    if (!trimmed) return "Please enter a question.";
    if (trimmed.length < MIN_LEN) return "Type a question with at least 3 characters.";
    if (trimmed.length > MAX_LEN) return `Question too long (${trimmed.length}/${MAX_LEN}).`;
    if (tokenize(trimmed).length === 0) return "Your question has no searchable keywords. Try rephrasing.";
    return null;
  }

  function bindCharCounter(inputId, counterId) {
    const input = document.getElementById(inputId);
    const counter = document.getElementById(counterId);
    if (!input || !counter) return;
    const update = () => {
      counter.textContent = `${input.value.length}/${MAX_LEN}`;
    };
    input.addEventListener("input", update);
    update();
  }

  function bindClientValidation(formId, inputId) {
    const form = document.getElementById(formId);
    const input = document.getElementById(inputId);
    if (!form || !input) return;
    form.addEventListener("submit", (event) => {
      const err = validateQuestion(input.value);
      if (err) {
        event.preventDefault();
        alert(err);
      }
    });
  }

  function bindAlertPicker() {
    const list = document.getElementById("alert-list");
    if (!list) return;
    const alertIdInput = document.getElementById("workflow-alert-id");
    const questionInput = document.getElementById("workflow-question");
    list.addEventListener("click", (event) => {
      const btn = event.target.closest(".alert-item");
      if (!btn) return;
      list.querySelectorAll(".alert-item").forEach((el) => el.classList.remove("is-active"));
      btn.classList.add("is-active");
      if (alertIdInput) alertIdInput.value = btn.dataset.alertId || "";
      if (questionInput) questionInput.value = btn.dataset.question || "";
    });
  }

  function bindArchitecture() {
    const blocks = document.querySelectorAll("[data-arch-block]");
    const detail = document.getElementById("arch-detail");
    if (!blocks.length || !detail) return;
    blocks.forEach((block) => {
      block.addEventListener("click", () => {
        blocks.forEach((b) => b.classList.remove("is-active"));
        block.classList.add("is-active");
        const key = block.dataset.archBlock;
        detail.querySelectorAll("[data-arch-panel]").forEach((panel) => {
          panel.hidden = panel.dataset.archPanel !== key;
        });
      });
    });
  }

  function bindWorkflowStages() {
    document.body.addEventListener("htmx:beforeRequest", (event) => {
      const elt = event.detail.elt;
      if (!elt || elt.id !== "workflow-form") return;
      document.querySelectorAll(".stage-pill").forEach((pill, idx) => {
        pill.classList.toggle("is-active", idx === 0);
      });
    });
    document.body.addEventListener("htmx:afterSwap", (event) => {
      if (event.detail.target?.id !== "workflow-result") return;
      document.querySelectorAll(".stage-pill").forEach((pill) => pill.classList.add("is-active"));
      updateSessionMetrics();
    });
  }

  function updateSessionMetrics() {
    const savedEl = document.getElementById("session-saved-min");
    const impactEl = document.getElementById("session-saved-impact");
    const active = document.querySelector(".alert-item.is-active");
    if (!active || !savedEl || !impactEl) return;
    const baseline = Number(active.dataset.baselineMin || 0);
    const assisted = Number(active.dataset.assistedMin || 0);
    const impact = Number(active.dataset.impactPerMin || 0);
    const delta = Math.max(0, baseline - assisted);
    if (delta <= 0) return;
    const prevMin = Number(localStorage.getItem("iiq_saved_min") || 0);
    const prevImpact = Number(localStorage.getItem("iiq_saved_impact") || 0);
    const nextMin = prevMin + delta;
    const nextImpact = prevImpact + delta * impact;
    localStorage.setItem("iiq_saved_min", String(nextMin));
    localStorage.setItem("iiq_saved_impact", String(nextImpact));
    savedEl.textContent = String(nextMin);
    impactEl.textContent = `$${nextImpact.toLocaleString()}`;
  }

  function restoreSessionMetrics() {
    const savedEl = document.getElementById("session-saved-min");
    const impactEl = document.getElementById("session-saved-impact");
    if (savedEl) savedEl.textContent = localStorage.getItem("iiq_saved_min") || "0";
    if (impactEl) {
      const val = Number(localStorage.getItem("iiq_saved_impact") || 0);
      impactEl.textContent = `$${val.toLocaleString()}`;
    }
  }

  function bindHtmxErrors() {
    document.body.addEventListener("htmx:responseError", () => {
      const targets = ["answer", "workflow-result"];
      targets.forEach((id) => {
        const el = document.getElementById(id);
        if (!el || el.innerHTML.trim()) return;
        el.innerHTML =
          '<article class="answer-card error"><header class="answer-header"><span class="badge badge-error">⚠ Error</span></header><p class="answer-body">Service unavailable. Check that the app is running and try again.</p></article>';
      });
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    bindCharCounter("question", "char-count");
    bindClientValidation("ask-form", "question");
    bindClientValidation("workflow-form", "workflow-question");
    bindAlertPicker();
    bindArchitecture();
    bindWorkflowStages();
    restoreSessionMetrics();
    bindHtmxErrors();
  });
})();
