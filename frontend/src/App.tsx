import React, { useState, useEffect } from "react";
import { Navbar } from "./components/common/Navbar";
import { MissionControlPage } from "./pages/MissionControlPage";
import { LiveTrainingPage } from "./pages/LiveTrainingPage";
import { CandidateExplorerPage } from "./pages/CandidateExplorerPage";
import { EvaluationPage } from "./pages/EvaluationPage";
import { AboutLimitsPage } from "./pages/AboutLimitsPage";
import { AdversarialStudioPage } from "./pages/AdversarialStudioPage";
import {
  Domain,
  TrainingStatus,
  Candidate,
  BenchmarkLeaderboard,
  TrainingWeights,
  MapPayload,
} from "./types";
import {
  fetchDomains,
  fetchTrainingStatus,
  startTraining,
  stopTraining,
  adjustWeights,
  fetchCandidates,
  updateCandidateStatus,
  fetchLeaderboard,
  createTrainingWebSocket,
} from "./services/api";

export const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<string>("control");
  const [domains, setDomains] = useState<Domain[]>([]);
  const [selectedDomain, setSelectedDomain] = useState<Domain | null>(null);

  // Training state & telemetry
  const [trainingStatus, setTrainingStatus] = useState<TrainingStatus>({
    status: "idle",
    domain_id: "transactions",
    round: 0,
    total_rounds: 12,
    weights: { alpha: 1.0, beta: 1.2, gamma: 1.0 },
    active_archive_size: 0,
    latest_event: null,
    error_message: null,
  });

  const [history, setHistory] = useState<any[]>([]);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [mapPayload, setMapPayload] = useState<MapPayload | null>(null);
  const [leaderboard, setLeaderboard] = useState<BenchmarkLeaderboard | null>(null);
  const [isLeaderboardLoading, setIsLeaderboardLoading] = useState<boolean>(false);
  const [wsConnected, setWsConnected] = useState<boolean>(false);

  // Initial Data Load
  useEffect(() => {
    fetchDomains()
      .then((data) => {
        setDomains(data);
        if (data.length > 0) {
          setSelectedDomain(data[0]);
        }
      })
      .catch((err) => console.error("Error loading domains:", err));

    fetchTrainingStatus()
      .then((status) => setTrainingStatus(status))
      .catch((err) => console.warn("Initial training status error:", err));

    fetchCandidates()
      .then((cands) => setCandidates(cands))
      .catch((err) => console.warn("Initial candidates error:", err));
  }, []);

  // WebSocket Telemetry Listener
  useEffect(() => {
    const cleanupWs = createTrainingWebSocket(
      (event) => {
        if (event.event === "training_round") {
          const data = event.data;
          setTrainingStatus((prev) => ({
            ...prev,
            status: "running",
            round: data.round,
            total_rounds: data.total_rounds,
            weights: data.weights,
            active_archive_size: data.archive_size,
            latest_event: data,
          }));

          setHistory((prev) => [...prev, data]);
          if (data.map_payload) {
            setMapPayload(data.map_payload);
          }
          if (data.recent_candidates && data.recent_candidates.length > 0) {
            setCandidates(data.recent_candidates);
          }
        } else if (event.event === "training_complete") {
          setTrainingStatus((prev) => ({ ...prev, status: "completed" }));
          // Refresh candidates and leaderboard
          fetchCandidates().then((cands) => setCandidates(cands));
          if (selectedDomain) {
            fetchLeaderboard(selectedDomain.id).then((lb) => setLeaderboard(lb));
          }
        } else if (event.event === "training_started") {
          setTrainingStatus((prev) => ({ ...prev, status: "running", round: 0 }));
          setHistory([]);
        }
      },
      (connected) => setWsConnected(connected)
    );

    return cleanupWs;
  }, [selectedDomain]);

  // Load Leaderboard on domain change or eval page view
  useEffect(() => {
    if (currentPage === "eval" && selectedDomain) {
      setIsLeaderboardLoading(true);
      fetchLeaderboard(selectedDomain.id)
        .then((lb) => setLeaderboard(lb))
        .catch((err) => console.error("Error loading leaderboard:", err))
        .finally(() => setIsLeaderboardLoading(false));
    }
  }, [currentPage, selectedDomain]);

  // Actions
  const handleStartTraining = async () => {
    if (!selectedDomain) return;
    try {
      await startTraining({
        domain_id: selectedDomain.id,
        alpha: trainingStatus.weights.alpha,
        beta: trainingStatus.weights.beta,
        gamma: trainingStatus.weights.gamma,
        n_rounds: 12,
        curriculum: true,
        use_offline_sim: false,
      });
      setTrainingStatus((prev) => ({ ...prev, status: "running", round: 0 }));
      setHistory([]);
      setCurrentPage("training");
    } catch (err: any) {
      alert(err.message || "Failed to start training");
    }
  };

  const handleStopTraining = async () => {
    try {
      await stopTraining();
      setTrainingStatus((prev) => ({ ...prev, status: "idle" }));
    } catch (err) {
      console.error(err);
    }
  };

  const handleAdjustWeights = async (newWeights: TrainingWeights) => {
    setTrainingStatus((prev) => ({ ...prev, weights: newWeights }));
    try {
      await adjustWeights(newWeights);
    } catch (err) {
      console.error("Failed to adjust weights:", err);
    }
  };

  const handleUpdateCandidateStatus = async (
    candidateId: string,
    status: "approved" | "rejected"
  ) => {
    try {
      await updateCandidateStatus(candidateId, status);
      setCandidates((prev) =>
        prev.map((c) => (c.id === candidateId ? { ...c, status } : c))
      );
    } catch (err) {
      console.error("Failed to update status:", err);
    }
  };

  return (
    <div className="min-h-screen bg-[#060414] text-slate-100 flex flex-col font-sans selection:bg-purple-600 selection:text-white">
      {/* Top Navbar */}
      <Navbar
        currentPage={currentPage}
        onPageChange={setCurrentPage}
        selectedDomain={selectedDomain}
        domains={domains}
        onSelectDomain={(dom) => {
          setSelectedDomain(dom);
          setTrainingStatus((prev) => ({ ...prev, domain_id: dom.id }));
        }}
        isTraining={trainingStatus.status === "running"}
      />

      {/* Main Content View */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 pt-6">
        {currentPage === "control" && (
          <MissionControlPage
            selectedDomain={selectedDomain}
            trainingStatus={trainingStatus}
            onStartTraining={handleStartTraining}
            onLaunchAdversarialRun={() => setCurrentPage("adversarial")}
            onNavigateToTraining={() => setCurrentPage("training")}
          />
        )}

        {currentPage === "adversarial" && (
          <AdversarialStudioPage
            onBackToMissionControl={() => setCurrentPage("control")}
            onNavigateToArchive={() => setCurrentPage("candidates")}
          />
        )}

        {currentPage === "training" && (
          <LiveTrainingPage
            status={trainingStatus}
            history={history}
            mapPayload={mapPayload}
            weights={trainingStatus.weights}
            onStartTraining={handleStartTraining}
            onStopTraining={handleStopTraining}
            onAdjustWeights={handleAdjustWeights}
            domainName={selectedDomain?.name || "Transactions"}
          />
        )}

        {currentPage === "candidates" && (
          <CandidateExplorerPage
            candidates={candidates}
            onUpdateStatus={handleUpdateCandidateStatus}
            domainName={selectedDomain?.name || "Transactions"}
          />
        )}

        {currentPage === "eval" && (
          <EvaluationPage
            leaderboard={leaderboard}
            domainId={selectedDomain?.id || "transactions"}
            domainName={selectedDomain?.name || "Transactions"}
            isLoading={isLeaderboardLoading}
            onRefresh={() => {
              if (selectedDomain) {
                setIsLeaderboardLoading(true);
                fetchLeaderboard(selectedDomain.id).then((lb) => setLeaderboard(lb));
              }
            }}
          />
        )}

        {currentPage === "about" && <AboutLimitsPage />}
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-purple-500/10 py-6 px-6 text-center text-xs font-mono text-slate-500 bg-[#060414]/90">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div>SENTINEL RESEARCH FRAMEWORK // STRICTLY FOR BENCHMARK GENERALIZATION</div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span>ALL FREE & OPEN SOURCE STACK</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
