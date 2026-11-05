export type Role = "owner" | "admin" | "analyst" | "viewer";

export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  plan: string;
}

export interface Me {
  user: User;
  org: Organization;
  role: Role;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  disease_pack: string;
  archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface SampleFile {
  id: string;
  filename: string;
  kind: string;
  size_bytes: number;
  created_at: string;
}

export interface Sample {
  id: string;
  project_id: string;
  name: string;
  external_id: string;
  disease_pack: string;
  platform: string;
  species: string;
  condition: string;
  sample_metadata: Record<string, unknown>;
  status: string;
  spot_count: number | null;
  archived: boolean;
  created_at: string;
}

export interface SampleDetail extends Sample {
  files: SampleFile[];
  runs: Run[];
}

export type RunStatus = "queued" | "running" | "succeeded" | "failed" | "cancelled";

export interface RunSummary {
  sample_id: string;
  pipeline_version: string;
  method: string;
  n_spots: number;
  n_genes: number;
  passed_spots: number;
  modeled_spots: number;
  n_domains: number;
  n_cell_types: number;
  dominant_cell_type: string | null;
  composition_mean: Record<string, number>;
  top_targets: Array<{
    gene: string;
    name: string;
    score: number;
    evidence_level: string;
  }>;
  runtime_seconds: number;
  synthetic: boolean;
  disease_pack: { id: string; name: string; version: string };
  warnings: string[];
  method_agreement?: number | null;
  significant_interactions?: number;
  not_assessed?: string[];
}

export interface Run {
  id: string;
  project_id: string;
  sample_id: string;
  disease_pack: string;
  pack_version: string;
  pipeline_version: string;
  status: RunStatus;
  stage: string;
  progress: number;
  summary: RunSummary | null;
  error_code: string | null;
  error_message: string | null;
  started_at: string | null;
  finished_at: string | null;
  created_at: string;
}

export interface RunProvenance {
  recorded_at: string;
  pipeline_version: string;
  disease_pack: { id: string; version: string; status: string; sha256: string };
  reference: { version: string; scrna_sources: string[]; spatial_sources: string[] };
  params: Record<string, unknown>;
  input: {
    kind: "visium" | "synthetic";
    files: { filename: string; sha256: string; size_bytes: number }[];
    synthetic_seed: number | null;
  };
  software: {
    commit: string;
    api_version: string;
    analysis_package: string;
    python: string;
    numpy: string;
    scipy: string;
    scikit_learn: string;
    pandas: string;
  };
}

export type ReportStatus = "draft" | "approved";

export interface ReportState {
  status: ReportStatus;
  created_at: string;
  approved_at: string | null;
  approved_by_name: string | null;
  approval_note: string;
}

export interface RunDetail extends Run {
  params: Record<string, unknown>;
  provenance: RunProvenance | null;
  sample: Sample | null;
  report: ReportState | null;
}

export interface ProjectDetail extends Project {
  samples: Sample[];
  runs: Run[];
  stats: {
    sample_count: number;
    run_count: number;
    completed_runs: number;
    spots: number;
  };
}

export type EvidenceLevel = "established" | "emerging" | "exploratory";

export interface TargetScore {
  gene: string;
  name: string;
  rationale: string;
  evidence_level: EvidenceLevel;
  detected: boolean;
  overall_score: number;
  by_domain: Record<string, number>;
  by_cell_type: Record<string, number>;
}

export interface Spot {
  barcode: string;
  x: number;
  y: number;
  domain: string;
  domain_name: string;
  uncertainty: number;
  qc_pass: boolean;
  composition: Record<string, number>;
}

export interface DomainSummary {
  id: string;
  name: string;
  color: string;
  count: number;
  pct: number;
  mean_uncertainty: number;
  top_cell_types: Array<{ id: string; value: number }>;
}

export interface QCSummary {
  n_spots: number;
  n_genes: number;
  passed_spots: number;
  failed_spots: number;
  median_counts: number;
  median_genes: number;
  median_mito_fraction: number;
  thresholds: {
    min_counts: number;
    min_genes: number;
    max_mito_fraction: number;
  };
}

export interface BenchmarkMetrics {
  n_spots: number;
  composition: {
    jsd_mean: number;
    rmse: number;
    dominant_type_pearson: number;
  };
  domains: {
    ari: number;
    nmi: number;
  };
  note: string;
}

export interface ResultPayload {
  sample_id: string;
  pipeline_version: string;
  summary: RunSummary;
  qc: {
    summary: QCSummary;
    warnings: string[];
  };
  composition: Record<string, number[]>;
  smoothed_composition: Record<string, number[]>;
  domains: string[];
  domain_names: string[];
  uncertainty: number[];
  target_scores: TargetScore[];
  spots: Spot[];
  domains_summary: DomainSummary[];
  metrics: BenchmarkMetrics | null;
  warnings: string[];
  artifacts: Record<string, unknown>;
  communication?: Interaction[];
  validation?: {
    method_concordance: MethodConcordance | null;
    atlas_check: AtlasCheck | null;
  };
}

export interface Interaction {
  id: string;
  name: string;
  ligand: string;
  receptor: string;
  sender: string;
  receiver: string;
  category: string;
  tested: boolean;
  missing: string[];
  score: number | null;
  p_value: number | null;
  q_value: number | null;
  significant: boolean;
  ligand_detected_fraction?: number;
  receptor_detected_fraction?: number;
  by_domain?: Record<string, number>;
  top_domain?: string | null;
}

export interface MethodConcordance {
  methods: string[];
  mean_spot_agreement: number;
  low_agreement_fraction: number;
  mean_cell_type_pearson: number | null;
  per_cell_type_pearson: Record<string, number | null>;
}

export interface AtlasCheck {
  name: string;
  citation: string;
  status: "ok" | "skipped_synthetic" | "unavailable" | "insufficient_genes" | "insufficient_zones";
  reason?: string;
  note?: string;
  structures?: string[];
  zones?: string[];
  genes?: string[];
  excluded_genes?: string[];
  n_genes?: number;
  correlation?: (number | null)[][];
  diagonal_mean?: number | null;
  top1_accuracy?: number | null;
  n_zones_compared?: number;
}

export interface CellType {
  id: string;
  name: string;
  markers: string[];
  color: string;
}

export interface Zone {
  id: string;
  name: string;
  markers: string[];
  color: string;
  description?: string;
}

export interface Target {
  gene: string;
  name: string;
  rationale: string;
  evidence_level: EvidenceLevel;
}

export interface DiseasePack {
  id: string;
  version: string;
  status: "draft" | "beta" | "validated" | "deprecated";
  name: string;
  short_name: string;
  tissue: string;
  data_richness: "high" | "medium" | "low";
  color: string;
  description: string;
  aliases: string[];
  cell_type_count: number;
  zone_count: number;
  target_count: number;
  reference: {
    scrna_sources?: string[];
    spatial_sources?: string[];
    minimum_samples?: number;
  };
  validation: {
    metrics: Record<string, unknown>;
    last_run: string | null;
    approved_by: string | null;
  };
  cell_types?: CellType[];
  zones?: Zone[];
  targets?: Target[];
  ligand_receptor_count?: number;
  ligand_receptor_pairs?: {
    ligand: string;
    receptor: string;
    sender: string;
    receiver: string;
    category?: string;
  }[];
  not_assessed?: string[];
  atlas_reference?: {
    name: string;
    citation: string;
    url?: string;
    license_status: "cleared" | "review_pending" | "restricted";
  } | null;
}

export interface DashboardSummary {
  projects: number;
  samples: number;
  runs: number;
  completed_runs: number;
  failed_runs: number;
  spots_analyzed: number;
  recent_runs: Run[];
  disease_packs: DiseasePack[];
}

export interface Member {
  id: string;
  user_id: string;
  name: string;
  email: string;
  role: Role;
  created_at: string;
}

export interface AuditLog {
  id: string;
  action: string;
  resource_type: string;
  resource_id: string;
  ip: string;
  log_metadata: Record<string, unknown>;
  created_at: string;
}
