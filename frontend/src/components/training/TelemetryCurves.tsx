import React from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";
import { Sliders, Activity, TrendingUp } from "lucide-react";
import { TrainingWeights } from "../../types";

interface TelemetryProps {
  history: any[];
  weights: TrainingWeights;
  onAdjustWeights: (weights: TrainingWeights) => void;
  isTraining: boolean;
}

export const TelemetryCurves: React.FC<TelemetryProps> = ({
  history,
  weights,
  onAdjustWeights,
  isTraining,
}) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Chart 1: Realism, Novelty & Hardness Rewards */}
      <div className="lg:col-span-2 glass-panel rounded-2xl p-4 sm:p-5 flex flex-col justify-between">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-purple-400" />
            <h3 className="font-display font-bold text-sm text-white tracking-wide">
              LIVE MULTI-OBJECTIVE REWARDS
            </h3>
          </div>
          <span className="text-[10px] font-mono text-cyan-300">
            {history.length > 0 ? `${history.length} ROUNDS RECORDED` : "AWAITING TELEMETRY"}
          </span>
        </div>

        <div className="w-full h-56">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={history} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(168, 85, 247, 0.1)" />
              <XAxis dataKey="round" stroke="#64748B" fontSize={10} fontStyle="mono" />
              <YAxis stroke="#64748B" fontSize={10} fontStyle="mono" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0B0826",
                  border: "1px solid rgba(168, 85, 247, 0.4)",
                  borderRadius: "8px",
                  fontSize: "11px",
                  fontFamily: "Space Grotesk, monospace",
                }}
              />
              <Legend wrapperStyle={{ fontSize: "10px", fontFamily: "Space Grotesk" }} />
              <Line
                type="monotone"
                dataKey="realism"
                name="Realism (Alpha)"
                stroke="#10B981"
                strokeWidth={2}
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="novelty"
                name="Novelty (Beta)"
                stroke="#A855F7"
                strokeWidth={2}
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="hardness"
                name="Hardness (Gamma)"
                stroke="#EC4899"
                strokeWidth={2}
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="reward"
                name="Total Combined Reward"
                stroke="#00F0FF"
                strokeWidth={2.5}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Sliders Control Panel */}
      <div className="glass-panel rounded-2xl p-4 sm:p-5 flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-2 mb-4">
            <Sliders className="w-4 h-4 text-cyan-400" />
            <h3 className="font-display font-bold text-sm text-white tracking-wide">
              OBJECTIVE SLIDERS
            </h3>
          </div>
          <p className="text-[11px] font-mono text-slate-400 mb-5 leading-relaxed">
            Interactively guide the generator in real time. Weights steer the curriculum balance.
          </p>

          {/* Slider 1: Alpha (Realism) */}
          <div className="mb-4">
            <div className="flex items-center justify-between text-xs font-mono mb-1.5">
              <span className="text-emerald-300">α REALISM:</span>
              <span className="text-white font-bold">{weights.alpha.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="3.0"
              step="0.1"
              value={weights.alpha}
              onChange={(e) =>
                onAdjustWeights({ ...weights, alpha: parseFloat(e.target.value) })
              }
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-400"
            />
          </div>

          {/* Slider 2: Beta (Novelty) */}
          <div className="mb-4">
            <div className="flex items-center justify-between text-xs font-mono mb-1.5">
              <span className="text-purple-300">β NOVELTY:</span>
              <span className="text-white font-bold">{weights.beta.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="3.0"
              step="0.1"
              value={weights.beta}
              onChange={(e) =>
                onAdjustWeights({ ...weights, beta: parseFloat(e.target.value) })
              }
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
          </div>

          {/* Slider 3: Gamma (Hardness) */}
          <div className="mb-4">
            <div className="flex items-center justify-between text-xs font-mono mb-1.5">
              <span className="text-pink-300">γ HARDNESS:</span>
              <span className="text-white font-bold">{weights.gamma.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="3.0"
              step="0.1"
              value={weights.gamma}
              onChange={(e) =>
                onAdjustWeights({ ...weights, gamma: parseFloat(e.target.value) })
              }
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-pink-500"
            />
          </div>
        </div>

        <div className="p-2.5 rounded-lg bg-white/5 border border-white/5 text-[10px] font-mono text-slate-400">
          Loss_G = -(α·Realism + β·Novelty + γ·Hardness)
        </div>
      </div>
    </div>
  );
};
