// layout.js
const API = "https://guardlink-production.up.railway.app";

const token = localStorage.getItem("token");
const role = localStorage.getItem("role");
if (!token || role !== "admin") window.location.href = "../login.html";

// Apply saved theme immediately
const savedTheme = localStorage.getItem("theme") || "light";
document.documentElement.setAttribute("data-theme", savedTheme);

async function apiFetch(endpoint, options = {}) {
  const response = await fetch(`${API}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
      ...options.headers
    }
  });
  return response;
}

function updateToggle(theme) {
  const checkbox = document.getElementById("themeCheckbox");
  const icon = document.getElementById("toggleIcon");
  if (checkbox) checkbox.checked = theme === "dark";
  if (icon) icon.textContent = theme === "dark" ? "🌙" : "☀️";
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme");
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("theme", next);
  updateToggle(next);
}

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("role");
  localStorage.removeItem("full_name");
  window.location.href = "../login.html";
}

window.addEventListener("DOMContentLoaded", () => {
  updateToggle(savedTheme);
  const nameEl = document.getElementById("adminName");
  if (nameEl) nameEl.textContent = localStorage.getItem("full_name") || "Admin";
});