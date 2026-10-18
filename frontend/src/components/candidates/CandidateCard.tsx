import React from "react";
import { Check, X, AlertTriangle, ShieldAlert, Sparkles } from "lucide-react";
import { Candidate } from "../../types";

interface CandidateCardProps {
  candidate: Candidate;
  onUpdateStatus: (id: string, status: "approved" | "rejected") => void;
}

export const CandidateCard: React.FC<CandidateCardProps> = ({
  candidate,
  onUpdateStatus,
}) => {
  const isApproved = candidate.status === "approved";
  const isRejected = candidate.status === "rejected";

  const riskColors: Record<string, string> = {
    Low: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
    Medium: "text-cyan-400 bg-cyan-500/10 border-cyan-500/30",
    High: "text-amber-400 bg-amber-500/10 border-amber-500/30",
    Critical: "text-rose-400 bg-rose-500/10 border-rose-500/30",
  };

  const riskClass = riskColors[candidate.explanation?.risk_level || "Medium"];

  return (
    <div className="glass-panel rounded-2xl p-4 sm:p-5 flex flex-col justify-between transition-all hover:border-purple-400/40">
      <div>
        {/* Header Badges */}
        <div className="flex items-center justify-between gap-2 mb-3">
          <span className="text-[9px] font-mono tracking-widest px-2 py-0.5 rounded bg-purple-900/40 text-purple-200 border border-purple-500/30">
            ID: {candidate.id} · ROUND {candidate.round_idx}
          </span>
          <span
            className={`text-[9px] font-mono tracking-wider px-2 py-0.5 rounded border uppercase ${riskClass}`}
          >
            {candidate.explanation?.risk_level || "ANOMALOUS"} RISK
          </span>
        </div>

        {/* Fictional Research Disclaimer Badge */}
        <div className="mb-3 px-2 py-1 rounded bg-amber-500/10 border border-amber-500/20 text-[9px] font-mono text-amber-300 flex items-center gap-1.5">
          <ShieldAlert className="w-3 h-3 text-amber-400 shrink-0" />
          <span>SYNTHETIC CANDIDATE — FICTIONAL / UNVALIDATED</span>
        </div>

        {/* Plain Language Summary */}
        <h4 className="font-display font-bold text-xs sm:text-sm text-white mb-2 leading-snug">
          {candidate.explanation?.summary || "Adversarially synthesized boundary candidate."}
        </h4>

        {/* Key Domain Anomalies */}
        <div className="space-y-1 mb-4">
          {candidate.explanation?.key_anomalies?.map((anom, idx) => (
            <div
              key={idx}
              className="text-[11px] font-mono text-slate-300 flex items-start gap-1.5"
            >
              <span className="text-cyan-400 mt-0.5">›</span>
              <span>{anom}</span>
            </div>
          ))}
        </div>

        {/* Score Meters */}
        <div className="space-y-2 pt-3 border-t border-white/5 mb-4 text-[10px] font-mono">
          <div>
            <div className="flex justify-between text-slate-400 mb-0.5">
              <span>REALISM:</span>
              <span className="text-emerald-400 font-bold">
                {(candidate.realism_score * 100).toFixed(0)}%
              </span>
            </div>
            <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-emerald-400"
                style={{ width: `${Math.min(100, candidate.realism_score * 100)}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between text-slate-400 mb-0.5">
              <span>NOVELTY (k-NN DISTANCE):</span>
              <span className="text-purple-400 font-bold">
                {(candidate.novelty_score * 100).toFixed(0)}%
              </span>
            </div>
            <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-purple-500"
                style={{ width: `${Math.min(100, candidate.novelty_score * 100)}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between text-slate-400 mb-0.5">
              <span>DETECTOR HARDNESS:</span>
              <span className="text-pink-400 font-bold">
                {(candidate.hardness_score * 100).toFixed(0)}%
              </span>
            </div>
            <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-pink-500"
                style={{ width: `${Math.min(100, candidate.hardness_score * 100)}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Human-in-the-Loop Triage Actions */}
      <div className="pt-2 flex items-center gap-2">
        <button
          onClick={() => onUpdateStatus(candidate.id, "approved")}
          className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-mono tracking-wider flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
            isApproved
              ? "bg-emerald-500/30 text-emerald-300 border border-emerald-500/60 shadow-sm"
              : "border border-white/10 hover:border-emerald-500/50 hover:bg-emerald-500/10 text-slate-300"
          }`}
        >
          <Check className="w-3.5 h-3.5 text-emerald-400" />
          <span>{isApproved ? "APPROVED" : "APPROVE"}</span>
        </button>

        <button
          onClick={() => onUpdateStatus(candidate.id, "rejected")}
          className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-mono tracking-wider flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
            isRejected
              ? "bg-rose-500/30 text-rose-300 border border-rose-500/60 shadow-sm"
              : "border border-white/10 hover:border-rose-500/50 hover:bg-rose-500/10 text-slate-300"
          }`}
        >
          <X className="w-3.5 h-3.5 text-rose-400" />
          <span>{isRejected ? "REJECTED" : "REJECT"}</span>
        </button>
      </div>
    </div>
  );
};
