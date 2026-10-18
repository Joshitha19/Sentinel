import React from "react";
import { motion } from "framer-motion";
import { Cpu, ShieldCheck, Compass, Eye, Archive, ArrowRight } from "lucide-react";

interface LoopProps {
  isTraining: boolean;
  activeRound: number;
  totalRounds: number;
}

export const AnimatedLoopDiagram: React.FC<LoopProps> = ({
  isTraining,
  activeRound,
  totalRounds,
}) => {
  const nodes = [
    {
      id: "gen",
      name: "1. GENERATOR",
      desc: "Latent MLP (Continuous + Gumbel)",
      icon: Cpu,
      color: "border-cyan-400 text-cyan-300 shadow-glow-cyan",
      tag: "SYNTHESIS"
    },
    {
      id: "realism",
      name: "2. REALISM GATE",
      desc: "Discriminator + Domain Rules",
      icon: ShieldCheck,
      color: "border-emerald-400 text-emerald-300",
      tag: "PLAUSIBILITY"
    },
    {
      id: "novelty",
      name: "3. NOVELTY ENGINE",
      desc: "Differentiable k-NN cdist",
      icon: Compass,
      color: "border-purple-400 text-purple-300 shadow-glow",
      tag: "DIVERSITY"
    },
    {
      id: "detector",
      name: "4. DETECTOR",
      desc: "Hardness = 1 - P(rare)",
      icon: Eye,
      color: "border-pink-400 text-pink-300",
      tag: "BLINDSPOTS"
    },
    {
      id: "archive",
      name: "5. ARCHIVE GATE",
      desc: "Human Triage & Retraining Pool",
      icon: Archive,
      color: "border-amber-400 text-amber-300 shadow-glow-amber",
      tag: "CURATION"
    },
  ];

  return (
    <div className="glass-panel rounded-2xl p-4 sm:p-6 relative overflow-hidden">
      {/* Top Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="font-display font-bold text-sm tracking-wide text-white flex items-center gap-2">
            <span>SENTINEL CLOSED-LOOP ADVERSARIAL CIRCUIT</span>
            {isTraining && (
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
            )}
          </h3>
          <p className="text-[11px] font-mono text-slate-400 mt-0.5">
            Round {activeRound} of {totalRounds} · Tripartite Objective Co-Evolution
          </p>
        </div>

        <div className="text-right font-mono text-[11px]">
          <span className="text-slate-400">STATE: </span>
          <span className={isTraining ? "text-cyan-400 font-bold" : "text-slate-400"}>
            {isTraining ? "STREAMING ITERATIONS" : "STANDBY"}
          </span>
        </div>
      </div>

      {/* 5-Node Interactive Pipeline */}
      <div className="grid grid-cols-1 sm:grid-cols-5 gap-3 relative">
        {nodes.map((node, index) => {
          const Icon = node.icon;
          return (
            <motion.div
              key={node.id}
              animate={isTraining ? { y: [-2, 2, -2] } : {}}
              transition={{ duration: 3, delay: index * 0.4, repeat: Infinity }}
              className={`p-3.5 rounded-xl bg-[#0F0A2C]/90 border ${
                node.color
              } flex flex-col justify-between transition-all hover:scale-[1.02]`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="w-7 h-7 rounded-lg bg-white/5 flex items-center justify-center">
                    <Icon className="w-4 h-4" />
                  </div>
                  <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-white/5 text-slate-300">
                    {node.tag}
                  </span>
                </div>
                <div className="font-display font-bold text-xs tracking-wider text-white">
                  {node.name}
                </div>
                <div className="text-[10px] font-mono text-slate-400 mt-1 leading-snug">
                  {node.desc}
                </div>
              </div>

              {/* Conduits indicator */}
              <div className="mt-3 pt-2 border-t border-white/5 flex items-center justify-between text-[9px] font-mono text-slate-500">
                <span>FEEDBACK</span>
                {index < 4 && (
                  <ArrowRight className="w-3 h-3 text-purple-400/60 hidden sm:block" />
                )}
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};
