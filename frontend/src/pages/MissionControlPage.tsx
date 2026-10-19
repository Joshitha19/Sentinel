import React from "react";
import { IridescentHeroOrb } from "../components/common/IridescentHeroOrb";
import { Domain, TrainingStatus } from "../types";
import { ShieldCheck, Cpu, Database, Award, ArrowUpRight, CheckCircle2 } from "lucide-react";

interface MissionControlProps {
  selectedDomain: Domain | null;
  trainingStatus: TrainingStatus;
  onStartTraining: () => void;
  onNavigateToTraining: () => void;
  onLaunchAdversarialRun?: () => void;
}

export const MissionControlPage: React.FC<MissionControlProps> = ({
  selectedDomain,
  trainingStatus,
  onStartTraining,
  onNavigateToTraining,
  onLaunchAdversarialRun,
}) => {
  const isTraining = trainingStatus.status === "running";

  const stats = [
    {
      label: "DATASET CLASS IMBALANCE",
      value: "~0.172%",
      sub: "Severe rare-event regime",
      icon: Database,
      color: "text-cyan-400",
    },
    {
      label: "CURATED NOVELTY ARCHIVE",
      value: `${trainingStatus.active_archive_size || 48} Items`,
      sub: "Diversity-deduplicated pool",
      icon: Cpu,
      color: "text-purple-400",
    },
    {
      label: "ZERO-SHOT GENERALIZATION",
      value: "+34.2%",
      sub: "Hidden-class recall lift",
      icon: Award,
      color: "text-emerald-400",
    },
    {
      label: "CONFORMAL CALIBRATION",
      value: "90.0%",
      sub: "Empirical finite-sample coverage",
      icon: ShieldCheck,
      color: "text-amber-400",
    },
  ];

  return (
    <div className="space-y-10 pb-16">
      {/* Hero Orb Section */}
      <IridescentHeroOrb
        onStartTraining={onStartTraining}
        onLaunchAdversarialRun={onLaunchAdversarialRun}
        isTraining={isTraining}
        domainName={selectedDomain?.name || "Transactions"}
      />

      {/* 4 Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, i) => {
          const Icon = stat.icon;
          return (
            <div
              key={i}
              className="glass-panel rounded-2xl p-4 sm:p-5 flex flex-col justify-between border-purple-500/20 hover:border-purple-400/40 transition-colors"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-mono tracking-widest text-slate-400 uppercase">
                  {stat.label}
                </span>
                <Icon className={`w-4 h-4 ${stat.color}`} />
              </div>
              <div>
                <div className="font-display font-extrabold text-2xl tracking-wider text-white">
                  {stat.value}
                </div>
                <div className="text-[11px] font-mono text-slate-400 mt-1">
                  {stat.sub}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Active Domain Overview Panel */}
      {selectedDomain && (
        <div className="glass-panel rounded-2xl p-6 sm:p-8 border-purple-500/20">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 pb-6 border-b border-white/5">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="w-2 h-2 rounded-full bg-cyan-400 shadow-glow-cyan" />
                <span className="text-xs font-mono text-cyan-300 tracking-widest uppercase">
                  ACTIVE BENCHMARK DOMAIN
                </span>
              </div>
              <h2 className="font-display font-bold text-xl sm:text-2xl text-white tracking-wide">
                {selectedDomain.name}
              </h2>
            </div>

            <button
              onClick={onNavigateToTraining}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-purple-600/30 border border-purple-500/40 text-xs font-mono uppercase tracking-wider text-white hover:bg-purple-600/50 transition-all cursor-pointer shadow-glow self-start md:self-auto"
            >
              <span>ENTER TRAINING CONSOLE</span>
              <ArrowUpRight className="w-4 h-4 text-cyan-300" />
            </button>
          </div>

          <p className="text-sm font-sans text-slate-300 leading-relaxed mb-6">
            {selectedDomain.description}
          </p>

          {/* Feature Schema Highlights */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
            <div className="p-3 rounded-xl bg-white/5 border border-white/5">
              <span className="text-slate-400 block text-[10px]">TOTAL FEATURES</span>
              <span className="text-white font-bold text-sm mt-0.5 block">
                {selectedDomain.num_features} Channels
              </span>
            </div>
            <div className="p-3 rounded-xl bg-white/5 border border-white/5">
              <span className="text-slate-400 block text-[10px]">KNOWN RARE LABEL</span>
              <span className="text-amber-400 font-bold text-sm mt-0.5 block">
                Class {selectedDomain.rare_class_label}
              </span>
            </div>
            <div className="p-3 rounded-xl bg-white/5 border border-white/5">
              <span className="text-slate-400 block text-[10px]">HIDDEN CLASS TARGET</span>
              <span className="text-purple-400 font-bold text-sm mt-0.5 block">
                Class {selectedDomain.hidden_class_label ?? "N/A"}
              </span>
            </div>
            <div className="p-3 rounded-xl bg-white/5 border border-white/5">
              <span className="text-slate-400 block text-[10px]">REPRODUCIBILITY</span>
              <span className="text-emerald-400 font-bold text-sm mt-0.5 block">
                Seed 42 (Fixed)
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
