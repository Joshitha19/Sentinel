import React from "react";
import { AnimatedLoopDiagram } from "../components/training/AnimatedLoopDiagram";
import { TelemetryCurves } from "../components/training/TelemetryCurves";
import { CanvasFeatureMap } from "../components/map/CanvasFeatureMap";
import { TrainingStatus, TrainingWeights, MapPayload } from "../types";
import { Play, Square, RefreshCw, Cpu } from "lucide-react";

interface LiveTrainingPageProps {
  status: TrainingStatus;
  history: any[];
  mapPayload: MapPayload | null;
  weights: TrainingWeights;
  onStartTraining: () => void;
  onStopTraining: () => void;
  onAdjustWeights: (weights: TrainingWeights) => void;
  domainName: string;
}

export const LiveTrainingPage: React.FC<LiveTrainingPageProps> = ({
  status,
  history,
  mapPayload,
  weights,
  onStartTraining,
  onStopTraining,
  onAdjustWeights,
  domainName,
}) => {
  const isTraining = status.status === "running";

  return (
    <div className="space-y-6 pb-16">
      {/* Page Header with Action Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-panel rounded-2xl p-5">
        <div>
          <div className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-cyan-400" />
            <h2 className="font-display font-bold text-lg sm:text-xl text-white tracking-wide">
              LIVE ADVERSARIAL TRAINING CONSOLE
            </h2>
          </div>
          <p className="text-xs font-mono text-slate-400 mt-0.5">
            Domain: {domainName.toUpperCase()} · Self-Play Co-Evolution Engine
          </p>
        </div>

        <div className="flex items-center gap-3">
          {!isTraining ? (
            <button
              onClick={onStartTraining}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-400/40 text-xs font-mono uppercase tracking-wider text-cyan-200 transition-all shadow-glow-cyan cursor-pointer"
            >
              <Play className="w-4 h-4 text-cyan-300 fill-cyan-300" />
              <span>START ADVERSARIAL RUN</span>
            </button>
          ) : (
            <button
              onClick={onStopTraining}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/40 text-xs font-mono uppercase tracking-wider text-rose-300 transition-all cursor-pointer"
            >
              <Square className="w-4 h-4 text-rose-400 fill-rose-400" />
              <span>STOP RUN</span>
            </button>
          )}
        </div>
      </div>

      {/* 5-Node Animated Circuit Diagram */}
      <AnimatedLoopDiagram
        isTraining={isTraining}
        activeRound={status.round}
        totalRounds={status.total_rounds}
      />

      {/* 2D Canvas Feature Scatter Map */}
      <CanvasFeatureMap
        mapPayload={mapPayload}
        title={`2D Latent Representation & Discovery Map — ${domainName}`}
      />

      {/* Live Curves & Interactive Weight Sliders */}
      <TelemetryCurves
        history={history}
        weights={weights}
        onAdjustWeights={onAdjustWeights}
        isTraining={isTraining}
      />
    </div>
  );
};
