const healthEl = document.getElementById("health");
const listEl = document.getElementById("tasks");
const form = document.getElementById("task-form");

async function loadHealth() {
  try {
    const res = await fetch("/health");
    const data = await res.json();
    healthEl.textContent = `Health: ${data.status} · DB ${data.database} · ${data.time}`;
    healthEl.className = `health ${data.status === "ok" ? "ok" : "bad"}`;
  } catch {
    healthEl.textContent = "Health: container not reachable";
    healthEl.className = "health bad";
  }
}

function renderTasks(tasks) {
  listEl.innerHTML = "";
  if (!tasks.length) {
    listEl.innerHTML = "<li>No tasks yet. Add one after the container is healthy.</li>";
    return;
  }
  for (const task of tasks) {
    const li = document.createElement("li");
    if (task.done) li.classList.add("done");

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = Boolean(task.done);
    checkbox.addEventListener("change", () => toggleTask(task.id));

    const title = document.createElement("span");
    title.textContent = task.title;

    const remove = document.createElement("button");
    remove.className = "ghost";
    remove.type = "button";
    remove.textContent = "Delete";
    remove.addEventListener("click", () => deleteTask(task.id));

    li.append(checkbox, title, remove);
    listEl.append(li);
  }
}

async function loadTasks() {
  const res = await fetch("/api/tasks");
  renderTasks(await res.json());
}

async function toggleTask(id) {
  await fetch(`/api/tasks/${id}`, { method: "PATCH" });
  await loadTasks();
}

async function deleteTask(id) {
  await fetch(`/api/tasks/${id}`, { method: "DELETE" });
  await loadTasks();
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = document.getElementById("title");
  const title = input.value.trim();
  if (!title) return;
  await fetch("/api/tasks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  input.value = "";
  await loadTasks();
});

loadHealth();
loadTasks();
setInterval(loadHealth, 15000);
