const samples = [
  "Hey, I'll send you the revised slides by Friday. And I'll call the landlord tomorrow about the sink. I should probably clean the spare room too, but maybe next week.",
  "Yep, I'll drop the keys at your place after work. I'll email the invoice before noon, too. I might start sorting the storage cupboard this weekend if I get a chance."
];

const transcriptElement = document.querySelector("#transcript");
const todosElement = document.querySelector("#todos");
const countElement = document.querySelector("#count");
const feedbackElement = document.querySelector("#feedback");
const sampleButtons = document.querySelectorAll(".sample-button");

function extractCommitments(text) {
  const clauses = text.split(/(?<=[.!?])\s+|\n+|(?:,?\s+and\s+|;\s*)(?=I(?:'ll| will| am going to)\b)/i);
  const commitments = [];

  for (const clause of clauses) {
    const promise = /\bI(?:'ll| will| am going to)\s+(.+)/i.exec(clause);
    if (!promise || /\b(?:maybe|might|should|could|probably|perhaps|if|try to|hope to|not|never)\b/i.test(clause.slice(0, promise.index) + " " + promise[1])) {
      continue;
    }

    const quote = clause.trim();
    const action = promise[1].replace(/[.!?]+$/, "").replace(/,\s*too$/i, "").trim();
    const due = /\b(?:by|before|on)\s+(?:next\s+|this\s+)?(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|tonight|noon|\d{1,2}(?::\d{2})?\s*(?:am|pm)?|[a-z]+\s+\d{1,2})\b|\b(?:tomorrow|tonight|today|after work|next week|this weekend)\b/i.exec(action);
    const task = (due ? action.slice(0, due.index) + action.slice(due.index + due[0].length) : action)
      .trim().replace(/\s+/g, " ").replace(/[,;\s]+$/, "");
    if (!/^[a-z]+(?:\s|$)/i.test(task) || task.length < 5) {
      continue;
    }
    commitments.push({
      task: task[0].toUpperCase() + task.slice(1),
      deadline: due ? due[0] : null,
      quote
    });
  }
  return commitments;
}

function renderCommitments(commitments) {
  countElement.textContent = `${commitments.length} found`;
  todosElement.replaceChildren(...commitments.map((commitment) => {
    const row = document.createElement("div");
    row.className = "todo";
    const checkbox = document.createElement("button");
    checkbox.className = "check";
    checkbox.type = "button";
    checkbox.setAttribute("aria-label", `Mark ${commitment.task} done`);
    checkbox.setAttribute("aria-pressed", "false");
    checkbox.addEventListener("click", () => {
      const done = checkbox.getAttribute("aria-pressed") !== "true";
      checkbox.setAttribute("aria-pressed", String(done));
      checkbox.setAttribute("aria-label", `${done ? "Mark" : "Unmark"} ${commitment.task} ${done ? "not done" : "done"}`);
      checkbox.textContent = done ? "✓" : "";
      row.classList.toggle("done", done);
    });

    const content = document.createElement("div");
    const task = document.createElement("p");
    task.className = "task";
    task.textContent = commitment.task;
    const metadata = document.createElement("div");
    metadata.className = "todo-meta";
    if (commitment.deadline) {
      const deadline = document.createElement("span");
      deadline.className = "deadline";
      deadline.textContent = commitment.deadline;
      metadata.append(deadline);
    }
    const quote = document.createElement("span");
    quote.className = "source-quote";
    quote.textContent = `“${commitment.quote}”`;
    metadata.append(quote);
    content.append(task, metadata);
    row.append(checkbox, content);
    return row;
  }));
}

function runExtraction() {
  const text = transcriptElement.value.trim();
  if (!text) {
    renderCommitments([]);
    feedbackElement.textContent = "Enter some text or choose a sample first.";
    feedbackElement.classList.add("error");
    transcriptElement.focus();
    return;
  }
  const commitments = extractCommitments(text);
  renderCommitments(commitments);
  feedbackElement.classList.remove("error");
  feedbackElement.textContent = commitments.length
    ? "Tap a checkbox to mark a promise done. Edit the text and run again to start fresh."
    : "No clear promises found. Try a sentence like “I'll send you the slides by Friday.”";
}

sampleButtons.forEach((button) => {
  button.addEventListener("click", () => {
    transcriptElement.value = samples[Number(button.dataset.sample)];
    sampleButtons.forEach((sampleButton) => {
      sampleButton.setAttribute("aria-pressed", String(sampleButton === button));
    });
    runExtraction();
  });
});

transcriptElement.addEventListener("input", () => {
  sampleButtons.forEach((button) => button.setAttribute("aria-pressed", "false"));
  feedbackElement.textContent = "Text changed. Select Find promises to update the results.";
  feedbackElement.classList.remove("error");
});
document.querySelector("#extract").addEventListener("click", runExtraction);
transcriptElement.value = samples[0];
runExtraction();
