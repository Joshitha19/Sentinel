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
  domain_id?: string;
  explanation: {
    summary: string;
    key_anomalies: string[];
    risk_level: string;
    metrics?: Record<string, any>;
    simple_explanation?: string;
    solution?: RareEventSolution;
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

export interface ColumnProfile {
  name: string;
  type: string;
  null_count: number;
  null_percentage: number;
  is_domain_match?: boolean;
  mean?: number;
  std?: number;
  min?: number;
  max?: number;
  p95?: number;
}

export interface ClassifiedRecord {
  row_index: number;
  classification: "Normal" | "Suspicious" | "Rare Anomaly";
  risk_score: number;
  data: Record<string, any>;
}

export interface CsvInspectionResult {
  status: string;
  domain_id: string;
  domain_name: string;
  total_rows: number;
  total_columns: number;
  column_profiles: ColumnProfile[];
  feature_stats: Record<string, { mean: number; std: number; min: number; max: number }>;
  class_distribution: {
    normal_count: number;
    suspicious_count: number;
    rare_count: number;
    rare_percentage: number;
  };
  records_preview: ClassifiedRecord[];
}

export interface RareEventSolution {
  title: string;
  immediate_containment: string[];
  root_cause_remediation: string[];
  model_defense_calibration: string;
}

export interface GeneratedRareEvent {
  event_id: string;
  archetype_id?: number;
  plausibility_score: number;
  rarity_score: number;
  risk_level: string;
  risk_score: number;
  hardness_score: number;
  conformal_p_value?: number;
  technical_summary: string;
  key_anomalies: string[];
  simple_explanation: string;
  solution: RareEventSolution;
  features: Record<string, any>;
  consistency_verified?: boolean;
  consistency_message?: string;
  top_deviation_names?: string[];
  score_formulas?: {
    realism: string;
    tail_novelty: string;
    detector_hardness: string;
  };
  triage_status?: "pending" | "approved" | "rejected";
}

export interface GanJourneyStep {
  step_number: number;
  title: string;
  character_generator: string;
  character_discriminator: string;
  simple_story: string;
  researcher_context: string;
  telemetry: Record<string, any>;
}

export interface TrainingRoundHistory {
  round: number;
  loss_g: number;
  loss_c: number;
  loss_d: number;
  novelty_multiplier: number;
  held_out_recall: number;
  realism_score: number;
}

export interface ProofOfTraining {
  training_time_seconds: number;
  seed: number;
  rounds_completed: number;
  real_vs_fake_auc: number;
  final_held_out_novel_recall: number;
  history: TrainingRoundHistory[];
}

export interface NoveltyDiscoveryCheck {
  has_held_out: boolean;
  held_out_subtype?: string;
  total_held_out_cases?: number;
  discovered_in_knn_neighborhood?: number;
  discovery_rate_pct?: number;
  detector_zero_shot_recall_pct?: number;
  detector_detected_cases?: number;
  isolation_forest_baseline_recall_pct?: number;
  isolation_forest_detected_cases?: number;
  relative_advantage_pct?: number;
  honest_assessment?: string;
  message?: string;
}

export interface GanGenerationResult {
  status: string;
  domain_id: string;
  generated_events: GeneratedRareEvent[];
  journey_steps: GanJourneyStep[];
  proof_of_training?: ProofOfTraining;
  novelty_discovery_check?: NoveltyDiscoveryCheck;
}


