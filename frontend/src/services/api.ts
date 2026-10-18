import {
  Domain,
  TrainingStatus,
  Candidate,
  BenchmarkLeaderboard,
  HiddenClassProof,
  TrainingWeights,
} from "../types";

const API_BASE = "/api";

export async function fetchDomains(): Promise<Domain[]> {
  const res = await fetch(`${API_BASE}/domains`);
  if (!res.ok) throw new Error("Failed to fetch domains");
  return res.json();
}

export async function fetchDomainDetails(domainId: string): Promise<Domain> {
  const res = await fetch(`${API_BASE}/domains/${domainId}`);
  if (!res.ok) throw new Error("Failed to fetch domain details");
  return res.json();
}

export async function fetchTrainingStatus(): Promise<TrainingStatus> {
  const res = await fetch(`${API_BASE}/train/status`);
  if (!res.ok) throw new Error("Failed to fetch training status");
  return res.json();
}

export async function startTraining(params: {
  domain_id: string;
  alpha: number;
  beta: number;
  gamma: number;
  n_rounds: number;
  curriculum: boolean;
  use_offline_sim?: boolean;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/train/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to start training");
  }
  return res.json();
}

export async function stopTraining(): Promise<any> {
  const res = await fetch(`${API_BASE}/train/stop`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to stop training");
  return res.json();
}

export async function adjustWeights(weights: TrainingWeights): Promise<any> {
  const res = await fetch(`${API_BASE}/train/adjust_weights`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(weights),
  });
  if (!res.ok) throw new Error("Failed to adjust weights");
  return res.json();
}

export async function fetchCandidates(): Promise<Candidate[]> {
  const res = await fetch(`${API_BASE}/candidates`);
  if (!res.ok) throw new Error("Failed to fetch candidates");
  return res.json();
}

export async function updateCandidateStatus(
  candidateId: string,
  status: "approved" | "rejected" | "pending"
): Promise<any> {
  const res = await fetch(`${API_BASE}/candidates/${candidateId}/status`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error("Failed to update candidate status");
  return res.json();
}

export async function fetchLeaderboard(domainId: string = "transactions"): Promise<BenchmarkLeaderboard> {
  const res = await fetch(`${API_BASE}/eval/leaderboard?domain_id=${domainId}`);
  if (!res.ok) throw new Error("Failed to fetch benchmark leaderboard");
  return res.json();
}

export async function runHiddenClassProof(domainId: string = "transactions"): Promise<HiddenClassProof> {
  const res = await fetch(`${API_BASE}/eval/hidden_class?domain_id=${domainId}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to run hidden-class experiment");
  return res.json();
}

export async function fetchConformalCalibration(domainId: string = "transactions"): Promise<any> {
  const res = await fetch(`${API_BASE}/eval/conformal?domain_id=${domainId}`);
  if (!res.ok) throw new Error("Failed to fetch conformal calibration");
  return res.json();
}

export function createTrainingWebSocket(
  onEvent: (event: any) => void,
  onStatusChange?: (connected: boolean) => void
): () => void {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws/train`;
  let ws: WebSocket | null = null;
  let isClosed = false;

  function connect() {
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      if (onStatusChange) onStatusChange(true);
    };

    ws.onmessage = (msg) => {
      try {
        const parsed = JSON.parse(msg.data);
        onEvent(parsed);
      } catch (err) {
        console.error("Failed to parse WS message", err);
      }
    };

    ws.onclose = () => {
      if (onStatusChange) onStatusChange(false);
      if (!isClosed) {
        // Auto-reconnect after 3s
        setTimeout(connect, 3000);
      }
    };

    ws.onerror = (err) => {
      console.warn("WebSocket connection error:", err);
      ws?.close();
    };
  }

  connect();

  return () => {
    isClosed = true;
    ws?.close();
  };
}
