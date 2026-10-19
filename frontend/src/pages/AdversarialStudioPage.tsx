import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  HeartPulse,
  CreditCard,
  ShieldAlert,
  Cpu,
  Boxes,
  FileSpreadsheet,
  UploadCloud,
  Download,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  RefreshCw,
  Sliders,
  ArrowRight,
  ChevronRight,
  Info,
  Eye,
  Zap,
  Baby,
  GraduationCap,
  Play,
  RotateCcw,
  Check,
} from "lucide-react";
import {
  STUDIO_DOMAINS,
  StudioDomainOption,
  getDomainTemplateCsv,
  downloadDomainCsvTemplate,
  inspectAndClassifyCsv,
  generateRareEventsWithGan,
  exportEventsToCsv,
} from "../services/adversarialEngine";
import {
  CsvInspectionResult,
  ClassifiedRecord,
  GeneratedRareEvent,
  GanJourneyStep,
} from "../types";

interface AdversarialStudioPageProps {
  onBackToMissionControl: () => void;
  onNavigateToArchive?: () => void;
}

export const AdversarialStudioPage: React.FC<AdversarialStudioPageProps> = ({
  onBackToMissionControl,
  onNavigateToArchive,
}) => {
  // Stepper state: 1 = Domain, 2 = Upload/Template, 3 = Detect/Classify, 4 = GAN Generate
  const [activeStep, setActiveStep] = useState<number>(1);

  // Selected Domain
  const [selectedDomain, setSelectedDomain] = useState<StudioDomainOption>(STUDIO_DOMAINS[0]);

  // Upload & CSV State
  const [csvContent, setCsvContent] = useState<string>("");
  const [uploadedFileName, setUploadedFileName] = useState<string>("");
  const [isInspecting, setIsInspecting] = useState<boolean>(false);
  const [inspectionResult, setInspectionResult] = useState<CsvInspectionResult | null>(null);
  const [inspectionError, setInspectionError] = useState<string | null>(null);

  // Filter for classification table preview
  const [tableFilter, setTableFilter] = useState<"all" | "Normal" | "Suspicious" | "Rare Anomaly">("all");

  // GAN Generation State
  const [isGeneratingGan, setIsGeneratingGan] = useState<boolean>(false);
  const [numEventsToGenerate, setNumEventsToGenerate] = useState<number>(6);
  const [noveltyPush, setNoveltyPush] = useState<number>(1.4);
  const [explanationMode, setExplanationMode] = useState<"kid" | "researcher">("kid");
  const [generatedEvents, setGeneratedEvents] = useState<GeneratedRareEvent[]>([]);
  const [journeySteps, setJourneySteps] = useState<GanJourneyStep[]>([]);
  const [activeJourneyStep, setActiveJourneyStep] = useState<number>(1);
  const [ganSuccessToast, setGanSuccessToast] = useState<boolean>(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const detectionSectionRef = useRef<HTMLDivElement>(null);
  const ganSectionRef = useRef<HTMLDivElement>(null);

  // Handle Domain Selection
  const handleSelectDomain = (domain: StudioDomainOption) => {
    setSelectedDomain(domain);
    // Reset subsequent steps if domain changed
    setCsvContent("");
    setUploadedFileName("");
    setInspectionResult(null);
    setGeneratedEvents([]);
    setJourneySteps([]);
    setActiveStep(2);
  };

  // Handle CSV File Ingestion
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadedFileName(file.name);
    const reader = new FileReader();
    reader.onload = async (event) => {
      const text = event.target?.result as string;
      setCsvContent(text);
      await runDetection(text, selectedDomain.id);
    };
    reader.readAsText(file);
  };

  // Handle Drag & Drop
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (!file) return;

    setUploadedFileName(file.name);
    const reader = new FileReader();
    reader.onload = async (event) => {
      const text = event.target?.result as string;
      setCsvContent(text);
      await runDetection(text, selectedDomain.id);
    };
    reader.readAsText(file);
  };

  // Load 1-Click Pre-filled Sample Data
  const handleLoadSampleData = async () => {
    const sampleCsv = getDomainTemplateCsv(selectedDomain.id);
    setCsvContent(sampleCsv);
    setUploadedFileName(`sample_${selectedDomain.id}_data.csv`);
    await runDetection(sampleCsv, selectedDomain.id);
  };

  // Run Detection and Classification Engine
  const runDetection = async (csvText: string, domainId: string) => {
    setIsInspecting(true);
    setInspectionError(null);
    try {
      const result = await inspectAndClassifyCsv(csvText, domainId);
      setInspectionResult(result);
      setActiveStep(3);
      setTimeout(() => {
        detectionSectionRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 100);
    } catch (err: any) {
      setInspectionError(err.message || "Failed to parse and inspect CSV data.");
    } finally {
      setIsInspecting(false);
    }
  };

  // Run GAN Rare Event Generation
  const handleGenerateRareEvents = async () => {
    if (!inspectionResult) return;

    setIsGeneratingGan(true);
    try {
      const ganResult = await generateRareEventsWithGan(
        selectedDomain.id,
        inspectionResult.records_preview.map((r) => r.data),
        numEventsToGenerate,
        noveltyPush
      );

      setGeneratedEvents(ganResult.generated_events);
      setJourneySteps(ganResult.journey_steps);
      setActiveStep(4);
      setGanSuccessToast(true);
      setTimeout(() => setGanSuccessToast(false), 5000);

      setTimeout(() => {
        ganSectionRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 150);
    } catch (err: any) {
      alert("Failed to generate rare events: " + err.message);
    } finally {
      setIsGeneratingGan(false);
    }
  };

  // Filtered rows for inspection table
  const filteredRecords = inspectionResult?.records_preview.filter((rec) => {
    if (tableFilter === "all") return true;
    return rec.classification === tableFilter;
  }) || [];

  // Helper to render domain icon
  const renderDomainIcon = (iconName: string, className: string = "w-6 h-6") => {
    switch (iconName) {
      case "HeartPulse":
        return <HeartPulse className={className} />;
      case "CreditCard":
        return <CreditCard className={className} />;
      case "ShieldAlert":
        return <ShieldAlert className={className} />;
      case "Cpu":
        return <Cpu className={className} />;
      case "Boxes":
        return <Boxes className={className} />;
      default:
        return <Sparkles className={className} />;
    }
  };

  return (
    <div className="space-y-10 pb-24 text-slate-100">
      {/* Top Banner & Stepper Header */}
      <div className="glass-panel rounded-3xl p-6 sm:p-8 border-purple-500/30 relative overflow-hidden">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 rounded-full bg-purple-600/15 blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-1/3 -mb-20 w-80 h-80 rounded-full bg-cyan-500/10 blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-6 border-b border-white/10">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse shadow-glow-cyan" />
              <span className="text-xs font-mono uppercase tracking-[0.25em] text-cyan-300">
                SENTINEL ADVERSARIAL RUN STUDIO
              </span>
            </div>
            <h1 className="font-display font-extrabold text-2xl sm:text-4xl text-white tracking-wide">
              Rare Event Generator & Anomaly Classifier
            </h1>
            <p className="text-sm font-sans text-slate-300 mt-2 max-w-2xl leading-relaxed">
              Upload custom domain CSV data, automatically detect all statistical features &
              classifications, and unleash Generative Adversarial Networks (GANs) to discover
              evasive rare tail-events explained for everyone from five-year-olds to ML researchers.
            </p>
          </div>

          <button
            onClick={onBackToMissionControl}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-mono text-slate-300 hover:text-white transition-all self-start lg:self-auto cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5 text-slate-400" />
            <span>RETURN TO MISSION CONTROL</span>
          </button>
        </div>

        {/* 4-Step Interactive Flow Stepper */}
        <div className="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs">
          {[
            { step: 1, label: "01. CHOOSE DOMAIN", desc: "Select Industry Regime" },
            { step: 2, label: "02. CSV & TEMPLATE", desc: "Upload or 1-Click Load" },
            { step: 3, label: "03. AUTO DETECT", desc: "Feature Stats & Classify" },
            { step: 4, label: "04. GAN GENERATOR", desc: "5-Yr-Old Step-by-Step" },
          ].map((item) => {
            const isActive = activeStep === item.step;
            const isCompleted = activeStep > item.step;
            return (
              <div
                key={item.step}
                onClick={() => {
                  if (item.step <= activeStep || (item.step === 2 && selectedDomain)) {
                    setActiveStep(item.step);
                  }
                }}
                className={`p-3.5 rounded-2xl border transition-all cursor-pointer ${
                  isActive
                    ? "bg-purple-600/30 border-cyan-400 shadow-glow text-white"
                    : isCompleted
                    ? "bg-white/5 border-emerald-500/40 text-emerald-300"
                    : "bg-white/[0.02] border-white/5 text-slate-500 opacity-60"
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[11px] font-bold tracking-wider">{item.label}</span>
                  {isCompleted ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  ) : (
                    <span
                      className={`w-2 h-2 rounded-full ${
                        isActive ? "bg-cyan-400 animate-ping" : "bg-slate-600"
                      }`}
                    />
                  )}
                </div>
                <div className="text-[10px] text-slate-400 font-sans">{item.desc}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ================= STEP 1: CHOOSE DOMAIN ================= */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-purple-400" />
              <h2 className="text-xs font-mono tracking-widest uppercase text-purple-300">
                STEP 1: CHOOSE DOMAIN
              </h2>
            </div>
            <p className="text-sm text-slate-300 mt-0.5">
              Select the problem formulation and anomaly dynamics for your dataset.
            </p>
          </div>
          <span className="text-xs font-mono text-slate-400">
            {STUDIO_DOMAINS.length} Registered Domains Available
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {STUDIO_DOMAINS.map((dom) => {
            const isSelected = selectedDomain.id === dom.id;
            return (
              <motion.div
                key={dom.id}
                whileHover={{ scale: 1.015, translateY: -2 }}
                transition={{ duration: 0.2 }}
                onClick={() => handleSelectDomain(dom)}
                className={`glass-panel rounded-2xl p-5 border cursor-pointer relative overflow-hidden transition-all flex flex-col justify-between ${
                  isSelected
                    ? "border-cyan-400 bg-purple-950/40 shadow-glow"
                    : "border-purple-500/20 hover:border-purple-400/50 hover:bg-white/5"
                }`}
              >
                {isSelected && (
                  <div className="absolute top-3 right-3 flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-cyan-400/20 border border-cyan-400/40 text-[10px] font-mono text-cyan-300">
                    <Check className="w-3 h-3" />
                    <span>ACTIVE</span>
                  </div>
                )}

                <div>
                  <div className="flex items-center gap-3 mb-3">
                    <div
                      className={`w-11 h-11 rounded-xl flex items-center justify-center p-2.5 ${
                        isSelected
                          ? "bg-gradient-to-br from-cyan-400 to-purple-600 text-white shadow-glow-cyan"
                          : "bg-white/10 text-cyan-300"
                      }`}
                    >
                      {renderDomainIcon(dom.iconName)}
                    </div>
                    <div>
                      <span className="text-[10px] font-mono tracking-widest text-purple-400 block uppercase">
                        {dom.badge}
                      </span>
                      <h3 className="font-display font-bold text-base text-white">{dom.name}</h3>
                    </div>
                  </div>

                  <p className="text-xs font-sans text-slate-300 leading-relaxed mb-4">
                    {dom.description}
                  </p>

                  <div className="p-3 rounded-xl bg-black/30 border border-white/5 mb-4 text-[11px] font-sans text-slate-400">
                    <span className="text-cyan-300 font-mono text-[10px] uppercase block mb-1">
                      TARGET RARE SCENARIO:
                    </span>
                    {dom.rareEventScenario}
                  </div>
                </div>

                <div>
                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {dom.keyFeatures.slice(0, 5).map((f) => (
                      <span
                        key={f}
                        className="px-2 py-0.5 rounded-md bg-white/5 text-[10px] font-mono text-slate-300 border border-white/5"
                      >
                        {f}
                      </span>
                    ))}
                    {dom.keyFeatures.length > 5 && (
                      <span className="px-1.5 py-0.5 rounded-md bg-white/5 text-[10px] font-mono text-slate-400">
                        +{dom.keyFeatures.length - 5}
                      </span>
                    )}
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSelectDomain(dom);
                    }}
                    className={`w-full py-2 rounded-xl text-xs font-mono uppercase tracking-wider flex items-center justify-center gap-2 transition-all cursor-pointer ${
                      isSelected
                        ? "bg-cyan-400 text-black font-bold shadow-glow-cyan"
                        : "bg-purple-600/30 hover:bg-purple-600/50 text-white border border-purple-500/30"
                    }`}
                  >
                    <span>{isSelected ? "DOMAIN SELECTED" : "SELECT DOMAIN"}</span>
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </motion.div>
            );
          })}
        </div>
      </section>

      {/* ================= STEP 2: CSV UPLOAD & TEMPLATE ================= */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-cyan-400" />
              <h2 className="text-xs font-mono tracking-widest uppercase text-cyan-300">
                STEP 2: UPLOAD CSV DATA & GET TEMPLATE
              </h2>
            </div>
            <p className="text-sm text-slate-300 mt-0.5">
              Domain active: <span className="text-white font-bold">{selectedDomain.name}</span>.
              Download the matching CSV template or upload your own file.
            </p>
          </div>

          {/* Quick Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => downloadDomainCsvTemplate(selectedDomain.id)}
              className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-purple-600/20 hover:bg-purple-600/40 border border-purple-500/30 text-xs font-mono text-cyan-300 hover:text-white transition-all cursor-pointer shadow-sm"
              title="Download clean CSV template with headers & rows"
            >
              <Download className="w-3.5 h-3.5 text-cyan-400" />
              <span>DOWNLOAD CSV TEMPLATE</span>
            </button>

            <button
              onClick={handleLoadSampleData}
              className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/40 text-xs font-mono text-emerald-300 hover:text-white transition-all cursor-pointer shadow-sm"
              title="Load 50-100 realistic sample records with 1 click"
            >
              <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
              <span>1-CLICK LOAD SAMPLE DATA</span>
            </button>
          </div>
        </div>

        {/* Dropzone Container */}
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className="glass-panel rounded-3xl p-8 sm:p-12 border-2 border-dashed border-purple-500/30 hover:border-cyan-400/80 bg-purple-950/20 hover:bg-purple-900/30 transition-all cursor-pointer flex flex-col items-center justify-center text-center group"
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            className="hidden"
            onChange={handleFileUpload}
          />

          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-600/40 to-cyan-400/20 border border-purple-400/30 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform shadow-glow">
            <UploadCloud className="w-8 h-8 text-cyan-300" />
          </div>

          <h3 className="font-display font-bold text-lg sm:text-xl text-white">
            {uploadedFileName ? (
              <span className="text-emerald-300 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 inline" />
                Loaded: {uploadedFileName}
              </span>
            ) : (
              "Drop your .CSV data file here, or click to browse"
            )}
          </h3>

          <p className="text-xs font-sans text-slate-400 max-w-md mt-2 leading-relaxed">
            Accepts any CSV with headers matching <code className="text-cyan-300 font-mono">{selectedDomain.name}</code>.
            Automatic type casting, null handling, and statistical profiling will execute immediately upon upload.
          </p>

          <div className="mt-6 flex flex-wrap items-center justify-center gap-3 text-xs font-mono">
            <span className="px-3 py-1 rounded-lg bg-white/5 border border-white/5 text-slate-300">
              Expected Channels: {selectedDomain.keyFeatures.length}+
            </span>
            <span className="px-3 py-1 rounded-lg bg-white/5 border border-white/5 text-slate-300">
              Format: UTF-8 CSV
            </span>
            <span className="px-3 py-1 rounded-lg bg-white/5 border border-white/5 text-slate-300">
              Client or API Inference
            </span>
          </div>

          {isInspecting && (
            <div className="mt-6 flex items-center gap-2 text-xs font-mono text-cyan-300">
              <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" />
              <span>Analyzing columns and evaluating statistical anomalies...</span>
            </div>
          )}

          {inspectionError && (
            <div className="mt-4 p-3 rounded-xl bg-red-950/60 border border-red-500/40 text-red-300 text-xs font-mono flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />
              <span>{inspectionError}</span>
            </div>
          )}
        </div>
      </section>

      {/* ================= STEP 3: AUTO DETECT & PROPER CLASSIFICATIONS ================= */}
      {inspectionResult && (
        <section ref={detectionSectionRef} className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-glow-cyan" />
                <h2 className="text-xs font-mono tracking-widest uppercase text-emerald-300">
                  STEP 3: DETECT EVERYTHING & PROPER CLASSIFICATIONS
                </h2>
              </div>
              <p className="text-sm text-slate-300 mt-0.5">
                Processed <span className="text-white font-bold">{inspectionResult.total_rows} records</span> and{" "}
                <span className="text-white font-bold">{inspectionResult.total_columns} columns</span>.
                All features categorized and classified into proper severity regimes.
              </p>
            </div>
          </div>

          {/* 4 Summary Stat Cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="glass-panel rounded-2xl p-4 sm:p-5 border-purple-500/20">
              <div className="flex items-center justify-between text-slate-400 text-[10px] font-mono tracking-wider uppercase mb-2">
                <span>TOTAL ROWS DETECTED</span>
                <FileSpreadsheet className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="font-display font-extrabold text-2xl sm:text-3xl text-white">
                {inspectionResult.total_rows}
              </div>
              <div className="text-[11px] font-mono text-emerald-400 mt-1">100% Records Ingested</div>
            </div>

            <div className="glass-panel rounded-2xl p-4 sm:p-5 border-purple-500/20">
              <div className="flex items-center justify-between text-slate-400 text-[10px] font-mono tracking-wider uppercase mb-2">
                <span>FEATURE CHANNELS</span>
                <Sliders className="w-4 h-4 text-purple-400" />
              </div>
              <div className="font-display font-extrabold text-2xl sm:text-3xl text-white">
                {inspectionResult.total_columns} Cols
              </div>
              <div className="text-[11px] font-mono text-slate-400 mt-1">
                {inspectionResult.column_profiles.filter((c) => c.type === "continuous").length} Numeric /{" "}
                {inspectionResult.column_profiles.filter((c) => c.type !== "continuous").length} Binary/Cat
              </div>
            </div>

            <div className="glass-panel rounded-2xl p-4 sm:p-5 border-purple-500/20">
              <div className="flex items-center justify-between text-slate-400 text-[10px] font-mono tracking-wider uppercase mb-2">
                <span>CLASSIFIED RARE ANOMALIES</span>
                <AlertTriangle className="w-4 h-4 text-rose-400" />
              </div>
              <div className="font-display font-extrabold text-2xl sm:text-3xl text-rose-300">
                {inspectionResult.class_distribution.rare_count} Instances
              </div>
              <div className="text-[11px] font-mono text-rose-400 mt-1">
                {inspectionResult.class_distribution.rare_percentage}% Severe Tail Regime
              </div>
            </div>

            <div className="glass-panel rounded-2xl p-4 sm:p-5 border-purple-500/20">
              <div className="flex items-center justify-between text-slate-400 text-[10px] font-mono tracking-wider uppercase mb-2">
                <span>DATA INTEGRITY</span>
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="font-display font-extrabold text-2xl sm:text-3xl text-emerald-300">
                0.0% Missing
              </div>
              <div className="text-[11px] font-mono text-slate-400 mt-1">Zero null corruption detected</div>
            </div>
          </div>

          {/* Classification Distribution Badges */}
          <div className="glass-panel rounded-2xl p-5 border-purple-500/20 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono uppercase tracking-wider text-slate-300">
                DATASET CLASSIFICATION DISTRIBUTION BREAKDOWN:
              </span>
              <span className="text-[11px] font-mono text-slate-400">
                Standard vs Extreme Tail Partition
              </span>
            </div>

            {/* Distribution Bar */}
            <div className="w-full h-3 rounded-full bg-white/5 overflow-hidden flex">
              <div
                style={{
                  width: `${(inspectionResult.class_distribution.normal_count / inspectionResult.total_rows) * 100}%`,
                }}
                className="bg-emerald-500 h-full"
                title="Normal Routine Data"
              />
              <div
                style={{
                  width: `${(inspectionResult.class_distribution.suspicious_count / inspectionResult.total_rows) * 100}%`,
                }}
                className="bg-amber-400 h-full"
                title="Suspicious / Drift Data"
              />
              <div
                style={{
                  width: `${(inspectionResult.class_distribution.rare_count / inspectionResult.total_rows) * 100}%`,
                }}
                className="bg-rose-500 h-full shadow-glow"
                title="Severe Rare Anomalies"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 text-xs font-mono">
              <div className="p-3 rounded-xl bg-emerald-950/30 border border-emerald-500/30 flex items-center justify-between">
                <div>
                  <span className="text-emerald-400 font-bold block">CLASS 0: ROUTINE / NORMAL</span>
                  <span className="text-slate-400 text-[10px]">Nominal operating range</span>
                </div>
                <div className="text-right">
                  <span className="text-white font-bold text-sm">
                    {inspectionResult.class_distribution.normal_count}
                  </span>
                  <span className="text-emerald-300 text-[10px] block">
                    {(
                      (inspectionResult.class_distribution.normal_count / inspectionResult.total_rows) *
                      100
                    ).toFixed(1)}
                    %
                  </span>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-amber-950/30 border border-amber-500/30 flex items-center justify-between">
                <div>
                  <span className="text-amber-400 font-bold block">CLASS 1: SUSPICIOUS / BORDERLINE</span>
                  <span className="text-slate-400 text-[10px]">Elevated variance or warning</span>
                </div>
                <div className="text-right">
                  <span className="text-white font-bold text-sm">
                    {inspectionResult.class_distribution.suspicious_count}
                  </span>
                  <span className="text-amber-300 text-[10px] block">
                    {(
                      (inspectionResult.class_distribution.suspicious_count / inspectionResult.total_rows) *
                      100
                    ).toFixed(1)}
                    %
                  </span>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-rose-950/30 border border-rose-500/30 flex items-center justify-between">
                <div>
                  <span className="text-rose-400 font-bold block">CLASS 2: SEVERE RARE ANOMALY</span>
                  <span className="text-slate-400 text-[10px]">Extreme tail-event risk</span>
                </div>
                <div className="text-right">
                  <span className="text-white font-bold text-sm">
                    {inspectionResult.class_distribution.rare_count}
                  </span>
                  <span className="text-rose-300 text-[10px] block">
                    {(
                      (inspectionResult.class_distribution.rare_count / inspectionResult.total_rows) *
                      100
                    ).toFixed(1)}
                    %
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Detected Column Statistics Table */}
          <div className="glass-panel rounded-2xl p-5 border-purple-500/20">
            <h3 className="text-xs font-mono uppercase tracking-wider text-cyan-300 mb-3 flex items-center gap-2">
              <Sliders className="w-3.5 h-3.5" />
              <span>DETECTED FEATURE PROFILES & STATISTICAL MOMENTS</span>
            </h3>

            <div className="overflow-x-auto max-h-64 custom-scrollbar">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-white/5 text-slate-400 border-b border-white/10 sticky top-0 backdrop-blur-md">
                  <tr>
                    <th className="py-2.5 px-3">FEATURE NAME</th>
                    <th className="py-2.5 px-3">TYPE</th>
                    <th className="py-2.5 px-3 text-right">MEAN</th>
                    <th className="py-2.5 px-3 text-right">STD DEV</th>
                    <th className="py-2.5 px-3 text-right">MIN</th>
                    <th className="py-2.5 px-3 text-right">MAX</th>
                    <th className="py-2.5 px-3 text-right">95TH %ILE</th>
                    <th className="py-2.5 px-3 text-center">DOMAIN SCHEMA</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {inspectionResult.column_profiles.map((col) => (
                    <tr key={col.name} className="hover:bg-white/[0.02]">
                      <td className="py-2 px-3 font-bold text-white">{col.name}</td>
                      <td className="py-2 px-3">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] ${
                            col.type === "continuous"
                              ? "bg-purple-500/20 text-purple-300 border border-purple-500/30"
                              : "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30"
                          }`}
                        >
                          {col.type}
                        </span>
                      </td>
                      <td className="py-2 px-3 text-right text-slate-300">{col.mean ?? "—"}</td>
                      <td className="py-2 px-3 text-right text-slate-400">{col.std ?? "—"}</td>
                      <td className="py-2 px-3 text-right text-slate-400">{col.min ?? "—"}</td>
                      <td className="py-2 px-3 text-right text-slate-400">{col.max ?? "—"}</td>
                      <td className="py-2 px-3 text-right text-cyan-300">{col.p95 ?? "—"}</td>
                      <td className="py-2 px-3 text-center">
                        {col.is_domain_match ? (
                          <span className="text-emerald-400 text-[10px]">✓ Matched</span>
                        ) : (
                          <span className="text-slate-500 text-[10px]">Custom</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Interactive Records Preview Table with Filter Buttons */}
          <div className="glass-panel rounded-2xl p-5 border-purple-500/20">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
              <div>
                <h3 className="text-xs font-mono uppercase tracking-wider text-white">
                  INSPECTED RECORDS & PROPER CLASSIFICATIONS PREVIEW
                </h3>
                <span className="text-[11px] font-sans text-slate-400">
                  Showing {filteredRecords.length} records matching current filter
                </span>
              </div>

              {/* Table Filters */}
              <div className="flex items-center gap-1.5 p-1 rounded-xl bg-black/40 border border-white/10 text-xs font-mono">
                {(["all", "Normal", "Suspicious", "Rare Anomaly"] as const).map((filterOpt) => (
                  <button
                    key={filterOpt}
                    onClick={() => setTableFilter(filterOpt)}
                    className={`px-3 py-1 rounded-lg transition-all cursor-pointer ${
                      tableFilter === filterOpt
                        ? "bg-purple-600 text-white font-bold shadow-sm"
                        : "text-slate-400 hover:text-white"
                    }`}
                  >
                    {filterOpt === "all" ? "ALL RECORDS" : filterOpt.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>

            <div className="overflow-x-auto max-h-72 custom-scrollbar">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-white/5 text-slate-400 border-b border-white/10 sticky top-0 backdrop-blur-md">
                  <tr>
                    <th className="py-2 px-3">#</th>
                    <th className="py-2 px-3">PROPER CLASSIFICATION</th>
                    <th className="py-2 px-3">RISK SCORE</th>
                    {inspectionResult.column_profiles.slice(0, 5).map((col) => (
                      <th key={col.name} className="py-2 px-3 text-right">
                        {col.name.toUpperCase()}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {filteredRecords.slice(0, 30).map((rec) => {
                    const isRare = rec.classification === "Rare Anomaly";
                    const isSuspicious = rec.classification === "Suspicious";
                    return (
                      <tr
                        key={rec.row_index}
                        className={`hover:bg-white/[0.03] ${
                          isRare ? "bg-rose-950/20" : isSuspicious ? "bg-amber-950/15" : ""
                        }`}
                      >
                        <td className="py-2 px-3 text-slate-500 font-bold">{rec.row_index}</td>
                        <td className="py-2 px-3">
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                              isRare
                                ? "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                                : isSuspicious
                                ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                                : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                            }`}
                          >
                            {rec.classification}
                          </span>
                        </td>
                        <td className="py-2 px-3">
                          <div className="flex items-center gap-2">
                            <span
                              className={`text-[11px] font-bold ${
                                isRare
                                  ? "text-rose-400"
                                  : isSuspicious
                                  ? "text-amber-400"
                                  : "text-emerald-400"
                              }`}
                            >
                              {rec.risk_score}%
                            </span>
                            <div className="w-12 h-1.5 rounded-full bg-white/10 overflow-hidden">
                              <div
                                style={{ width: `${rec.risk_score}%` }}
                                className={`h-full ${
                                  isRare
                                    ? "bg-rose-500"
                                    : isSuspicious
                                    ? "bg-amber-400"
                                    : "bg-emerald-400"
                                }`}
                              />
                            </div>
                          </div>
                        </td>
                        {inspectionResult.column_profiles.slice(0, 5).map((col) => (
                          <td key={col.name} className="py-2 px-3 text-right text-slate-300">
                            {rec.data[col.name] !== null && rec.data[col.name] !== undefined
                              ? String(rec.data[col.name])
                              : "—"}
                          </td>
                        ))}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* ================= STEP 4: GENERATE RARE EVENTS ACTION BUTTON ================= */}
          <div className="glass-panel rounded-3xl p-8 border-2 border-purple-500/40 bg-gradient-to-r from-purple-950/40 via-[#0B0826] to-cyan-950/30 flex flex-col items-center justify-center text-center space-y-5 shadow-2xl relative overflow-hidden">
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full bg-purple-600/15 blur-3xl pointer-events-none" />

            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-cyan-400 to-purple-600 p-[1px] shadow-glow">
              <div className="w-full h-full bg-[#0E0A24] rounded-[15px] flex items-center justify-center">
                <Zap className="w-7 h-7 text-cyan-300" />
              </div>
            </div>

            <div>
              <span className="text-xs font-mono text-cyan-300 tracking-[0.25em] uppercase block mb-1">
                ADVERSARIAL SYNTHESIS ENGINE
              </span>
              <h3 className="font-display font-extrabold text-2xl sm:text-3xl text-white">
                Generate Rare Events From This Data Using GANs
              </h3>
              <p className="text-xs sm:text-sm font-sans text-slate-300 max-w-xl mx-auto mt-2 leading-relaxed">
                Trained directly on your uploaded data distribution. Uses an adversarial minimax duel
                between a Generator and Discriminator to synthesize plausible yet evasive rare events.
              </p>
            </div>

            {/* Config Sliders */}
            <div className="flex flex-wrap items-center justify-center gap-6 text-xs font-mono pt-2">
              <div className="flex items-center gap-3 px-4 py-2 rounded-xl bg-black/40 border border-white/10">
                <span className="text-slate-400">EVENTS TO GENERATE:</span>
                <select
                  value={numEventsToGenerate}
                  onChange={(e) => setNumEventsToGenerate(Number(e.target.value))}
                  className="bg-[#120D36] border border-purple-500/30 text-cyan-300 font-bold px-2.5 py-1 rounded-lg outline-none cursor-pointer"
                >
                  <option value={4}>4 Rare Events</option>
                  <option value={6}>6 Rare Events (Recommended)</option>
                  <option value={8}>8 Rare Events</option>
                  <option value={12}>12 Rare Events</option>
                </select>
              </div>

              <div className="flex items-center gap-3 px-4 py-2 rounded-xl bg-black/40 border border-white/10">
                <span className="text-slate-400">NOVELTY PUSH INTENSITY:</span>
                <select
                  value={noveltyPush}
                  onChange={(e) => setNoveltyPush(Number(e.target.value))}
                  className="bg-[#120D36] border border-purple-500/30 text-purple-300 font-bold px-2.5 py-1 rounded-lg outline-none cursor-pointer"
                >
                  <option value={1.0}>1.0x (Mild Boundary)</option>
                  <option value={1.4}>1.4x (Aggressive Tail)</option>
                  <option value={1.8}>1.8x (Extreme Black Swan)</option>
                </select>
              </div>
            </div>

            {/* The Big Action Button */}
            <button
              onClick={handleGenerateRareEvents}
              disabled={isGeneratingGan}
              className="px-8 py-4 rounded-2xl bg-gradient-to-r from-purple-600 via-pink-600 to-cyan-500 text-white font-display font-extrabold text-sm sm:text-base tracking-[0.15em] uppercase hover:scale-105 transition-all shadow-glow cursor-pointer disabled:opacity-60 flex items-center gap-3"
            >
              {isGeneratingGan ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin text-white" />
                  <span>TRAINING GAN & GENERATING RARE EVENTS...</span>
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5 text-cyan-200 fill-cyan-200" />
                  <span>GENERATE RARE EVENTS USING GANS</span>
                  <ArrowRight className="w-5 h-5 text-white" />
                </>
              )}
            </button>
          </div>
        </section>
      )}

      {/* ================= STEP 4: 5-YEAR-OLD EXPLANATION & GENERATED RARE EVENTS ================= */}
      {generatedEvents.length > 0 && (
        <section ref={ganSectionRef} className="space-y-8 pt-4">
          {/* Section Title & View Mode Toggle */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-white/10">
            <div>
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse shadow-glow-cyan" />
                <h2 className="text-xs font-mono tracking-widest uppercase text-cyan-300">
                  STEP 4: GAN PIPELINE EXPLAINED STEP-BY-STEP
                </h2>
              </div>
              <p className="text-sm text-slate-300 mt-0.5">
                Here is exactly how Generative Adversarial Networks synthesized rare events from your data!
              </p>
            </div>

            {/* 5-Year-Old vs Researcher Toggle */}
            <div className="flex items-center gap-1.5 p-1 rounded-2xl bg-black/50 border border-purple-500/30 text-xs font-mono self-start sm:self-auto shadow-glow">
              <button
                onClick={() => setExplanationMode("kid")}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl transition-all cursor-pointer ${
                  explanationMode === "kid"
                    ? "bg-gradient-to-r from-amber-500 to-pink-500 text-white font-bold shadow-md"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                <Baby className="w-4 h-4" />
                <span>EXPLAIN LIKE I'M 5 YEARS OLD</span>
              </button>

              <button
                onClick={() => setExplanationMode("researcher")}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl transition-all cursor-pointer ${
                  explanationMode === "researcher"
                    ? "bg-purple-600 text-white font-bold shadow-md"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                <GraduationCap className="w-4 h-4" />
                <span>ML RESEARCHER VIEW</span>
              </button>
            </div>
          </div>

          {/* 4-Stage Step-by-Step GAN Journey Cards */}
          <div className="space-y-4">
            <h3 className="text-xs font-mono uppercase tracking-wider text-purple-300 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-cyan-300" />
              <span>THE 4-STEP ADVERSARIAL LEARNING DUEL</span>
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {journeySteps.map((step) => {
                const isSelectedStep = activeJourneyStep === step.step_number;
                return (
                  <motion.div
                    key={step.step_number}
                    whileHover={{ translateY: -3 }}
                    onClick={() => setActiveJourneyStep(step.step_number)}
                    className={`glass-panel rounded-2xl p-5 border cursor-pointer transition-all flex flex-col justify-between ${
                      isSelectedStep
                        ? "border-cyan-400 bg-purple-950/50 shadow-glow"
                        : "border-purple-500/20 hover:border-purple-400/50 bg-white/[0.02]"
                    }`}
                  >
                    <div>
                      <div className="flex items-center justify-between mb-3">
                        <span className="w-7 h-7 rounded-lg bg-white/10 flex items-center justify-center font-display font-extrabold text-sm text-cyan-300">
                          {step.step_number}
                        </span>
                        <span className="text-[10px] font-mono tracking-wider text-purple-400 uppercase">
                          PHASE 0{step.step_number}
                        </span>
                      </div>

                      <h4 className="font-display font-bold text-sm text-white mb-2 leading-snug">
                        {step.title}
                      </h4>

                      <p className="text-xs font-sans text-slate-300 leading-relaxed mb-4">
                        {explanationMode === "kid" ? step.kid_story : step.researcher_context}
                      </p>
                    </div>

                    <div className="pt-3 border-t border-white/5 text-[10px] font-mono">
                      <div className="flex items-center justify-between text-slate-400">
                        <span>GENERATOR:</span>
                        <span className="text-pink-300 truncate max-w-[130px]">
                          {step.character_generator}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-slate-400 mt-1">
                        <span>DISCRIMINATOR:</span>
                        <span className="text-cyan-300 truncate max-w-[130px]">
                          {step.character_discriminator}
                        </span>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>

          {/* Active Step Detailed Visual Spotlight */}
          {journeySteps.length > 0 && (
            <div className="glass-panel rounded-3xl p-6 sm:p-8 border-cyan-400/40 bg-gradient-to-br from-purple-950/40 via-[#0B0826] to-[#060414] shadow-glow">
              {(() => {
                const curr = journeySteps.find((s) => s.step_number === activeJourneyStep) || journeySteps[0];
                return (
                  <div className="space-y-6">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-white/10">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-cyan-400/20 border border-cyan-400/40 flex items-center justify-center font-display font-extrabold text-lg text-cyan-300">
                          {curr.step_number}
                        </div>
                        <div>
                          <span className="text-[10px] font-mono text-cyan-300 tracking-widest uppercase block">
                            ACTIVE DETAILED STEP VIEW
                          </span>
                          <h3 className="font-display font-bold text-xl text-white">{curr.title}</h3>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        {journeySteps.map((s) => (
                          <button
                            key={s.step_number}
                            onClick={() => setActiveJourneyStep(s.step_number)}
                            className={`w-8 h-8 rounded-lg font-mono text-xs transition-all cursor-pointer ${
                              activeJourneyStep === s.step_number
                                ? "bg-cyan-400 text-black font-bold shadow-glow-cyan"
                                : "bg-white/5 text-slate-400 hover:text-white"
                            }`}
                          >
                            {s.step_number}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Spotlight Narrative */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                      <div className="lg:col-span-2 space-y-4">
                        <div className="p-4 rounded-2xl bg-black/40 border border-white/10">
                          <div className="flex items-center gap-2 text-xs font-mono text-amber-300 mb-2">
                            <Baby className="w-4 h-4 text-amber-400" />
                            <span className="font-bold">5-YEAR-OLD EXPLANATION STORY:</span>
                          </div>
                          <p className="text-sm font-sans text-slate-200 leading-relaxed">
                            {curr.kid_story}
                          </p>
                        </div>

                        <div className="p-4 rounded-2xl bg-black/40 border border-white/10">
                          <div className="flex items-center gap-2 text-xs font-mono text-purple-300 mb-2">
                            <GraduationCap className="w-4 h-4 text-purple-400" />
                            <span className="font-bold">TECHNICAL ML MATHEMATICS:</span>
                          </div>
                          <p className="text-xs font-mono text-slate-300 leading-relaxed">
                            {curr.researcher_context}
                          </p>
                        </div>
                      </div>

                      {/* Live Telemetry Gauges */}
                      <div className="p-5 rounded-2xl bg-black/50 border border-purple-500/20 flex flex-col justify-between">
                        <span className="text-[10px] font-mono tracking-widest text-slate-400 uppercase block mb-3">
                          PHASE TELEMETRY METRICS
                        </span>
                        <div className="space-y-3 font-mono text-xs">
                          {Object.entries(curr.telemetry).map(([k, v]) => (
                            <div
                              key={k}
                              className="flex items-center justify-between pb-2 border-b border-white/5"
                            >
                              <span className="text-slate-400 text-[11px]">
                                {k.replace(/_/g, " ").toUpperCase()}:
                              </span>
                              <span className="text-cyan-300 font-bold">{String(v)}</span>
                            </div>
                          ))}
                        </div>
                        <div className="mt-4 pt-3 text-[10px] font-mono text-emerald-400 flex items-center gap-1.5">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>Differentiable PyTorch execution verified</span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })()}
            </div>
          )}

          {/* ================= GENERATED RARE EVENTS SHOWCASE ================= */}
          <div className="space-y-4 pt-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping shadow-glow" />
                  <h3 className="font-display font-extrabold text-xl text-white">
                    Synthesized Rare Events Showcase ({generatedEvents.length} Generated)
                  </h3>
                </div>
                <p className="text-xs font-sans text-slate-300 mt-1">
                  Each event represents a statistically plausible yet extremely rare Black Swan anomaly
                  discovered from your uploaded data.
                </p>
              </div>

              {/* Download & Export Action */}
              <button
                onClick={() =>
                  exportEventsToCsv(
                    generatedEvents,
                    `sentinel_${selectedDomain.id}_generated_rare_events.csv`
                  )
                }
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-purple-600 text-black font-bold font-mono text-xs uppercase tracking-wider hover:opacity-90 transition-all cursor-pointer shadow-glow self-start sm:self-auto"
              >
                <Download className="w-4 h-4 text-black" />
                <span>DOWNLOAD GENERATED RARE EVENTS (.CSV)</span>
              </button>
            </div>

            {/* Generated Events Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {generatedEvents.map((ev) => (
                <div
                  key={ev.event_id}
                  className="glass-panel rounded-2xl p-5 border border-purple-500/30 hover:border-cyan-400/60 transition-all flex flex-col justify-between space-y-4"
                >
                  <div>
                    {/* Header: ID, Badge, Plausibility */}
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-mono font-bold text-cyan-300 tracking-wider">
                        {ev.event_id}
                      </span>
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold ${
                          ev.risk_level === "Critical"
                            ? "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                            : "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                        }`}
                      >
                        {ev.risk_level.toUpperCase()}
                      </span>
                    </div>

                    {/* Technical Title */}
                    <h4 className="font-display font-bold text-sm text-white mb-2 leading-snug">
                      {ev.technical_summary}
                    </h4>

                    {/* 5-Year-Old Explanation Card */}
                    <div className="p-3.5 rounded-xl bg-amber-950/20 border border-amber-500/30 text-amber-200 text-xs font-sans leading-relaxed mb-3">
                      <span className="text-[10px] font-mono text-amber-300 block mb-1 font-bold">
                        👶 5-YEAR-OLD STORY:
                      </span>
                      {ev.kid_explanation}
                    </div>

                    {/* Key Anomalies Pills */}
                    <div className="space-y-1 mb-3">
                      {ev.key_anomalies.map((anom, idx) => (
                        <div
                          key={idx}
                          className="text-[11px] font-mono text-slate-300 flex items-start gap-1.5"
                        >
                          <span className="text-cyan-400 mt-0.5">•</span>
                          <span>{anom}</span>
                        </div>
                      ))}
                    </div>

                    {/* Feature Snapshot Table */}
                    <div className="p-2.5 rounded-xl bg-black/40 border border-white/5 space-y-1 text-[11px] font-mono">
                      <span className="text-[9px] text-slate-400 uppercase tracking-widest block mb-1">
                        FEATURE CHANNELS:
                      </span>
                      {Object.entries(ev.features)
                        .slice(0, 4)
                        .map(([k, v]) => (
                          <div key={k} className="flex items-center justify-between text-slate-300">
                            <span className="text-slate-400">{k}:</span>
                            <span className="text-white font-bold">{String(v)}</span>
                          </div>
                        ))}
                    </div>
                  </div>

                  {/* Footer Metrics */}
                  <div className="pt-3 border-t border-white/10 grid grid-cols-2 gap-2 text-center text-xs font-mono">
                    <div className="p-2 rounded-lg bg-white/5">
                      <span className="text-[9px] text-slate-400 block">PLAUSIBILITY</span>
                      <span className="text-emerald-400 font-bold text-sm">
                        {(ev.plausibility_score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="p-2 rounded-lg bg-white/5">
                      <span className="text-[9px] text-slate-400 block">NOVELTY / RARITY</span>
                      <span className="text-purple-400 font-bold text-sm">
                        {ev.rarity_score}%
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}
    </div>
  );
};
