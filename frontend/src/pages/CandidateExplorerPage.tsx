import React, { useState } from "react";
import { Candidate } from "../types";
import { CandidateCard } from "../components/candidates/CandidateCard";
import {
  Archive,
  Filter,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  Clock,
  Download,
  CheckCheck,
  Zap,
} from "lucide-react";

interface CandidateExplorerProps {
  candidates: Candidate[];
  onUpdateStatus: (id: string, status: "approved" | "rejected") => void;
  domainName: string;
  onNavigateToStudio?: () => void;
}

export const CandidateExplorerPage: React.FC<CandidateExplorerProps> = ({
  candidates,
  onUpdateStatus,
  domainName,
  onNavigateToStudio,
}) => {
  const [filter, setFilter] = useState<"all" | "approved" | "pending" | "rejected">("all");

  const filteredCandidates = candidates.filter((c) => {
    if (filter === "all") return true;
    return c.status === filter;
  });

  const countApproved = candidates.filter((c) => c.status === "approved").length;
  const countPending = candidates.filter((c) => c.status === "pending").length;
  const countRejected = candidates.filter((c) => c.status === "rejected").length;

  const handleApproveAllPending = () => {
    candidates
      .filter((c) => c.status === "pending")
      .forEach((c) => onUpdateStatus(c.id, "approved"));
  };

  const handleRejectAllPending = () => {
    candidates
      .filter((c) => c.status === "pending")
      .forEach((c) => onUpdateStatus(c.id, "rejected"));
  };

  const handleExportCuratedArchive = () => {
    if (candidates.length === 0) return;
    const headers = [
      "Candidate_ID",
      "Status",
      "Realism_Score",
      "Novelty_Score",
      "Hardness_Score",
      "Risk_Level",
      "Summary",
      "Simple_Explanation",
    ];
    const rows = [headers.join(",")];
    candidates.forEach((c) => {
      rows.push(
        [
          c.id,
          c.status,
          (c.realism_score * 100).toFixed(1) + "%",
          (c.novelty_score * 100).toFixed(1) + "%",
          (c.hardness_score * 100).toFixed(1) + "%",
          c.explanation?.risk_level || "High",
          `"${(c.explanation?.summary || "").replace(/"/g, '""')}"`,
          `"${(c.explanation?.simple_explanation || "").replace(/"/g, '""')}"`,
        ].join(",")
      );
    });

    const blob = new Blob([rows.join("\n")], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `sentinel_${domainName.toLowerCase()}_curated_candidates.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6 pb-16">
      {/* Header & Stats Banner */}
      <div className="glass-panel rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Archive className="w-5 h-5 text-purple-400" />
            <h2 className="font-display font-bold text-xl text-white tracking-wide">
              CANDIDATE NOVELTY ARCHIVE & HUMAN TRIAGE GATE
            </h2>
          </div>
          <p className="text-xs font-mono text-slate-400 mt-1">
            Domain: {domainName.toUpperCase()} · Expert-in-the-Loop Verification Gateway
          </p>
        </div>

        {/* Triage Stats Pills */}
        <div className="flex items-center gap-2 text-xs font-mono">
          <div className="px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>{countApproved} APPROVED</span>
          </div>
          <div className="px-3 py-1.5 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-cyan-400" />
            <span>{countPending} PENDING</span>
          </div>
          <div className="px-3 py-1.5 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-300 flex items-center gap-1.5">
            <XCircle className="w-3.5 h-3.5 text-rose-400" />
            <span>{countRejected} REJECTED</span>
          </div>
        </div>
      </div>

      {/* Filter Tabs & Bulk Actions Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs font-mono">
        <div className="flex items-center gap-2">
          <span className="text-slate-400 flex items-center gap-1 mr-2">
            <Filter className="w-3.5 h-3.5" />
            <span>FILTER:</span>
          </span>
          {(["all", "approved", "pending", "rejected"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setFilter(tab)}
              className={`px-3.5 py-1.5 rounded-lg uppercase tracking-wider transition-all cursor-pointer ${
                filter === tab
                  ? "bg-purple-600/30 text-cyan-300 border border-purple-500/50 shadow-glow"
                  : "text-slate-400 hover:text-white bg-white/5"
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Bulk Action Buttons */}
        <div className="flex items-center gap-2">
          {countPending > 0 && (
            <>
              <button
                onClick={handleApproveAllPending}
                className="px-3 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-400/40 text-emerald-300 flex items-center gap-1.5 transition-all cursor-pointer"
              >
                <CheckCheck className="w-3.5 h-3.5" />
                <span>APPROVE ALL PENDING</span>
              </button>
              <button
                onClick={handleRejectAllPending}
                className="px-3 py-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 border border-rose-400/40 text-rose-300 flex items-center gap-1.5 transition-all cursor-pointer"
              >
                <XCircle className="w-3.5 h-3.5" />
                <span>REJECT ALL PENDING</span>
              </button>
            </>
          )}

          {candidates.length > 0 && (
            <button
              onClick={handleExportCuratedArchive}
              className="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 hover:text-white flex items-center gap-1.5 transition-all cursor-pointer"
            >
              <Download className="w-3.5 h-3.5 text-cyan-300" />
              <span>EXPORT ARCHIVE (.CSV)</span>
            </button>
          )}
        </div>
      </div>

      {/* Grid of Candidate Cards */}
      {filteredCandidates.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredCandidates.map((candidate) => (
            <CandidateCard
              key={candidate.id}
              candidate={candidate}
              onUpdateStatus={onUpdateStatus}
            />
          ))}
        </div>
      ) : (
        <div className="py-20 text-center glass-panel rounded-2xl border-white/5 space-y-4">
          <Archive className="w-12 h-12 text-slate-600 mx-auto" />
          <div>
            <h4 className="font-display font-bold text-slate-300 text-lg">NO CANDIDATES IN THIS FILTER</h4>
            <p className="text-xs font-mono text-slate-500 mt-1 max-w-md mx-auto">
              Synthesize new rare events in Stage 02 (Adversarial Studio) and click "Send to Human Check Gate" to inspect candidates here.
            </p>
          </div>
          {onNavigateToStudio && (
            <button
              onClick={onNavigateToStudio}
              className="px-5 py-2.5 rounded-xl bg-purple-600/30 hover:bg-purple-600/50 border border-purple-500/40 text-cyan-300 font-mono text-xs font-bold tracking-wider inline-flex items-center gap-2 cursor-pointer transition-all shadow-glow"
            >
              <Zap className="w-4 h-4 text-cyan-300" />
              <span>LAUNCH ADVERSARIAL STUDIO (STAGE 02)</span>
            </button>
          )}
        </div>
      )}
    </div>
  );
};
