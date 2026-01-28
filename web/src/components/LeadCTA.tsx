import React, { useState } from "react";
import { saveLead } from "../utils/supabaseClient";
import { Mail, MessageSquare } from "lucide-react";
import "./LeadCTA.css";

interface LeadCTAProps {
  email: string;
}

export default function LeadCTA({ email }: LeadCTAProps) {
  const [showForm, setShowForm] = useState(false);
  const [wantsCall, setWantsCall] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      await saveLead(email, "", wantsCall);
      setSubmitted(true);
    } catch (error) {
      console.error("Error saving lead:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="lead-cta-section">
      <div className="cta-container">
        <h2>Need Support with Implementation?</h2>
        <p>
          As a Full Professor with over 20 years experience in higher education, I can help you interpret your results and redesign your assessments for AI resilience.
        </p>

        <div className="cta-options">
          <a
            href="mailto:sam.illingworth@gmail.com"
            className="cta-button email-button"
          >
            <Mail size={20} />
            <span>Book a Strategy Call</span>
            <small>sam.illingworth@gmail.com</small>
          </a>

          <a
            href="https://theslowai.substack.com"
            target="_blank"
            rel="noopener noreferrer"
            className="cta-button community-button"
          >
            <MessageSquare size={20} />
            <span>Join Slow AI Community</span>
            <small>theslowai.substack.com</small>
          </a>
        </div>

        {!submitted && (
          <>
            {!showForm && (
              <button
                className="interest-button"
                onClick={() => setShowForm(true)}
              >
                Let me know if you're interested
              </button>
            )}

            {showForm && (
              <form className="interest-form" onSubmit={handleSubmit}>
                <label>
                  <input
                    type="checkbox"
                    checked={wantsCall}
                    onChange={(e) => setWantsCall(e.target.checked)}
                  />
                  I'd like to book a strategy call
                </label>
                <button type="submit" disabled={loading}>
                  {loading ? "Sending..." : "Submit"}
                </button>
              </form>
            )}
          </>
        )}

        {submitted && (
          <div className="success-message">
            Thank you! I'll be in touch soon.
          </div>
        )}
      </div>
    </section>
  );
}
