const queryInput = document.getElementById("query-input");
const categorySelect = document.getElementById("category-select");
const summary = document.getElementById("summary");
const resultsContainer = document.getElementById("results");
const detailsContainer = document.getElementById("details");
const resultCount = document.getElementById("result-count");

const metrics = {
  indexedTerms: document.getElementById("indexed-terms"),
  totalNodes: document.getElementById("total-nodes"),
  nodeVisits: document.getElementById("node-visits"),
  candidateCount: document.getElementById("candidate-count"),
};

let latestPayload = null;
let selectedProductId = null;
let debounceId = null;

function updateMetrics(payload) {
  metrics.indexedTerms.textContent = payload.metrics.indexed_terms;
  metrics.totalNodes.textContent = payload.metrics.total_nodes;
  metrics.nodeVisits.textContent = payload.metrics.node_visits;
  metrics.candidateCount.textContent = payload.metrics.candidate_count;
}

function renderCategoryOptions(categories) {
  const currentValue = categorySelect.value;
  categorySelect.innerHTML = '<option value="">All Categories</option>';

  categories.forEach((category) => {
    const option = document.createElement("option");
    option.value = category;
    option.textContent = category;
    categorySelect.append(option);
  });

  categorySelect.value = categories.includes(currentValue) ? currentValue : "";
}

function renderDetails(product) {
  if (!product) {
    detailsContainer.className = "details empty";
    detailsContainer.textContent =
      "Select a suggestion to view its aisle, price, stock status, and aliases.";
    return;
  }

  detailsContainer.className = "details";
  detailsContainer.innerHTML = `
    <h3>${product.name}</h3>
    <p>${product.description}</p>
    <div class="detail-row"><strong>Category:</strong> ${product.category}</div>
    <div class="detail-row"><strong>Aisle:</strong> ${product.aisle}</div>
    <div class="detail-row"><strong>Price:</strong> $${product.price}</div>
    <div class="detail-row"><strong>Popularity:</strong> ${product.popularity}</div>
    <div class="detail-row"><strong>Status:</strong> ${product.in_stock ? "In Stock" : "Out of Stock"}</div>
    <div class="badge-row">
      ${product.aliases.map((alias) => `<span class="badge">${alias}</span>`).join("")}
    </div>
  `;
}

function renderResults(payload) {
  latestPayload = payload;
  updateMetrics(payload);
  renderCategoryOptions(payload.categories);

  resultCount.textContent = `${payload.total_matches} match${payload.total_matches === 1 ? "" : "es"}`;

  if (payload.total_matches === 0) {
    resultsContainer.innerHTML = '<p class="detail-row">No products matched that prefix.</p>';
    renderDetails(null);
    summary.textContent = "No matches found. Try a different prefix or remove the category filter.";
    return;
  }

  const label = payload.normalized_query
    ? `Showing ${payload.result_count} of ${payload.total_matches} matches for "${payload.normalized_query}".`
    : `Showing featured products from the catalog.`;
  summary.textContent = label;

  resultsContainer.innerHTML = "";
  payload.results.forEach((product, index) => {
    const card = document.createElement("article");
    card.className = `result-card${product.product_id === selectedProductId ? " active" : ""}`;
    card.innerHTML = `
      <h3>${product.name}</h3>
      <div class="result-meta">${product.category} · ${product.aisle}</div>
      <div class="badge-row">
        <span class="badge">$${product.price}</span>
        <span class="badge${product.in_stock ? "" : " stock-out"}">${product.in_stock ? "In Stock" : "Out of Stock"}</span>
      </div>
    `;

    card.addEventListener("click", () => {
      selectedProductId = product.product_id;
      document
        .querySelectorAll(".result-card")
        .forEach((element) => element.classList.remove("active"));
      card.classList.add("active");
      renderDetails(product);
    });

    resultsContainer.append(card);

    if (index === 0 && selectedProductId === null) {
      selectedProductId = product.product_id;
      card.classList.add("active");
      renderDetails(product);
    }
  });

  if (!payload.results.some((product) => product.product_id === selectedProductId)) {
    selectedProductId = payload.results[0].product_id;
    renderDetails(payload.results[0]);
    const firstCard = resultsContainer.querySelector(".result-card");
    if (firstCard) {
      firstCard.classList.add("active");
    }
  }
}

async function fetchResults() {
  const params = new URLSearchParams({
    q: queryInput.value,
    category: categorySelect.value,
    limit: "8",
  });

  const response = await fetch(`/api/search?${params.toString()}`);
  const payload = await response.json();
  renderResults(payload);
}

function queueFetch() {
  clearTimeout(debounceId);
  debounceId = setTimeout(() => {
    selectedProductId = null;
    fetchResults().catch(() => {
      summary.textContent = "Unable to load search results.";
    });
  }, 180);
}

queryInput.addEventListener("input", queueFetch);
categorySelect.addEventListener("change", queueFetch);

fetchResults().catch(() => {
  summary.textContent = "Unable to load search results.";
});
