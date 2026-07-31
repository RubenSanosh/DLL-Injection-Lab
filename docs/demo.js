"use strict";

const SCENARIOS = {
  classic: {
    flowId: "classic-dll-injection-001",
    actorPid: 4100,
    targetPid: 4200,
    module: "synthetic://lab/telemetry-demo.dll",
    events: [
      ["cross_process_handle_open", "Cross-process handle", "Actor requests access to a different target"],
      ["remote_memory_allocation", "Remote allocation", "Target-side memory region is reserved"],
      ["remote_memory_write", "Remote write", "Fictional module path is staged"],
      ["remote_thread_start", "Remote thread", "Cross-process execution signal is emitted"],
      ["image_load", "Module image load", "Target records the expected synthetic module"],
    ],
  },
  cooperative: {
    flowId: "cooperative-plugin-001",
    actorPid: 4300,
    targetPid: 4300,
    module: "synthetic://lab/approved-plugin.dll",
    events: [
      ["user_approval", "User approval", "Fictional user approves a local plug-in"],
      ["self_module_load_requested", "Self-load request", "Host requests a module in its own process"],
      ["image_load", "Module image load", "Host records the approved plug-in image"],
    ],
  },
};

let currentScenario = "classic";
let enabledEvents = new Set(SCENARIOS.classic.events.map((event) => event[0]));

const chain = document.querySelector("#event-chain");
const eventCount = document.querySelector("#event-count");
const resultCard = document.querySelector("#result-card");
const resultIcon = document.querySelector("#result-icon");
const resultKicker = document.querySelector("#result-kicker");
const resultTitle = document.querySelector("#result-title");
const resultCopy = document.querySelector("#result-copy");
const evidenceList = document.querySelector("#evidence-list");
const jsonToggle = document.querySelector("#json-toggle");
const jsonOutput = document.querySelector("#json-output");

function escapeText(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function activeEvents() {
  return SCENARIOS[currentScenario].events.filter((event) => enabledEvents.has(event[0]));
}

function hasFinding() {
  const scenario = SCENARIOS[currentScenario];
  return (
    currentScenario === "classic" &&
    scenario.actorPid !== scenario.targetPid &&
    scenario.events.every((event) => enabledEvents.has(event[0]))
  );
}

function eventRecords() {
  const scenario = SCENARIOS[currentScenario];
  return activeEvents().map((event) => ({
    schema_version: "1.0.0",
    scenario: currentScenario,
    flow_id: scenario.flowId,
    tick: scenario.events.findIndex((candidate) => candidate[0] === event[0]) + 1,
    actor_pid: scenario.actorPid,
    target_pid: scenario.targetPid,
    action: event[0],
    module: scenario.module,
    synthetic: true,
  }));
}

function renderChain() {
  const scenario = SCENARIOS[currentScenario];
  chain.innerHTML = scenario.events
    .map((event, index) => {
      const enabled = enabledEvents.has(event[0]);
      return `
        <li>
          <button
            type="button"
            class="event-button${enabled ? "" : " disabled"}"
            data-action="${escapeText(event[0])}"
            aria-pressed="${enabled}"
            aria-label="${enabled ? "Remove" : "Restore"} event ${index + 1}: ${escapeText(event[1])}"
          >
            <span class="event-number">0${index + 1}</span>
            <span class="event-label">
              <strong>${escapeText(event[1])}</strong>
              <span>${escapeText(event[2])}</span>
            </span>
            <span class="event-state">${enabled ? "ACTIVE" : "REMOVED"}</span>
          </button>
        </li>`;
    })
    .join("");

  const active = activeEvents().length;
  eventCount.textContent = `${active} / ${scenario.events.length} active`;
}

function renderResult() {
  const scenario = SCENARIOS[currentScenario];
  const finding = hasFinding();
  resultCard.classList.toggle("finding", finding);
  resultCard.classList.toggle("clear", !finding);
  resultIcon.textContent = finding ? "HIGH" : "CLEAR";

  if (finding) {
    resultKicker.textContent = "HIGH CONFIDENCE";
    resultTitle.textContent = "Synthetic sequence detected";
    resultCopy.textContent = "The complete ordered chain was correlated inside one fictional process flow.";
  } else if (currentScenario === "cooperative") {
    resultKicker.textContent = "CLEAN CONTROL";
    resultTitle.textContent = "No cross-process finding";
    resultCopy.textContent = "Actor and target are the same fictional process, so the detector correctly stays quiet.";
  } else {
    resultKicker.textContent = "CHAIN INCOMPLETE";
    resultTitle.textContent = "No correlated finding";
    resultCopy.textContent = "At least one required event is missing. Restore the full ordered chain to trigger the rule.";
  }

  evidenceList.innerHTML = `
    <div><dt>Technique</dt><dd>${finding ? "T1055.001" : "not assigned"}</dd></div>
    <div><dt>Flow</dt><dd>${escapeText(scenario.flowId)}</dd></div>
    <div><dt>Actor / target</dt><dd>${scenario.actorPid} / ${scenario.targetPid}</dd></div>
    <div><dt>Module</dt><dd>${escapeText(scenario.module)}</dd></div>`;

  jsonOutput.textContent = JSON.stringify(
    {
      mode: "synthetic-event-only",
      finding_count: finding ? 1 : 0,
      events: eventRecords(),
    },
    null,
    2,
  );
}

function render() {
  renderChain();
  renderResult();
}

chain.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const action = button.dataset.action;
  if (enabledEvents.has(action)) enabledEvents.delete(action);
  else enabledEvents.add(action);
  render();
});

document.querySelectorAll("[data-scenario]").forEach((button) => {
  button.addEventListener("click", () => {
    currentScenario = button.dataset.scenario;
    enabledEvents = new Set(SCENARIOS[currentScenario].events.map((event) => event[0]));
    document.querySelectorAll("[data-scenario]").forEach((candidate) => {
      const active = candidate === button;
      candidate.classList.toggle("active", active);
      candidate.setAttribute("aria-pressed", String(active));
    });
    render();
  });
});

document.querySelector("#reset-events").addEventListener("click", () => {
  enabledEvents = new Set(SCENARIOS[currentScenario].events.map((event) => event[0]));
  render();
});

jsonToggle.addEventListener("click", () => {
  const expanded = jsonToggle.getAttribute("aria-expanded") === "true";
  jsonToggle.setAttribute("aria-expanded", String(!expanded));
  jsonToggle.textContent = expanded ? "View JSON evidence" : "Hide JSON evidence";
  jsonOutput.hidden = expanded;
});

render();
