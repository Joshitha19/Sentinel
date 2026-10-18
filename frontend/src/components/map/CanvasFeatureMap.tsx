import React, { useRef, useEffect, useState } from "react";
import { MapPayload, MapPoint } from "../../types";
import { Crosshair, Layers, ZoomIn } from "lucide-react";

interface CanvasMapProps {
  mapPayload: MapPayload | null;
  title?: string;
}

export const CanvasFeatureMap: React.FC<CanvasMapProps> = ({
  mapPayload,
  title = "2D Latent Representation & Discovery Map",
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [hoveredPoint, setHoveredPoint] = useState<MapPoint | null>(null);
  const [pulsePhase, setPulsePhase] = useState<number>(0);

  // Animation loop for pulsing active candidate points
  useEffect(() => {
    let animId: number;
    const animate = () => {
      setPulsePhase((prev) => (prev + 0.05) % (Math.PI * 2));
      animId = requestAnimationFrame(animate);
    };
    animId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animId);
  }, []);

  // Main canvas draw routine
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Handle high-DPI displays
    const dpr = window.devicePixelRatio || 1;
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);

    // Clear background
    ctx.fillStyle = "#070518";
    ctx.fillRect(0, 0, width, height);

    // Draw subtle dark grid
    ctx.strokeStyle = "rgba(168, 85, 247, 0.08)";
    ctx.lineWidth = 1;
    const gridSize = 40;
    for (let x = 0; x < width; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Draw center crosshair reticles
    ctx.strokeStyle = "rgba(0, 240, 255, 0.15)";
    ctx.beginPath();
    ctx.moveTo(width / 2, 0);
    ctx.lineTo(width / 2, height);
    ctx.moveTo(0, height / 2);
    ctx.lineTo(width, height / 2);
    ctx.stroke();

    if (!mapPayload || !mapPayload.points) return;

    // Coordinate mapping from [-100, 100] to canvas [padding, width-padding]
    const padding = 30;
    const mapX = (x: number) => padding + ((x + 100) / 200) * (width - 2 * padding);
    const mapY = (y: number) => padding + ((y + 100) / 200) * (height - 2 * padding);

    // Render points by layers
    // Layer 1: Nominal (Cyan)
    ctx.fillStyle = "rgba(0, 240, 255, 0.35)";
    for (const pt of mapPayload.points) {
      if (pt.type === "nominal") {
        const cx = mapX(pt.x);
        const cy = mapY(pt.y);
        ctx.beginPath();
        ctx.arc(cx, cy, 2.2, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    // Layer 2: Archive Items (Violet)
    ctx.fillStyle = "#A855F7";
    ctx.shadowColor = "rgba(168, 85, 247, 0.6)";
    ctx.shadowBlur = 6;
    for (const pt of mapPayload.points) {
      if (pt.type === "archive") {
        const cx = mapX(pt.x);
        const cy = mapY(pt.y);
        ctx.beginPath();
        ctx.arc(cx, cy, 3.8, 0, Math.PI * 2);
        ctx.fill();
      }
    }
    ctx.shadowBlur = 0;

    // Layer 3: Known Rare (Amber)
    ctx.fillStyle = "#F59E0B";
    ctx.shadowColor = "rgba(245, 158, 11, 0.8)";
    ctx.shadowBlur = 8;
    for (const pt of mapPayload.points) {
      if (pt.type === "known_rare") {
        const cx = mapX(pt.x);
        const cy = mapY(pt.y);
        ctx.beginPath();
        ctx.arc(cx, cy, 4.5, 0, Math.PI * 2);
        ctx.fill();
        // Inner white dot
        ctx.fillStyle = "#FFFFFF";
        ctx.beginPath();
        ctx.arc(cx, cy, 1.5, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "#F59E0B";
      }
    }
    ctx.shadowBlur = 0;

    // Layer 4: Active Candidate Batch (Pulsing Magenta / White rings)
    const pulseRadius = 5.0 + Math.sin(pulsePhase) * 2.5;
    const ringRadius = 10.0 + Math.sin(pulsePhase) * 4.0;

    for (const pt of mapPayload.points) {
      if (pt.type === "candidate") {
        const cx = mapX(pt.x);
        const cy = mapY(pt.y);

        // Pulsing radar ring
        ctx.strokeStyle = `rgba(236, 72, 153, ${0.7 - Math.sin(pulsePhase) * 0.3})`;
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.arc(cx, cy, ringRadius, 0, Math.PI * 2);
        ctx.stroke();

        // Glowing core
        ctx.fillStyle = "#FFFFFF";
        ctx.shadowColor = "#EC4899";
        ctx.shadowBlur = 12;
        ctx.beginPath();
        ctx.arc(cx, cy, pulseRadius, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
      }
    }
  }, [mapPayload, pulsePhase]);

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas || !mapPayload) return;
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    const padding = 30;

    // Invert mapping
    const normX = ((mouseX - padding) / (width - 2 * padding)) * 200 - 100;
    const normY = ((mouseY - padding) / (height - 2 * padding)) * 200 - 100;

    // Find closest point within radius
    let closest: MapPoint | null = null;
    let minDist = 8.0;

    for (const pt of mapPayload.points) {
      const d = Math.hypot(pt.x - normX, pt.y - normY);
      if (d < minDist) {
        minDist = d;
        closest = pt;
      }
    }
    setHoveredPoint(closest);
  };

  return (
    <div className="glass-panel rounded-2xl p-4 sm:p-5 flex flex-col relative overflow-hidden">
      {/* Top Header & Legend */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3 z-10">
        <div>
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-cyan-400" />
            <h3 className="font-display font-bold text-sm tracking-wide text-white">
              {title}
            </h3>
          </div>
          <p className="text-[11px] font-mono text-slate-400 mt-0.5">
            PCA 2D projection · Real vs Novel Candidates
          </p>
        </div>

        {/* Legend */}
        <div className="flex items-center flex-wrap gap-3 text-[10px] font-mono">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400/80 shadow-glow-cyan" />
            <span className="text-slate-300">REAL NORMAL</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400 shadow-glow-amber" />
            <span className="text-slate-300">KNOWN RARE</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-500 shadow-glow" />
            <span className="text-slate-300">ARCHIVE</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-pink-500 animate-ping" />
            <span className="text-slate-300">NEW CANDIDATES</span>
          </div>
        </div>
      </div>

      {/* Canvas Element */}
      <div className="relative w-full h-[360px] sm:h-[420px] rounded-xl overflow-hidden border border-purple-500/20 bg-[#070518]">
        <canvas
          ref={canvasRef}
          onMouseMove={handleMouseMove}
          onMouseLeave={() => setHoveredPoint(null)}
          className="w-full h-full cursor-crosshair"
        />

        {/* Hover Inspector Tooltip */}
        {hoveredPoint && (
          <div className="absolute bottom-3 left-3 bg-[#0B0826]/90 border border-purple-500/40 rounded-lg p-2 text-xs font-mono backdrop-blur-md shadow-xl text-slate-200">
            <div className="text-[10px] text-cyan-300 font-bold uppercase">
              TYPE: {hoveredPoint.type.replace("_", " ")}
            </div>
            <div>X: {hoveredPoint.x.toFixed(2)}, Y: {hoveredPoint.y.toFixed(2)}</div>
          </div>
        )}

        {/* Empty state hint */}
        {(!mapPayload || mapPayload.points.length === 0) && (
          <div className="absolute inset-0 flex items-center justify-center text-xs font-mono text-slate-500">
            Awaiting active training telemetry coordinates...
          </div>
        )}
      </div>
    </div>
  );
};
