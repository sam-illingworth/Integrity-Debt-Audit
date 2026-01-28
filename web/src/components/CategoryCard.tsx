import { ChevronDown, ChevronUp } from "lucide-react";
import type { CategoryResult } from "../types";
import "./CategoryCard.css";

interface CategoryCardProps {
  category: CategoryResult;
  isExpanded: boolean;
  onToggle: () => void;
}

export default function CategoryCard({
  category,
  isExpanded,
  onToggle,
}: CategoryCardProps) {
  const score = category.verified_score || category.score;
  const statusColor =
    score >= 4 ? "green" : score === 3 ? "orange" : "red";
  const statusLabel =
    score >= 4 ? "Resilient" : score === 3 ? "Moderate" : "Vulnerable";

  return (
    <div className={`category-card ${statusColor}`}>
      <button
        className="category-header"
        onClick={onToggle}
      >
        <div className="category-info">
          <h3>{category.category}</h3>
          <span className={`status-badge ${statusColor}`}>
            {statusLabel} ({score}/5)
          </span>
        </div>
        <div className="toggle-icon">
          {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </div>
      </button>

      {isExpanded && (
        <div className="category-content">
          <div className="content-section">
            <h4>Analysis</h4>
            <p>{category.critique}</p>
          </div>

          <div className="content-section">
            <h4>Reflection Question</h4>
            <p>{category.question}</p>
          </div>

          {category.quote !== "N/A" && (
            <div className="content-section">
              <h4>Evidence from Your Assessment</h4>
              <blockquote>{category.quote}</blockquote>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
