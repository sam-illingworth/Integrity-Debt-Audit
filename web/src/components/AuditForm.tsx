import { useState } from "react";
import { analyzeAssessment } from "../utils/auditService";
import { extractFromFile, fetchFromURL } from "../utils/textExtraction";
import type { AuditResult } from "../types";
import { Upload, FileText } from "lucide-react";
import "./AuditForm.css";

interface AuditFormProps {
  onComplete: (result: AuditResult, email: string) => void;
}

export default function AuditForm({ onComplete }: AuditFormProps) {
  const [email, setEmail] = useState("");
  const [inputType, setInputType] = useState<"file" | "paste">("file");
  const [file, setFile] = useState<File | null>(null);
  const [textInput, setTextInput] = useState("");
  const [expectation, setExpectation] = useState("Medium");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (
        !["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"].includes(
          selectedFile.type
        )
      ) {
        setError("Please upload a PDF or DOCX file");
        return;
      }
      setFile(selectedFile);
      setError("");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!email || !email.includes("@")) {
      setError("Please provide a valid email address");
      return;
    }

    let assessmentText: string | null = null;

    try {
      setLoading(true);

      if (inputType === "file") {
        if (!file) {
          setError("Please select a file to upload");
          return;
        }
        assessmentText = await extractFromFile(file);
      } else {
        if (!textInput.trim()) {
          setError("Please paste your assessment or enter a URL");
          return;
        }

        if (textInput.trim().startsWith("http")) {
          assessmentText = await fetchFromURL(textInput.trim());
        } else {
          assessmentText = textInput;
        }
      }

      if (!assessmentText || assessmentText.length < 100) {
        setError("Assessment content is too short. Please provide at least 100 characters.");
        return;
      }

      const result = await analyzeAssessment(assessmentText);
      onComplete(result, email);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "An error occurred";
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="audit-form-container">
      <header className="audit-header">
        <div className="audit-header-content">
          <h1>Integrity Debt Diagnostic</h1>
          <p>Analyze your assessment for AI resilience</p>
        </div>
      </header>

      <main className="audit-main">
        <section className="intro-section">
          <div className="intro-text">
            <h2>What is this tool?</h2>
            <p>
              The <strong>Integrity Debt Audit</strong> helps you identify if your assessments can be easily automated by AI. Many traditional assignments are now vulnerable to being completed by AI in minutes rather than through genuine student learning.
            </p>
            <p>
              This diagnostic evaluates your assessment brief across <strong>10 evidence-based categories</strong> that distinguish human learning from AI automation. Each category is scored from 1 (easily automated) to 5 (resilient to AI), giving you a total integrity score out of 50.
            </p>
          </div>

          <div className="intro-benefits">
            <h3>Why use this audit?</h3>
            <ul>
              <li>Stop chasing ghosts with AI detectors – they don't work reliably</li>
              <li>Fix the curriculum, not the students</li>
              <li>Protect institutional reputation</li>
              <li>Design AI-resilient assessments</li>
            </ul>
          </div>
        </section>

        <form className="audit-form" onSubmit={handleSubmit}>
          <div className="form-section">
            <h3>1. Your Details</h3>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="email">Email Address (required)</label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="expectation">Predicted Susceptibility</label>
                <select
                  id="expectation"
                  value={expectation}
                  onChange={(e) => setExpectation(e.target.value)}
                >
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                </select>
              </div>
            </div>
          </div>

          <div className="form-divider"></div>

          <div className="form-section">
            <h3>2. Assessment Input</h3>

            <div className="input-type-selector">
              <button
                type="button"
                className={`input-type-btn ${inputType === "file" ? "active" : ""}`}
                onClick={() => setInputType("file")}
              >
                <Upload size={18} />
                File Upload
              </button>
              <button
                type="button"
                className={`input-type-btn ${inputType === "paste" ? "active" : ""}`}
                onClick={() => setInputType("paste")}
              >
                <FileText size={18} />
                Paste Text or URL
              </button>
            </div>

            {inputType === "file" ? (
              <div className="form-group">
                <label htmlFor="file">Upload Assessment Brief (PDF or DOCX)</label>
                <div className="file-input-wrapper">
                  <input
                    id="file"
                    type="file"
                    accept=".pdf,.docx"
                    onChange={handleFileChange}
                  />
                  <div className="file-input-placeholder">
                    {file ? (
                      <>
                        <FileText size={24} />
                        <p>{file.name}</p>
                      </>
                    ) : (
                      <>
                        <Upload size={24} />
                        <p>Click to upload or drag and drop</p>
                        <span>PDF or DOCX</span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="form-group">
                <label htmlFor="text-input">Assessment Brief or URL</label>
                <textarea
                  id="text-input"
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                  placeholder="Paste your complete assessment text here, or enter the URL to a public assessment page..."
                  rows={8}
                />
              </div>
            )}
          </div>

          {error && <div className="error-message">{error}</div>}

          <button
            type="submit"
            disabled={loading}
            className="submit-button"
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Analyzing...
              </>
            ) : (
              "Generate Diagnostic Report"
            )}
          </button>
        </form>

        <section className="footer-info">
          <p>
            <strong>Privacy:</strong> This tool is stateless. Assessment briefs are processed in-memory and not stored.
          </p>
        </section>
      </main>
    </div>
  );
}
