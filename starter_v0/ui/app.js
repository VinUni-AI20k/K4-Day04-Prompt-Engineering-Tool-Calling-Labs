const messages = document.querySelector("#messages");
const form = document.querySelector("#chat-form");
const input = document.querySelector("#message");
const artifact = document.querySelector("#artifact");
const sessionId = `ui-${new Date().toISOString().replace(/[^0-9]/g, "").slice(0, 17)}`;

function addMessage(kind, text) {
  const article = document.createElement("article");
  article.className = `message ${kind}`;
  const label = document.createElement("span");
  label.className = "label";
  label.textContent = kind === "user" ? "Bạn" : "Agent";
  const paragraph = document.createElement("p");
  paragraph.textContent = text || "(Không có nội dung)";
  article.append(label, paragraph);
  messages.append(article);
  messages.scrollTop = messages.scrollHeight;
}

function addTrace(payload) {
  const details = document.createElement("details");
  details.className = "trace";
  details.open = true;
  const summary = document.createElement("summary");
  summary.textContent = `Trace · ${payload.status} · ${payload.rounds.length} round(s)`;
  details.append(summary);

  for (const round of payload.rounds) {
    const block = document.createElement("section");
    const title = document.createElement("h3");
    title.textContent = `Round ${round.round}`;
    const pre = document.createElement("pre");
    pre.textContent = JSON.stringify({
      assistant_text: round.assistant_text,
      tool_calls: round.tool_calls,
      tool_results: round.tool_results,
    }, null, 2);
    block.append(title, pre);
    details.append(block);
  }
  messages.append(details);
  messages.scrollTop = messages.scrollHeight;
}

async function loadHealth() {
  try {
    const response = await fetch("/api/health");
    const data = await response.json();
    artifact.textContent = `${data.artifact_version} · ${data.provider}/${data.model}`;
  } catch (error) {
    artifact.textContent = "Backend unavailable";
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;
  addMessage("user", message);
  input.value = "";
  input.disabled = true;
  form.querySelector("button").disabled = true;

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({session_id: sessionId, message}),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(`${data.error}: ${data.message}`);
    addMessage("assistant", data.assistant_text);
    addTrace(data);
  } catch (error) {
    addMessage("assistant", `ERROR: ${error.message}`);
  } finally {
    input.disabled = false;
    form.querySelector("button").disabled = false;
    input.focus();
  }
});

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

loadHealth();
