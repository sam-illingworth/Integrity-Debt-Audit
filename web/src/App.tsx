import { useState } from "react";
import AuditForm from "./components/AuditForm";
import ResultsDashboard from "./components/ResultsDashboard";
import type { AuditResult } from "./types";
import "./App.css";

function App() {
  const [auditComplete, setAuditComplete] = useState(false);
  const [auditResult, setAuditResult] = useState<AuditResult | null>(null);
  const [email, setEmail] = useState("");

  const handleAuditComplete = (result: AuditResult, userEmail: string) => {
    setAuditResult(result);
    setEmail(userEmail);
    setAuditComplete(true);
  };

  const handleNewAudit = () => {
    setAuditComplete(false);
    setAuditResult(null);
    setEmail("");
  };

  return (
    <div className="app">
      {!auditComplete ? (
        <AuditForm onComplete={handleAuditComplete} />
      ) : auditResult ? (
        <ResultsDashboard
          result={auditResult}
          email={email}
          onNewAudit={handleNewAudit}
        />
      ) : null}
    </div>
  );
}

export default App;
