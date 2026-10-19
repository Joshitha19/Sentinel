import React from "react";
import { motion } from "framer-motion";
import { ArrowRight, Sparkles, Terminal } from "lucide-react";

interface HeroOrbProps {
  onStartTraining: () => void;
  onLaunchAdversarialRun?: () => void;
  isTraining: boolean;
  domainName: string;
}

export const IridescentHeroOrb: React.FC<HeroOrbProps> = ({
  onStartTraining,
  onLaunchAdversarialRun,
  isTraining,
  domainName,
}) => {
  return (
    <div className="relative w-full py-12 md:py-20 flex flex-col items-center justify-center overflow-hidden">
      {/* Background ambient lighting glows */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[550px] h-[550px] rounded-full bg-purple-600/15 blur-[120px] pointer-events-none" />
      <div className="absolute top-1/3 left-2/3 -translate-x-1/2 -translate-y-1/2 w-[350px] h-[350px] rounded-full bg-pink-600/10 blur-[90px] pointer-events-none" />
      <div className="absolute top-2/3 left-1/3 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] rounded-full bg-cyan-500/10 blur-[90px] pointer-events-none" />

      {/* Floating secondary spheres from reference */}
      <motion.div
        animate={{ y: [-15, 15, -15], x: [-10, 10, -10] }}
        transition={{ duration: 7, repeat: Infinity, ease: "easeInOut" }}
        className="absolute top-12 left-[12%] md:left-[22%] w-16 h-16 md:w-24 md:h-24 rounded-full iridescent-secondary-orb pointer-events-none opacity-60"
      />
      <motion.div
        animate={{ y: [12, -12, 12], x: [8, -8, 8] }}
        transition={{ duration: 9, repeat: Infinity, ease: "easeInOut" }}
        className="absolute bottom-10 right-[10%] md:right-[20%] w-20 h-20 md:w-28 md:h-28 rounded-full iridescent-secondary-orb pointer-events-none opacity-50"
      />

      {/* Main Iridescent Sphere */}
      <div className="relative z-10 flex flex-col items-center justify-center">
        <motion.div
          animate={{ scale: [1, 1.02, 1], rotate: [0, 4, 0] }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
          className="relative w-64 h-64 sm:w-80 sm:h-80 md:w-96 md:h-96 rounded-full iridescent-orb flex items-center justify-center shadow-2xl"
        >
          {/* Inner specular gloss highlight */}
          <div className="absolute top-6 left-10 w-24 h-16 rounded-full bg-white/20 blur-md rotate-[-35deg] pointer-events-none" />
          <div className="absolute bottom-8 right-12 w-28 h-20 rounded-full bg-pink-500/25 blur-lg pointer-events-none" />

          {/* Central Typography Overlay echoing "PROJECT TWELVE" reference */}
          <div className="text-center z-20 px-4">
            <h1 className="font-display font-extrabold text-3xl sm:text-5xl md:text-6xl tracking-[0.18em] text-white uppercase drop-shadow-[0_10px_25px_rgba(0,0,0,0.8)]">
              SENTINEL
            </h1>
            <p className="mt-1 sm:mt-2 text-[10px] sm:text-xs font-mono tracking-[0.35em] text-cyan-300 uppercase">
              NOVELTY ENGINE // {domainName.toUpperCase()}
            </p>
          </div>
        </motion.div>

        {/* Minimalist White Dash and Action Button matching reference */}
        <div className="mt-8 flex flex-col items-center gap-4 z-20">
          <div className="w-12 h-[2px] bg-white/80 shadow-glow" />

          <button
            onClick={onLaunchAdversarialRun || onStartTraining}
            disabled={isTraining}
            className="group flex items-center gap-3 px-6 py-2.5 rounded-lg wireframe-btn text-xs font-mono uppercase tracking-[0.2em] text-white hover:text-cyan-300 transition-all cursor-pointer disabled:opacity-50"
          >
            <span>{isTraining ? "ACTIVE TRAINING IN PROGRESS..." : "LAUNCH ADVERSARIAL RUN"}</span>
            <ArrowRight className="w-4 h-4 text-cyan-400 group-hover:translate-x-1.5 transition-transform" />
          </button>

          <p className="max-w-md text-center text-[11px] font-sans text-slate-400 leading-relaxed px-4">
            Generates plausible, novel, hard-to-detect synthetic candidates to stress-test
            and expand detection boundaries against evasive rare-event drift.
          </p>
        </div>
      </div>
    </div>
  );
};
