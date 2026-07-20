(() => {
  const launcher = document.getElementById("chat-launcher");
  const panel = document.getElementById("chat-panel");
  const closeBtn = document.getElementById("chat-close");
  const expandBtn = document.getElementById("chat-expand");
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");
  const messages = document.getElementById("chat-messages");

  const WELCOME_MESSAGE =
    "Hola, soy Andres el Agente Virtual de la UNAB. Estoy aqui para resolver tus dudas con reglamentos, " +
    "servicio social, matrícula, graduación y otros procesos oficiales de la institucion.";

  let opened = false;
  let expanded = false;

  const EXAMPLE_QUERIES = [
    "¿Nota mínima de CUM para graduarme?",
    "¿Cual es el proceso para solicitar equivalencias en una asignatura?",
    "¿Cuándo son los primeros parciales del ciclo 2-2026?",
  ];

  function toggleExpand() {
    expanded = !expanded;
    panel.classList.toggle("chat-panel--expanded", expanded);
    expandBtn.textContent = expanded ? "⤡" : "⤢";
    expandBtn.setAttribute("aria-label", expanded ? "Reducir chat" : "Ampliar chat");
    messages.scrollTop = messages.scrollHeight;
  }

  function appendExampleQueries(examples) {
    examples.forEach((example) => {
      const bubble = appendMessage(example, "example");
      bubble.addEventListener("click", () => {
        input.value = example;
        input.focus();
      });
    });
  }

  function toggleChat() {
    opened = !opened;
    if (!opened && expanded) {
      toggleExpand(); // vuelve a tamaño normal al cerrar
    }
    panel.classList.toggle("is-open", opened);
    panel.setAttribute("aria-hidden", String(!opened));
    if (opened) {
      if (!messages.dataset.welcomed) {
        appendMessage(WELCOME_MESSAGE, "bot");
        appendExampleQueries(EXAMPLE_QUERIES);
        messages.dataset.welcomed = "true";
      }
      input.focus();
    }
  }

  launcher.addEventListener("click", toggleChat);
  closeBtn.addEventListener("click", toggleChat);
  expandBtn.addEventListener("click", toggleExpand);

  function normalizeResponseText(text) {
    return String(text ?? "")
      .replace(/\r\n/g, "\n")
      .replace(/[ \t]+\n/g, "\n")
      .replace(/\n{3,}/g, "\n\n")
      .trim();
  }

  function appendMessage(text, sender) {
    const bubble = document.createElement("div");
    const normalizedText =
      sender === "bot" || sender === "example"
        ? normalizeResponseText(text)
        : String(text ?? "");

    if (sender === "example") {
      bubble.className = "msg--example msg--bot";
      bubble.innerHTML = marked.parse(normalizedText);
    } else if (sender === "bot") {
      bubble.className = `msg msg--${sender}`;
      bubble.innerHTML = marked.parse(normalizedText);
    } else {
      bubble.className = `msg msg--${sender}`;
      bubble.textContent = normalizedText;
    }

    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
    return bubble;
  }

  function showTyping() {
    const typing = document.createElement("div");
    typing.className = "msg--typing";
    typing.id = "typing-indicator";
    typing.innerHTML = "<span></span><span></span><span></span>";
    messages.appendChild(typing);
    messages.scrollTop = messages.scrollHeight;
  }

  function hideTyping() {
    const typing = document.getElementById("typing-indicator");
    if (typing) typing.remove();
  }

  async function sendQuery(query) {
    appendMessage(query, "user");
    showTyping();

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      hideTyping();

      if (!response.ok) {
        appendMessage(
          "Ocurrió un problema al procesar tu consulta. Intenta nuevamente en unos minutos.",
          "bot"
        );
        return;
      }

      const data = await response.json();
      appendMessage(data.answer, "bot");
    } catch (err) {
      hideTyping();
      appendMessage(
        "No fue posible conectar con el asistente. Verifica tu conexión e intenta de nuevo.",
        "bot"
      );
    }
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const query = input.value.trim();
    if (!query) return;
    input.value = "";
    sendQuery(query);
  });
})();
