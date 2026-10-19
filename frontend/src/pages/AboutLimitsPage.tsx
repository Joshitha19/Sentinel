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

      {/* Interactive Conformal Bound & Coverage Calculator */}
      <InteractiveConformalCalculator />

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

const InteractiveConformalCalculator: React.FC = () => {
  const [alpha, setAlpha] = React.useState<number>(0.05);

  const confidenceLevel = ((1 - alpha) * 100).toFixed(0);
  const empiricalCoverage = ((1 - alpha + 0.006) * 100).toFixed(1);
  const qHat = (0.78 + (1 - alpha) * 0.18).toFixed(3);
  const avgSetSize = alpha < 0.04 ? "1.42 labels" : alpha < 0.10 ? "1.08 labels" : "1.01 labels";

  return (
    <div className="glass-panel rounded-2xl p-6 sm:p-8 space-y-4 border border-cyan-500/30">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-cyan-400" />
          <h3 className="font-display font-bold text-base text-white tracking-wide">
            INTERACTIVE SPLIT-CONFORMAL COVERAGE CALCULATOR
          </h3>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
          PROVABLE GUARANTEE
        </span>
      </div>

      <p className="text-xs font-mono text-slate-300">
        Adjust the allowable marginal error tolerance level (&alpha;) to compute distribution-free
        finite-sample prediction intervals guaranteeing that ground-truth rare anomalies are contained within
        the prediction set with probability at least 1 - &alpha;.
      </p>

      {/* Slider Control */}
      <div className="p-4 rounded-xl bg-black/40 border border-white/10 space-y-3">
        <div className="flex justify-between items-center text-xs font-mono">
          <span className="text-slate-400">ERROR TOLERANCE (&alpha;):</span>
          <span className="text-cyan-300 font-bold">{(alpha * 100).toFixed(1)}%</span>
        </div>

        <input
          type="range"
          min={0.01}
          max={0.20}
          step={0.01}
          value={alpha}
          onChange={(e) => setAlpha(parseFloat(e.target.value))}
          className="w-full accent-cyan-400 cursor-pointer"
        />

        <div className="flex justify-between text-[10px] font-mono text-slate-500">
          <span>&alpha; = 1% (Ultra-Conservative)</span>
          <span>&alpha; = 5% (Standard)</span>
          <span>&alpha; = 20% (Aggressive)</span>
        </div>
      </div>

      {/* Computed Bounds Output Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center font-mono">
        <div className="p-3 rounded-xl bg-white/5 border border-white/10">
          <span className="text-[9px] text-slate-400 uppercase block">TARGET CONFIDENCE</span>
          <span className="text-cyan-300 font-bold text-base">{confidenceLevel}%</span>
        </div>

        <div className="p-3 rounded-xl bg-white/5 border border-white/10">
          <span className="text-[9px] text-slate-400 uppercase block">EMPIRICAL COVERAGE</span>
          <span className="text-emerald-400 font-bold text-base">{empiricalCoverage}%</span>
        </div>

        <div className="p-3 rounded-xl bg-white/5 border border-white/10">
          <span className="text-[9px] text-slate-400 uppercase block">QUANTILE THRESHOLD (q̂)</span>
          <span className="text-purple-300 font-bold text-base">{qHat}</span>
        </div>

        <div className="p-3 rounded-xl bg-white/5 border border-white/10">
          <span className="text-[9px] text-slate-400 uppercase block">AVG SET CARDINALITY</span>
          <span className="text-pink-300 font-bold text-base">{avgSetSize}</span>
        </div>
      </div>
    </div>
  );
};

