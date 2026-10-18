import React, { useState } from "react";
import { Candidate } from "../types";
import { CandidateCard } from "../components/candidates/CandidateCard";
import { Archive, Filter, ShieldCheck, CheckCircle2, XCircle, Clock } from "lucide-react";

interface CandidateExplorerProps {
  candidates: Candidate[];
  onUpdateStatus: (id: string, status: "approved" | "rejected") => void;
  domainName: string;
}

export const CandidateExplorerPage: React.FC<CandidateExplorerProps> = ({
  candidates,
  onUpdateStatus,
  domainName,
}) => {
  const [filter, setFilter] = useState<"all" | "approved" | "pending" | "rejected">("all");

  const filteredCandidates = candidates.filter((c) => {
    if (filter === "all") return true;
    return c.status === filter;
  });

  const countApproved = candidates.filter((c) => c.status === "approved").length;
  const countPending = candidates.filter((c) => c.status === "pending").length;
  const countRejected = candidates.filter((c) => c.status === "rejected").length;

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

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 text-xs font-mono">
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
        <div className="py-20 text-center glass-panel rounded-2xl border-white/5">
          <Archive className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <h4 className="font-display font-bold text-slate-300">NO CANDIDATES FOUND</h4>
          <p className="text-xs font-mono text-slate-500 mt-1">
            Start an adversarial training run to generate candidates for the archive.
          </p>
        </div>
      )}
    </div>
  );
};
