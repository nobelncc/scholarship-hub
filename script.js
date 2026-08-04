const DATA_URL = "data/scholarships.json";

let scholarships = [];
let filteredScholarships = [];

const searchInput = document.getElementById("searchInput");
const countryFilter = document.getElementById("countryFilter");
const degreeFilter = document.getElementById("degreeFilter");
const fundingFilter = document.getElementById("fundingFilter");
const statusFilter = document.getElementById("statusFilter");
const clearFilters = document.getElementById("clearFilters");

const scholarshipGrid = document.getElementById("scholarshipGrid");
const loading = document.getElementById("loading");
const errorMessage = document.getElementById("errorMessage");
const noResults = document.getElementById("noResults");

const totalCount = document.getElementById("totalCount");
const countryCount = document.getElementById("countryCount");
const providerCount = document.getElementById("providerCount");
const resultCount = document.getElementById("resultCount");


/* =========================
   Load scholarship data
========================= */

async function loadScholarships() {
  try {
    const response = await fetch(`${DATA_URL}?v=${Date.now()}`);

    if (!response.ok) {
      throw new Error("Unable to load scholarship data.");
    }

    const data = await response.json();

    scholarships = Array.isArray(data)
      ? data
      : Array.isArray(data.scholarships)
        ? data.scholarships
        : [];

    filteredScholarships = [...scholarships];

    updateStats();
    populateFilters();
    renderScholarships();

    loading.classList.add("hidden");

  } catch (error) {
    console.error("Scholarship data error:", error);

    loading.classList.add("hidden");
    errorMessage.classList.remove("hidden");
  }
}


/* =========================
   Statistics
========================= */

function updateStats() {
  totalCount.textContent = scholarships.length;

  const countries = new Set();
  const providers = new Set();

  scholarships.forEach((scholarship) => {

    getArray(scholarship.destination_countries).forEach((country) => {
      countries.add(country);
    });

    if (scholarship.provider) {
      providers.add(scholarship.provider);
    }
  });

  countryCount.textContent = countries.size;
  providerCount.textContent = providers.size;
}


/* =========================
   Populate filters
========================= */

function populateFilters() {

  const countries = new Set();
  const degrees = new Set();
  const fundingTypes = new Set();

  scholarships.forEach((scholarship) => {

    getArray(scholarship.destination_countries).forEach((country) => {
      countries.add(country);
    });

    getArray(scholarship.degree_levels).forEach((degree) => {
      degrees.add(degree);
    });

    getArray(scholarship.funding_type).forEach((funding) => {
      fundingTypes.add(funding);
    });
  });

  populateSelect(
    countryFilter,
    countries,
    "All destinations"
  );

  populateSelect(
    degreeFilter,
    degrees,
    "All degree levels"
  );

  populateSelect(
    fundingFilter,
    fundingTypes,
    "All funding types"
  );
}


function populateSelect(selectElement, values, defaultText) {

  selectElement.innerHTML = "";

  const defaultOption = document.createElement("option");

  defaultOption.value = "";
  defaultOption.textContent = defaultText;

  selectElement.appendChild(defaultOption);

  [...values]
    .filter(Boolean)
    .sort((a, b) => a.localeCompare(b))
    .forEach((value) => {

      const option = document.createElement("option");

      option.value = value;
      option.textContent = value;

      selectElement.appendChild(option);
    });
}


/* =========================
   Filtering
========================= */

function applyFilters() {

  const searchTerm =
    searchInput.value.trim().toLowerCase();

  const selectedCountry =
    countryFilter.value.toLowerCase();

  const selectedDegree =
    degreeFilter.value.toLowerCase();

  const selectedFunding =
    fundingFilter.value.toLowerCase();

  const selectedStatus =
    statusFilter.value.toLowerCase();


  filteredScholarships = scholarships.filter((scholarship) => {

    /* Search */

    if (searchTerm) {

      const searchableText = [

        scholarship.title,

        scholarship.provider,

        scholarship.source,

        scholarship.description,

        scholarship.official_url,

        ...getArray(scholarship.destination_countries),

        ...getArray(scholarship.eligible_countries),

        ...getArray(scholarship.degree_levels),

        ...getArray(scholarship.fields),

        ...getArray(scholarship.funding_type)

      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      if (!searchableText.includes(searchTerm)) {
        return false;
      }
    }


    /* Country */

    if (selectedCountry) {

      const countries = getArray(
        scholarship.destination_countries
      ).map((item) => item.toLowerCase());

      if (!countries.includes(selectedCountry)) {
        return false;
      }
    }


    /* Degree */

    if (selectedDegree) {

      const degrees = getArray(
        scholarship.degree_levels
      ).map((item) => item.toLowerCase());

      if (!degrees.includes(selectedDegree)) {
        return false;
      }
    }


    /* Funding */

    if (selectedFunding) {

      const funding = getArray(
        scholarship.funding_type
      ).map((item) => item.toLowerCase());

      if (!funding.includes(selectedFunding)) {
        return false;
      }
    }


    /* Status */

    if (selectedStatus) {

      const status =
        String(scholarship.status || "unknown")
          .toLowerCase();

      if (status !== selectedStatus) {
        return false;
      }
    }


    return true;
  });


  renderScholarships();
}


/* =========================
   Render scholarships
========================= */

function renderScholarships() {

  scholarshipGrid.innerHTML = "";

  resultCount.textContent =
    filteredScholarships.length;


  if (filteredScholarships.length === 0) {

    noResults.classList.remove("hidden");

    return;
  }

  noResults.classList.add("hidden");


  filteredScholarships.forEach((scholarship) => {

    scholarshipGrid.appendChild(
      createScholarshipCard(scholarship)
    );

  });
}


/* =========================
   Create scholarship card
========================= */

function createScholarshipCard(scholarship) {

  const card = document.createElement("article");

  card.className = "scholarship-card";


  const status =
    String(scholarship.status || "unknown")
      .toLowerCase();

  const statusClass =
    status === "open"
      ? "status-open"
      : status === "closed"
        ? "status-closed"
        : "status-unknown";


  const statusText =
    status.charAt(0).toUpperCase() +
    status.slice(1);


  const provider =
    scholarship.provider ||
    scholarship.source ||
    "Unknown provider";


  const title =
    scholarship.title ||
    "Scholarship opportunity";


  const description =
    scholarship.description ||
    "Visit the official source for complete information.";


  const destinations =
    getArray(scholarship.destination_countries);


  const degrees =
    getArray(scholarship.degree_levels);


  const funding =
    getArray(scholarship.funding_type);


  const deadline =
    formatDate(scholarship.deadline);


  const duration =
    scholarship.duration ||
    "Not specified";


  const destinationText =
    destinations.length
      ? destinations.slice(0, 2).join(", ")
      : "Not specified";


  const degreeText =
    degrees.length
      ? degrees.slice(0, 2).join(", ")
      : "Not specified";


  const tags = [

    ...destinations.slice(0, 2),

    ...degrees.slice(0, 2),

    ...funding.slice(0, 1)

  ];


  const officialUrl =
    safeUrl(scholarship.official_url);


  card.innerHTML = `

    <div class="card-top">

      <div class="provider">
        ${escapeHtml(provider)}
      </div>

      <span class="status ${statusClass}">
        ${escapeHtml(statusText)}
      </span>

    </div>


    <h3>
      ${escapeHtml(title)}
    </h3>


    <p class="card-description">
      ${escapeHtml(description)}
    </p>


    <div class="card-tags">

      ${
        tags.length
          ? tags
              .map(
                (tag) =>
                  `<span class="tag">${escapeHtml(tag)}</span>`
              )
              .join("")
          : `<span class="tag">Scholarship</span>`
      }

    </div>


    <div class="card-meta">

      <div class="meta-item">

        <span class="meta-label">
          Destination
        </span>

        <span class="meta-value">
          ${escapeHtml(destinationText)}
        </span>

      </div>


      <div class="meta-item">

        <span class="meta-label">
          Degree
        </span>

        <span class="meta-value">
          ${escapeHtml(degreeText)}
        </span>

      </div>


      <div class="meta-item">

        <span class="meta-label">
          Deadline
        </span>

        <span class="meta-value">
          ${escapeHtml(deadline)}
        </span>

      </div>


      <div class="meta-item">

        <span class="meta-label">
          Duration
        </span>

        <span class="meta-value">
          ${escapeHtml(duration)}
        </span>

      </div>

    </div>


    ${
      officialUrl
        ? `
          <a
            class="card-button"
            href="${officialUrl}"
            target="_blank"
            rel="noopener noreferrer"
          >
            View Official Opportunity ↗
          </a>
        `
        : `
          <span
            class="card-button"
            style="opacity:0.5; cursor:not-allowed;"
          >
            Official link unavailable
          </span>
        `
    }

  `;


  return card;
}


/* =========================
   Utility functions
========================= */

function getArray(value) {

  if (Array.isArray(value)) {
    return value
      .map((item) => String(item).trim())
      .filter(Boolean);
  }

  if (typeof value === "string") {

    return value
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
  }

  return [];
}


function formatDate(value) {

  if (!value) {
    return "Not specified";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return date.toLocaleDateString(
    "en-US",
    {
      year: "numeric",
      month: "short",
      day: "numeric"
    }
  );
}


function safeUrl(value) {

  if (!value) {
    return "";
  }

  try {

    const url = new URL(value);

    if (
      url.protocol === "http:" ||
      url.protocol === "https:"
    ) {
      return url.href;
    }

  } catch (error) {
    return "";
  }

  return "";
}


function escapeHtml(value) {

  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}


/* =========================
   Event listeners
========================= */

searchInput.addEventListener(
  "input",
  applyFilters
);

countryFilter.addEventListener(
  "change",
  applyFilters
);

degreeFilter.addEventListener(
  "change",
  applyFilters
);

fundingFilter.addEventListener(
  "change",
  applyFilters
);

statusFilter.addEventListener(
  "change",
  applyFilters
);


clearFilters.addEventListener(
  "click",
  () => {

    searchInput.value = "";

    countryFilter.value = "";

    degreeFilter.value = "";

    fundingFilter.value = "";

    statusFilter.value = "";

    applyFilters();
  }
);


/* =========================
   Start application
========================= */

loadScholarships();
