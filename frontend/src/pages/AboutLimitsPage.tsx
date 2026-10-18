import React from "react";
import { ShieldAlert, BookOpen, AlertCircle, CheckCircle2, FileText } from "lucide-react";

export const AboutLimitsPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-16">
      {/* Header */}
      <div className="glass-panel rounded-2xl p-6 sm:p-8 border-purple-500/20">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-9 h-9 rounded-xl bg-purple-600/20 border border-purple-500/40 flex items-center justify-center">
            <BookOpen className="w-5 h-5 text-purple-300" />
          </div>
          <h2 className="font-display font-bold text-2xl text-white tracking-wide">
            SENTINEL // RESEARCH SPECIFICATION & HONEST BOUNDS
          </h2>
        </div>
        <p className="text-xs font-mono text-cyan-300">
          Self-Evolving Novelty and Rare-Event Intelligence through Learning
        </p>
      </div>

      {/* Critical Explicit Non-Claims Banner */}
      <div className="p-6 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-200 space-y-3">
        <div className="flex items-center gap-2 font-display font-bold text-sm tracking-wider uppercase text-amber-300">
          <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0" />
          <span>MANDATORY RESEARCH DISCLOSURE & BOUNDARIES</span>
        </div>
        <p className="text-xs font-sans leading-relaxed text-amber-200/90">
          <strong>SENTINEL is a PROPOSED research framework</strong> designed to explore adversarial robustness and novelty-driven synthetic expansion in extreme class-imbalanced environments.
        </p>
        <ul className="text-xs font-mono space-y-2 pt-2 border-t border-amber-500/20">
          <li className="flex items-start gap-2">
            <span className="text-amber-400 font-bold">✕ NO REAL CLINICAL DIAGNOSES:</span>
            <span>The system does not detect or diagnose real-world human illnesses. Medical biomarkers and symptom records are simulated or anonymized benchmarks.</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-amber-400 font-bold">✕ NO REAL FRAUD DISCOVERY:</span>
            <span>Generated candidates are synthetic mathematical vectors designed to identify detector blind spots, not actual criminal transaction traces.</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-emerald-400 font-bold">✓ WHAT IT DOES:</span>
            <span>It measurably improves detector generalization and zero-shot recall on held-out rare subclasses by training against diverse, plausible, and hard-to-detect synthetic vectors.</span>
          </li>
        </ul>
      </div>

      {/* Mathematical Formulation Section */}
      <div className="glass-panel rounded-2xl p-6 sm:p-8 space-y-4">
        <h3 className="font-display font-bold text-base text-white tracking-wide flex items-center gap-2">
          <FileText className="w-4 h-4 text-cyan-400" />
          <span>MATHEMATICAL OBJECTIVE FORMULATION</span>
        </h3>
        <p className="text-xs font-mono text-slate-300 leading-relaxed">
          Traditional generative methods (e.g., CTGAN or standard GANs) maximize only Realism, tending to collapse onto existing high-density rare clusters or generate near-duplicates. SENTINEL formulates generation as a multi-objective reward maximization problem:
        </p>

        <div className="p-4 rounded-xl bg-[#09061C] border border-purple-500/30 text-xs font-mono text-cyan-300 space-y-2">
          <div>ℛ(x) = α · Realism(x) + β · Novelty(x) + γ · Hardness(x)</div>
          <div className="text-slate-400 text-[11px]">
            where:
            <br />• Realism(x) = D(x) - λ · DomainPenalty(x)
            <br />• Novelty(x) = (1/k) ∑ d_knn(x, D_rare ∪ Archive)  [differentiable via torch.cdist]
            <br />• Hardness(x) = 1.0 - P_detector(rare | x)
            <br />• Loss_Generator = -ℛ(x)
          </div>
        </div>
      </div>

      {/* Assumptions & Known Failure Modes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div className="glass-panel rounded-2xl p-5">
          <h4 className="font-display font-bold text-sm text-white mb-2 text-purple-300">
            SYSTEM ASSUMPTIONS
          </h4>
          <ul className="text-xs font-mono text-slate-400 space-y-2">
            <li>• Reference features have continuous or relaxed categorical representations.</li>
            <li>• Domain constraints can be expressed via differentiable or heuristic penalty functions.</li>
            <li>• Exchangeability holds on calibration data for valid conformal coverage.</li>
          </ul>
        </div>

        <div className="glass-panel rounded-2xl p-5">
          <h4 className="font-display font-bold text-sm text-white mb-2 text-pink-300">
            KNOWN LIMITS & RISKS
          </h4>
          <ul className="text-xs font-mono text-slate-400 space-y-2">
            <li>• Setting beta too high relative to alpha can produce implausible fantasy vectors.</li>
            <li>• Extreme class imbalance (e.g. &lt;0.01%) requires carefully calibrated positive sample weights.</li>
            <li>• Requires human-in-the-loop review to curate the candidate archive before retraining.</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
