import React from "react";
import { HiddenClassProof } from "../../types";
import { CheckCircle2, ShieldCheck, Zap, X } from "lucide-react";

interface ModalProps {
  proof: HiddenClassProof | null;
  isOpen: boolean;
  onClose: () => void;
  isLoading: boolean;
}

export const HiddenClassModal: React.FC<ModalProps> = ({
  proof,
  isOpen,
  onClose,
  isLoading,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <div className="relative w-full max-w-2xl glass-panel rounded-2xl p-6 border border-cyan-500/40 shadow-glow-cyan text-white animate-scale-in">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center">
            <Zap className="w-5 h-5 text-cyan-300" />
          </div>
          <div>
            <h3 className="font-display font-bold text-lg tracking-wide text-white">
              HIDDEN-CLASS GENERALIZATION PROOF
            </h3>
            <p className="text-xs font-mono text-cyan-300">
              Zero-Shot Recall on Held-Out Rare Subclass
            </p>
          </div>
        </div>

        {isLoading ? (
          <div className="py-12 flex flex-col items-center justify-center gap-3">
            <div className="w-8 h-8 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin" />
            <p className="text-xs font-mono text-slate-400">
              Training detector on visible classes & testing zero-shot holdout...
            </p>
          </div>
        ) : proof ? (
          <div className="space-y-5">
            {/* Context callout */}
            <div className="p-3.5 rounded-xl bg-purple-950/40 border border-purple-500/30 text-xs font-mono text-slate-300 leading-relaxed">
              <span className="text-cyan-300 font-bold">EXPERIMENTAL PROTOCOL: </span>
              The rare subclass <span className="text-amber-400 font-bold">'{proof.hidden_class_name}'</span> was completely filtered out from all training, validation, and calibration splits. It was evaluated strictly at test time ({proof.n_hidden_test_instances} instances).
            </div>

            {/* Results Table */}
            <div className="overflow-x-auto rounded-xl border border-white/10">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-[#120D36] text-slate-400 text-[10px] uppercase">
                  <tr>
                    <th className="py-2.5 px-3">Model Architecture</th>
                    <th className="py-2.5 px-3 text-right">Hidden-Class Recall</th>
                    <th className="py-2.5 px-3 text-right">Overall PR-AUC</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {proof.comparison.map((row, idx) => {
                    const isOurs = row.model.includes("SENTINEL");
                    return (
                      <tr
                        key={idx}
                        className={isOurs ? "bg-cyan-500/10 font-bold text-cyan-200" : "text-slate-300"}
                      >
                        <td className="py-2.5 px-3">{row.model}</td>
                        <td className="py-2.5 px-3 text-right text-emerald-400">
                          {(row.hidden_recall * 100).toFixed(1)}%
                        </td>
                        <td className="py-2.5 px-3 text-right">
                          {row.overall_pr_auc.toFixed(4)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Conclusion banner */}
            <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-xs font-mono text-emerald-300 flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>{proof.proof_summary}</span>
            </div>
          </div>
        ) : (
          <div className="py-8 text-center text-xs font-mono text-slate-400">
            Click Run to execute the test.
          </div>
        )}

        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-lg bg-purple-600/30 border border-purple-500/40 text-xs font-mono uppercase tracking-wider text-white hover:bg-purple-600/50 transition-all cursor-pointer"
          >
            Close Proof
          </button>
        </div>
      </div>
    </div>
  );
};
