export interface Domain {
  id: string;
  name: string;
  description: string;
  num_features: number;
  class_labels: Record<string, string>;
  rare_class_label: number;
  hidden_class_label: number | null;
  feature_names: string[];
  feature_schema: Record<string, any>;
}

export interface TrainingWeights {
  alpha: number;
  beta: number;
  gamma: number;
}

export interface MapPoint {
  x: number;
  y: number;
  type: "nominal" | "known_rare" | "archive" | "candidate";
}

export interface MapPayload {
  total_points: number;
  points: MapPoint[];
  bounds: { min: number; max: number };
}

export interface Candidate {
  id: string;
  realism_score: number;
  novelty_score: number;
  hardness_score: number;
  reward: number;
  round_idx: number;
  status: "approved" | "rejected" | "pending";
  created_at: number;
  explanation: {
    summary: string;
    key_anomalies: string[];
    risk_level: string;
    metrics?: Record<string, any>;
  };
  synthetic_watermark: string;
  features_preview: number[];
}

export interface TrainingRoundEvent {
  round: number;
  total_rounds: number;
  weights: TrainingWeights;
  loss_g: number;
  loss_d: number;
  realism: number;
  novelty: number;
  hardness: number;
  reward: number;
  archive_size: number;
  new_candidates_added: number;
  val_pr_auc: number;
  val_roc_auc: number;
  val_recall: number;
  map_payload: MapPayload;
  recent_candidates: Candidate[];
}

export interface TrainingStatus {
  status: "idle" | "running" | "completed" | "error";
  domain_id: string;
  round: number;
  total_rounds: number;
  weights: TrainingWeights;
  active_archive_size: number;
  latest_event: TrainingRoundEvent | null;
  error_message: string | null;
}

export interface ModelMetricRow {
  model_name: string;
  pr_auc: number;
  roc_auc: number;
  recall_at_target_fpr: number;
  false_alarm_rate?: number;
  precision?: number;
  f1?: number;
  hidden_class_recall: number;
  calibration_ece: number;
  threshold?: number;
  conformal?: any;
  memorization?: any;
}

export interface BenchmarkLeaderboard {
  domain_id: string;
  domain_name: string;
  splits_summary: any;
  models_leaderboard: ModelMetricRow[];
  sentinel_history: TrainingRoundEvent[];
  conformal_details: any;
}

export interface HiddenClassProof {
  domain: string;
  hidden_class_name: string;
  n_hidden_test_instances: number;
  comparison: {
    model: string;
    hidden_recall: number;
    overall_pr_auc: number;
  }[];
  proof_summary: string;
}
