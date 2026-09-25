import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
Building2,
ExternalLink,
Search,
ArrowRight,
BriefcaseBusiness,
RefreshCw,
Sparkles,
FileDown,
} from "lucide-react";

const API = "/api";

const TEST_COMPANIES = [
"Live Verify 06ef0be6",
"Live Verify Final 50a02b1d",
"Analytics Verify bf92b8a2",
];

function Companies() {
const [companies, setCompanies] = useState([]);
const [search, setSearch] = useState("");
const [loading, setLoading] = useState(true);
const [error, setError] = useState("");

const loadCompanies = async () => {
try {
setLoading(true);
setError("");


  const response = await fetch(`${API}/companies/`);

  if (!response.ok) {
    throw new Error(`Failed to load companies: ${response.status}`);
  }

  const data = await response.json();

  const cleanCompanies = Array.isArray(data)
    ? data.filter((company) => !TEST_COMPANIES.includes(company.name))
    : [];

  setCompanies(cleanCompanies);
} catch (err) {
  setError(err.message || "Unable to load companies.");
} finally {
  setLoading(false);
}


};

useEffect(() => {
loadCompanies();
}, []);

const filteredCompanies = useMemo(() => {
const value = search.trim().toLowerCase();


if (!value) {
  return companies;
}

return companies.filter((company) => {
  const name = company.name || "";
  const industry = company.industry || "";

  return (
    name.toLowerCase().includes(value) ||
    industry.toLowerCase().includes(value)
  );
});


}, [companies, search]);

return ( <main className="companies-page"> <div className="companies-container">


    <section className="companies-header">
      <div className="companies-heading">
        <div className="companies-eyebrow">
          <Sparkles size={14} />
          Placement Directory
        </div>

        <h1>Explore Companies</h1>

        <p>
          Browse placement companies and explore their recruitment
          details, interview rounds, technical topics, and frequently
          asked questions.
        </p>
      </div>

      <button
        type="button"
        className="companies-refresh"
        onClick={loadCompanies}
        disabled={loading}
      >
        <RefreshCw
          size={16}
          className={loading ? "companies-spin" : ""}
        />
        Refresh
      </button>
    </section>

    <section className="companies-overview">
      <div className="companies-overview-icon">
        <Building2 size={22} />
      </div>

      <div>
        <span>Available Companies</span>
        <strong>{companies.length}</strong>
      </div>

      <div className="companies-overview-divider" />

      <div className="companies-overview-text">
        <BriefcaseBusiness size={17} />
        <span>Placement opportunities collected from feedback</span>
      </div>
    </section>

    <section className="companies-toolbar">
      <div className="companies-search">
        <Search size={18} />

        <input
          type="text"
          placeholder="Search company or industry..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />

        {search && (
          <button
            type="button"
            className="companies-clear"
            onClick={() => setSearch("")}
          >
            Clear
          </button>
        )}
      </div>

      <div className="companies-count">
        Showing <strong>{filteredCompanies.length}</strong> companies
      </div>
    </section>

    {error && (
      <section className="companies-error">
        <div>
          <strong>Unable to load companies</strong>
          <p>{error}</p>
        </div>

        <button type="button" onClick={loadCompanies}>
          Try Again
        </button>
      </section>
    )}

    {loading && !error && (
      <section className="companies-grid">
        {[1, 2, 3, 4, 5, 6].map((item) => (
          <div className="company-skeleton" key={item}>
            <div className="skeleton-logo" />
            <div className="skeleton-line large" />
            <div className="skeleton-line" />
            <div className="skeleton-button" />
          </div>
        ))}
      </section>
    )}

    {!loading && !error && filteredCompanies.length === 0 && (
      <section className="companies-empty">
        <div className="companies-empty-icon">
          <Search size={25} />
        </div>

        <h2>No companies found</h2>

        <p>
          Try searching with another company name or industry.
        </p>

        {search && (
          <button
            type="button"
            onClick={() => setSearch("")}
          >
            Clear Search
          </button>
        )}
      </section>
    )}

    {!loading && !error && filteredCompanies.length > 0 && (
      <section className="companies-grid">
        {filteredCompanies.map((company, index) => (
          <article className="company-card" key={company.id}>

            <div className="company-card-top">
              <div className="company-logo">
                {company.name
                  ? company.name.charAt(0).toUpperCase()
                  : "C"}
              </div>

              <span className="company-badge">
                Company {index + 1}
              </span>
            </div>

            <div className="company-card-content">
              <h2>{company.name || "Unknown Company"}</h2>

              <div className="company-industry">
                <Building2 size={14} />
                <span>
                  {company.industry || "Information Technology"}
                </span>
              </div>
            </div>

           <div className="company-card-footer">
  <Link
    to={`/companies/${company.id}`}
    className="company-view-button"
  >
    Explore Company
    <ArrowRight size={15} />
  </Link>

  <Link
    to={`/companies/${company.id}?print=true`}
    className="company-report-button"
    title="Download company report"
  >
    <FileDown size={15} />
    Report
  </Link>

  {company.website && (
    <a
      href={company.website}
      target="_blank"
      rel="noreferrer"
      className="company-website"
      title="Open company website"
    >
      <ExternalLink size={15} />
    </a>
  )}
</div>

          </article>
        ))}
      </section>
    )}

  </div>
</main>

);
}

export default Companies;
