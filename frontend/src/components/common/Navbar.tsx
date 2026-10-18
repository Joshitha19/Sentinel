import React from "react";
import { Shield, Activity, Cpu, Sparkles } from "lucide-react";
import { Domain } from "../../types";

interface NavbarProps {
  currentPage: string;
  onPageChange: (page: string) => void;
  selectedDomain: Domain | null;
  domains: Domain[];
  onSelectDomain: (domain: Domain) => void;
  isTraining: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentPage,
  onPageChange,
  selectedDomain,
  domains,
  onSelectDomain,
  isTraining,
}) => {
  const navItems = [
    { id: "control", label: "01 MISSION CONTROL" },
    { id: "training", label: "02 LIVE TRAINING" },
    { id: "candidates", label: "03 CANDIDATE ARCHIVE" },
    { id: "eval", label: "04 BENCHMARKS & PROOF" },
    { id: "about", label: "05 HONEST BOUNDS" },
  ];

  return (
    <header className="sticky top-0 z-50 w-full bg-[#060414]/90 backdrop-blur-xl border-b border-purple-500/20 px-6 py-3.5 transition-all">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand / Logo */}
        <div
          onClick={() => onPageChange("control")}
          className="flex items-center gap-3 cursor-pointer group"
        >
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-purple-600 via-pink-600 to-cyan-400 p-[1px] shadow-glow">
            <div className="w-full h-full bg-[#0B0826] rounded-[11px] flex items-center justify-center">
              <Shield className="w-4 h-4 text-cyan-300 group-hover:scale-110 transition-transform" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-display font-extrabold text-base tracking-[0.25em] text-white">
                SENTINEL
              </span>
              <span className="text-[9px] font-mono tracking-widest px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
                PROPOSED
              </span>
            </div>
            <p className="text-[10px] font-mono tracking-wider text-slate-400 hidden sm:block">
              NOVELTY-DRIVEN ADVERSARIAL LEARNING
            </p>
          </div>
        </div>

        {/* Center Nav Links */}
        <nav className="hidden lg:flex items-center gap-1.5">
          {navItems.map((item) => {
            const active = currentPage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onPageChange(item.id)}
                className={`px-3 py-1.5 rounded-lg text-[11px] font-mono tracking-wider transition-all ${
                  active
                    ? "bg-purple-600/20 text-cyan-300 border border-purple-500/40 shadow-glow"
                    : "text-slate-400 hover:text-white hover:bg-white/5"
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* Right Controls: Domain Switcher & Status */}
        <div className="flex items-center gap-3">
          {/* Domain Dropdown */}
          <div className="relative">
            <select
              value={selectedDomain?.id || "transactions"}
              onChange={(e) => {
                const found = domains.find((d) => d.id === e.target.value);
                if (found) onSelectDomain(found);
              }}
              className="bg-[#120D36] border border-purple-500/30 hover:border-cyan-400 text-xs font-mono tracking-wider text-cyan-200 px-3 py-1.5 rounded-lg outline-none cursor-pointer transition-colors shadow-sm"
            >
              {domains.map((dom) => (
                <option key={dom.id} value={dom.id} className="bg-[#0B0826] text-white">
                  DOMAIN: {dom.name.toUpperCase()}
                </option>
              ))}
            </select>
          </div>

          {/* Engine Status Indicator */}
          <div className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-[#120D36] border border-white/10 text-xs font-mono">
            <div
              className={`w-2 h-2 rounded-full ${
                isTraining
                  ? "bg-cyan-400 animate-ping"
                  : "bg-emerald-400 shadow-glow-cyan"
              }`}
            />
            <span className="text-[10px] text-slate-300 uppercase tracking-widest hidden sm:inline">
              {isTraining ? "ACTIVE RUN" : "IDLE"}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
