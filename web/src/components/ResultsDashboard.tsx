import { useState } from "react";
import type { AuditResult } from "../types";
import { generatePDF } from "../utils/pdfGenerator";
import { saveAuditResult } from "../utils/supabaseClient";
import CategoryCard from "./CategoryCard";
import LeadCTA from "./LeadCTA";
import { Download } from "lucide-react";
import "./ResultsDashboard.css";

interface ResultsDashboardProps {
  result: AuditResult;
  email: string;
  onNewAudit: () => void;
}

export default function ResultsDashboard({
  result,
  email,
  onNewAudit,
}: ResultsDashboardProps) {
  const [expandedCategories, setExpandedCategories] = useState<
    Record<string, boolean>
  >({});
  const [downloading, setDownloading] = useState(false);
  const [saved, setSaved] = useState(false);

  const score = result.total_score || 0;
  const susceptibility = result.susceptibility || "";

  const scoreColor =
    score >= 40
      ? "green"
      : score >= 25
        ? "orange"
        : "red";
  const scoreLabel =
    score >= 40
      ? "Resilient"
      : score >= 25
        ? "Moderate"
        : "Vulnerable";

  const toggleCategory = (category: string) => {
    setExpandedCategories((prev) => ({
      ...prev,
      [category]: !prev[category],
    }));
  };

  const handleDownloadPDF = async () => {
    try {
      setDownloading(true);
      const pdf = generatePDF(result);
      const pdfBlob = pdf.output("blob") as Blob;

      pdf.save("Integrity_Debt_Audit.pdf");

      // Save to database
      await saveAuditResult(
        email,
        score,
        susceptibility,
        result.audit_results,
        result.doc_context,
        pdfBlob
      );

      setSaved(true);
    } catch (error) {
      console.error("Error downloading PDF:", error);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="results-container">
      <div className="results-header">
        <button className="back-button" onClick={onNewAudit}>
          ← Audit New Brief
        </button>
        <h1>Audit Results</h1>
      </div>

      <div className="summary-section">
        <div className="summary-box">
          <h2>{result.doc_context}</h2>

          <div className="score-display">
            <div className={`score-circle ${scoreColor}`}>
              <div className="score-number">{score}</div>
              <div className="score-label">/50</div>
            </div>
            <div className="score-info">
              <div className="score-title">{scoreLabel} Position</div>
              <div className="score-description">{susceptibility}</div>
            </div>
          </div>

          <div className="top-improvements">
            <h3>Top Priority Improvements</h3>
            <ol>
              {result.top_improvements.map((imp, idx) => (
                <li key={idx}>{imp}</li>
              ))}
            </ol>
          </div>

          <button
            className="download-button"
            onClick={handleDownloadPDF}
            disabled={downloading}
          >
            {downloading ? (
              <>
                <span className="spinner"></span>
                Generating PDF...
              </>
            ) : (
              <>
                <Download size={18} />
                Download Full Report (PDF)
              </>
            )}
          </button>

          {saved && (
            <div className="saved-message">
              Report saved and downloaded successfully
            </div>
          )}
        </div>
      </div>

      <div className="categories-section">
        <h2>Category Breakdown</h2>
        <div className="categories-grid">
          {result.audit_results.map((cat, idx) => (
            <CategoryCard
              key={idx}
              category={cat}
              isExpanded={expandedCategories[cat.category] || false}
              onToggle={() => toggleCategory(cat.category)}
            />
          ))}
        </div>
      </div>

      <LeadCTA email={email} />
    </div>
  );
}
