const API = "";

// Elements
const modal = document.getElementById("modal");
const addBtn = document.getElementById("addBtn");
const closeBtn = document.querySelector(".close");
const saveDomain = document.getElementById("saveDomain");
const domainInput = document.getElementById("domainInput");
const testBtn = document.getElementById("testBtn");
const tbody = document.querySelector("#domainTable tbody");

// Open modal
addBtn.onclick = () => { modal.style.display = "block"; domainInput.value = ""; }
closeBtn.onclick = () => modal.style.display = "none";
window.onclick = (e) => { if (e.target == modal) modal.style.display = "none"; }

// Add domain
saveDomain.onclick = async () => {
  const domain = domainInput.value.trim();
  if (!domain) return alert("Enter domain");

  await fetch(`${API}/domains`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ domain })
  });
  modal.style.display = "none";
  loadData();
}

// Test all
testBtn.onclick = async () => {
  testBtn.disabled = true;
  testBtn.textContent = "Testing...";
  await fetch(`${API}/test-all`, { method: "POST" });
  setTimeout(loadData, 1000);
  testBtn.disabled = false;
  testBtn.textContent = "Test All";
}


// Add domain
saveDomain.onclick = async () => {
  const domain = domainInput.value.trim();
  if (!domain) return alert("Enter domain");

  const res = await fetch(`${API}/domains`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ domain })
  });

  const data = await res.json();
  modal.style.display = "none";

  // Auto-refresh immediately
  loadData();
};

// Load & render
async function loadData() {
  const statusRes = await fetch(`${API}/status`);
  const data = await statusRes.json();

  // Update cards
  const total = data.length;
  const valid = data.filter(d => d.days_remaining >= 30).length;
  const soon = data.filter(d => d.days_remaining >= 0 && d.days_remaining < 30).length;
  const expired = data.filter(d => d.days_remaining < 0).length;

  document.getElementById("total").textContent = total;
  document.getElementById("valid").textContent = valid;
  document.getElementById("soon").textContent = soon;
  document.getElementById("expired").textContent = expired;

  // Update table
  tbody.innerHTML = "";
  data.forEach(row => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${row.domain}</strong></td>
      <td><span class="status ${row.status.toLowerCase().includes('valid') ? 'valid' : row.status.includes('Expires') ? 'warning' : 'danger'}">${row.status}</span></td>
      <td>${row.expires}</td>
      <td>${row.days_remaining} days</td>
      <td>${row.last_checked}</td>
      <td><button class="action-btn">${row.actions}</button></td>
    `;
    tbody.appendChild(tr);
  });
}

saveDomain.onclick = async () => {
  const domain = domainInput.value.trim();
  if (!domain) return alert("Enter domain");

  saveDomain.disabled = true;
  saveDomain.textContent = "Adding...";

  try {
    await fetch(`/api/domains`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ domain })
    });
    loadData();  // Refresh instantly
  } catch (e) {
    alert("Error adding domain");
  }

  saveDomain.disabled = false;
  saveDomain.textContent = "Add";
  modal.style.display = "none";
};


// // Auto-refresh every 30s
// setInterval(loadData, 30000);
// loadData(); // Initial load




