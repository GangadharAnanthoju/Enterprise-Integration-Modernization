const state = {
  correlationId: null,
  approvalId: null,
  approvalDecision: null,
};

const elements = {
  conversation: document.querySelector("#conversation"),
  chatForm: document.querySelector("#chat-form"),
  userMessage: document.querySelector("#user-message"),
  executeReady: document.querySelector("#execute-ready"),
  sendButton: document.querySelector("#send-button"),
  healthIndicator: document.querySelector("#health-indicator"),
  healthLabel: document.querySelector("#health-label"),
  runtimeLabel: document.querySelector("#runtime-label"),
  actionStatus: document.querySelector("#action-status"),
  actionDetails: document.querySelector("#action-details"),
  entityList: document.querySelector("#entity-list"),
  resultView: document.querySelector("#result-view"),
  approvalStatus: document.querySelector("#approval-status"),
  approvalSummary: document.querySelector("#approval-summary"),
  approvalForm: document.querySelector("#approval-form"),
  reviewer: document.querySelector("#reviewer"),
  approvalComment: document.querySelector("#approval-comment"),
  approveButton: document.querySelector("#approve-button"),
  rejectButton: document.querySelector("#reject-button"),
  executeButton: document.querySelector("#execute-button"),
  auditList: document.querySelector("#audit-list"),
  refreshAudit: document.querySelector("#refresh-audit"),
  runtimeDetails: document.querySelector("#runtime-details"),
  refreshRuntime: document.querySelector("#refresh-runtime"),
  toast: document.querySelector("#toast"),
};

function apiUrl(path) {
  const uiIndex = window.location.pathname.indexOf("/ui");
  const prefix = uiIndex >= 0 ? window.location.pathname.slice(0, uiIndex) : "";
  return `${prefix}${path}`;
}

async function request(path, options = {}) {
  const response = await fetch(apiUrl(path), {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail || data);
    throw new Error(detail || `Request failed with status ${response.status}`);
  }
  return data;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function badgeClass(status) {
  if (["completed", "approved", "allow", "ready", "ok"].includes(status)) return "success";
  if (["approval_required", "pending", "needs_attention", "require_approval"].includes(status)) return "warning";
  if (["failed", "rejected", "deny", "error"].includes(status)) return "danger";
  return "neutral";
}

function setBadge(element, status) {
  element.textContent = status || "None";
  element.className = `badge ${badgeClass(status)}`;
}

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.classList.add("visible");
  window.setTimeout(() => elements.toast.classList.remove("visible"), 3200);
}

function addMessage(role, message, isError = false) {
  const article = document.createElement("article");
  article.className = `message ${role}${isError ? " error" : ""}`;
  article.innerHTML = `
    <div class="message-label">${role === "user" ? "You" : "Agent"}</div>
    <p>${escapeHtml(message)}</p>
  `;
  elements.conversation.append(article);
  elements.conversation.scrollTop = elements.conversation.scrollHeight;
}

function resultValue(value) {
  if (value === null || value === undefined) return "Not available";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function resultLabel(key) {
  return key
    .replaceAll("_", " ")
    .replace(/([a-z0-9])([A-Z])/g, "$1 $2")
    .replace(/^./, (character) => character.toUpperCase());
}

function addExecutionResult(simulationResult) {
  if (!simulationResult?.result) return;
  const rows = Object.entries(simulationResult.result)
    .map(([key, value]) => `
      <div>
        <dt>${escapeHtml(resultLabel(key))}</dt>
        <dd>${escapeHtml(resultValue(value))}</dd>
      </div>
    `)
    .join("");
  const article = document.createElement("article");
  article.className = "message assistant execution-result";
  article.innerHTML = `
    <div class="message-label">${escapeHtml(resultLabel(simulationResult.tool_name))} result</div>
    <dl>${rows}</dl>
  `;
  elements.conversation.append(article);
  elements.conversation.scrollTop = elements.conversation.scrollHeight;
}

function activateTab(name) {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.tab === name);
  });
  document.querySelectorAll(".tab-panel").forEach((panel) => {
    panel.classList.toggle("active", panel.id === `tab-${name}`);
  });
}

function renderAction(data) {
  state.correlationId = data.correlation_id;
  elements.refreshAudit.disabled = !state.correlationId;
  setBadge(elements.actionStatus, data.status);
  elements.actionDetails.innerHTML = `
    <div><dt>Selected tool</dt><dd>${escapeHtml(data.selected_tool || "None")}</dd></div>
    <div><dt>Risk decision</dt><dd>${escapeHtml(data.risk_decision || "None")}</dd></div>
    <div><dt>Correlation ID</dt><dd>${escapeHtml(data.correlation_id)}</dd></div>
    <div><dt>Tool called</dt><dd>${data.tool_called ? "Yes" : "No"}</dd></div>
  `;
  elements.entityList.innerHTML = Object.entries(data.entities || {})
    .map(([key, value]) => `<span class="entity">${escapeHtml(key)}=${escapeHtml(value)}</span>`)
    .join("");
  elements.resultView.textContent = data.simulation_result
    ? JSON.stringify(data.simulation_result, null, 2)
    : JSON.stringify(data.planned_action || { message: data.message }, null, 2);
}

function resetApproval() {
  state.approvalId = null;
  state.approvalDecision = null;
  setBadge(elements.approvalStatus, "none");
  elements.approvalSummary.textContent = "High-risk requests will appear here.";
  elements.approveButton.disabled = true;
  elements.rejectButton.disabled = true;
  elements.executeButton.disabled = true;
}

function renderApproval(approval) {
  if (!approval) {
    resetApproval();
    return;
  }
  state.approvalId = approval.approval_id;
  state.approvalDecision = null;
  setBadge(elements.approvalStatus, approval.status);
  elements.approvalSummary.textContent =
    `${approval.requested_tool} requires review. ${approval.reason}`;
  elements.approveButton.disabled = false;
  elements.rejectButton.disabled = false;
  elements.executeButton.disabled = true;
  activateTab("approval");
}

async function refreshAudit() {
  if (!state.correlationId) return;
  try {
    const events = await request(`/audit/${encodeURIComponent(state.correlationId)}`);
    if (!events.length) {
      elements.auditList.innerHTML = '<li class="empty">No audit events recorded yet.</li>';
      return;
    }
    elements.auditList.innerHTML = events.map((event) => `
      <li>
        <span class="event-title">${escapeHtml(event.event_type)}</span>
        <span class="event-meta">${escapeHtml(event.source)} · ${escapeHtml(event.status)}</span>
      </li>
    `).join("");
  } catch (error) {
    showToast(`Audit refresh failed: ${error.message}`);
  }
}

async function submitChat(event) {
  event.preventDefault();
  const userMessage = elements.userMessage.value.trim();
  if (!userMessage) return;
  addMessage("user", userMessage);
  elements.userMessage.value = "";
  elements.sendButton.disabled = true;
  resetApproval();
  try {
    const data = await request("/agent/chat", {
      method: "POST",
      body: JSON.stringify({
        user_message: userMessage,
        simulate_when_ready: elements.executeReady.checked,
      }),
    });
    addMessage("assistant", data.message);
    addExecutionResult(data.simulation_result);
    renderAction(data);
    renderApproval(data.approval_request);
    await refreshAudit();
  } catch (error) {
    addMessage("assistant", error.message, true);
  } finally {
    elements.sendButton.disabled = false;
    elements.userMessage.focus();
  }
}

async function decideApproval(decision) {
  if (!state.approvalId) return;
  const reviewer = elements.reviewer.value.trim();
  if (!reviewer) {
    showToast("Reviewer is required.");
    return;
  }
  try {
    const data = await request(`/approvals/${encodeURIComponent(state.approvalId)}/decision`, {
      method: "POST",
      body: JSON.stringify({
        decision,
        reviewer,
        comment: elements.approvalComment.value.trim() || null,
      }),
    });
    state.approvalDecision = decision;
    setBadge(elements.approvalStatus, data.status);
    elements.approvalSummary.textContent =
      `${data.requested_tool} was ${data.decision} by ${data.reviewer}.`;
    elements.approveButton.disabled = true;
    elements.rejectButton.disabled = true;
    elements.executeButton.disabled = decision !== "approved";
    addMessage("assistant", `Approval ${data.decision} by ${data.reviewer}.`);
    await refreshAudit();
  } catch (error) {
    showToast(`Approval decision failed: ${error.message}`);
  }
}

async function executeApproval() {
  if (!state.approvalId || state.approvalDecision !== "approved") return;
  elements.executeButton.disabled = true;
  try {
    const data = await request(`/approvals/${encodeURIComponent(state.approvalId)}/execute`, {
      method: "POST",
    });
    setBadge(elements.approvalStatus, data.execution_status);
    elements.resultView.textContent = JSON.stringify(data.simulation_result, null, 2);
    addMessage("assistant", data.message);
    addExecutionResult(data.simulation_result);
    activateTab("action");
    await refreshAudit();
  } catch (error) {
    elements.executeButton.disabled = false;
    showToast(`Approved execution failed: ${error.message}`);
  }
}

async function refreshRuntime() {
  try {
    const [health, adapter, mcp, readiness] = await Promise.all([
      request("/health"),
      request("/foundry/agent-adapter"),
      request("/mcp/config"),
      request("/operations/readiness"),
    ]);
    elements.healthIndicator.className = "status-dot ok";
    elements.healthLabel.textContent = health.status;
    elements.runtimeLabel.textContent = `${adapter.runtime} · MCP ${mcp.mode}`;
    elements.runtimeDetails.innerHTML = `
      <div><dt>Health</dt><dd>${escapeHtml(health.status)}</dd></div>
      <div><dt>Agent runtime</dt><dd>${escapeHtml(adapter.runtime)} / ${escapeHtml(adapter.implementation_status)}</dd></div>
      <div><dt>MCP execution</dt><dd>${escapeHtml(mcp.mode)} / ${escapeHtml(mcp.server_name)}</dd></div>
      <div><dt>Readiness</dt><dd>${escapeHtml(readiness.status)}</dd></div>
    `;
  } catch (error) {
    elements.healthIndicator.className = "status-dot error";
    elements.healthLabel.textContent = "Unavailable";
    elements.runtimeLabel.textContent = error.message;
  }
}

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => activateTab(tab.dataset.tab));
});
document.querySelectorAll(".scenario").forEach((scenario) => {
  scenario.addEventListener("click", () => {
    elements.userMessage.value = scenario.dataset.prompt;
    elements.userMessage.focus();
  });
});
elements.chatForm.addEventListener("submit", submitChat);
elements.approveButton.addEventListener("click", () => decideApproval("approved"));
elements.rejectButton.addEventListener("click", () => decideApproval("rejected"));
elements.executeButton.addEventListener("click", executeApproval);
elements.refreshAudit.addEventListener("click", refreshAudit);
elements.refreshRuntime.addEventListener("click", refreshRuntime);
elements.userMessage.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    elements.chatForm.requestSubmit();
  }
});

refreshRuntime();
