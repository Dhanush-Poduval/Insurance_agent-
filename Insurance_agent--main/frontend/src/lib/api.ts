// =============================================================================
// SAFAR Insurance — Centralized API Client
// Connects to FastAPI backend at /api/v2/*
// =============================================================================

const API_BASE = (import.meta as any).env?.VITE_API_BASE || 'http://localhost:8000';

// ---------------------------------------------------------------------------
// Core fetch wrapper with error handling
// ---------------------------------------------------------------------------
async function apiFetch<T = any>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...(options?.headers || {}),
      },
      ...options,
    });
    if (!res.ok) {
      const errorBody = await res.json().catch(() => null);
      const message = errorBody?.detail || `API Error ${res.status}`;
      throw new Error(message);
    }
    return res.json() as Promise<T>;
  } catch (err: any) {
    console.error(`[API] ${options?.method || 'GET'} ${endpoint} failed:`, err);
    throw err;
  }
}

// ---------------------------------------------------------------------------
// Query-string helper  (?key=value&…)
// ---------------------------------------------------------------------------
function qs(params: Record<string, any>): string {
  const filtered = Object.entries(params).filter(
    ([, v]) => v !== undefined && v !== null
  );
  if (!filtered.length) return '';
  return '?' + new URLSearchParams(filtered.map(([k, v]) => [k, String(v)])).toString();
}

// =============================================================================
// Types — mirror backend Pydantic schemas
// =============================================================================

export type PlatformType = 'zomato' | 'amazon' | 'swiggy';

export interface PremiumCalculationRequest {
  worker_id: string;
  avg_income: number;       // gt 0, between 50-10000
  zone_id: string;
  platform_type: PlatformType;
  week_starting?: string;   // ISO date "YYYY-MM-DD"
}

export interface PremiumBreakdown {
  expected_loss: number;
  platform_fee: number;
  risk_margin: number;
  base_premium: number;
  zone_discount: number;
  loyalty_discount: number;
  seasonal_loading: number;
  final_premium: number;
}

export interface PremiumCalculationResponse {
  worker_id: string;
  weekly_premium: number;
  predicted_risk: number;
  disruption_frequency: number;
  risk_factors: Record<string, number>;
  premium_breakdown: PremiumBreakdown;
  explainability: Record<string, string>;
  week_starting: string;
  expires_at: string;
}

export interface WorkerProfile {
  worker_id: string;
  platform: string;
  zone: string;
  avg_hourly_earnings: number;
  risk_category: string;
  peak_hours: any;
  statistics: {
    total_premiums_calculated: number;
    average_weekly_premium: number;
    total_payouts_claimed: number;
    claims_success_rate: string;
  };
  created_at: string;
  updated_at: string;
}

export interface ClaimHistoryItem {
  premium_id: string;
  week_starting: string;
  zone_id: string;
  base_premium: number;
  payout_amount: number;
  payout_percentage: string;
  loss_ratio: number;
  claimed_at: string;
}

export interface ClaimHistoryResponse {
  worker_id: string;
  total_claims: number;
  claims: ClaimHistoryItem[];
  timestamp: string;
}

export interface PayoutStatusResponse {
  worker_id: string;
  pending_payouts: number;
  total_pending_amount: number;
  payouts: {
    premium_id: string;
    zone_id: string;
    payout_amount: number;
    status: string;
    created_at: string;
  }[];
  timestamp: string;
}

export interface ZoneAnalytics {
  zone_id: string;
  status?: string;
  message?: string;
  metrics?: {
    disruption_events_30d: number;
    average_rainfall_mm: number;
    average_aqi: number;
    total_deliveries_attempted: number;
    total_failed_deliveries: number;
    failure_rate: string;
    risk_level: string;
  };
  recent_events?: {
    date: string;
    rainfall: number;
    aqi: number;
    failed_rate: string;
  }[];
  timestamp?: string;
}

export interface TriggerEvaluationResult {
  zone_id: string;
  rainfall_triggered: boolean;
  aqi_triggered: boolean;
  temperature_triggered: boolean;
  payout_triggered: boolean;
  payout_reason: string;
  timestamp: string;
}

export interface TriggerHistoryResponse {
  zone_id: string;
  total_events: number;
  triggered_events: number;
  events: {
    timestamp: string;
    triggered: boolean;
    reason: string;
    weather: any;
  }[];
}

export interface TriggerStatistics {
  total_events: number;
  triggered_events: number;
  trigger_rate: string;
  zones_monitored: number;
  zones: string[];
  timestamp: string;
}

export interface Suggestion {
  type: string;
  title: string;
  description: string;
  impact: string;
  priority: string;
}

export interface SuggestionsResponse {
  worker_id: string;
  current_risk_category: string;
  suggestions: Suggestion[];
  timestamp: string;
}

export interface SystemStatus {
  status: string;
  timestamp: string;
  database: {
    workers_registered: number;
    premiums_calculated: number;
    trigger_events: number;
    triggers_activated: number;
    trigger_rate: string;
  };
  services: Record<string, string>;
  uptime: string;
  api_version: string;
}

export interface Recommendation {
  title: string;
  description: string;
  action: string;
  impact: string;
}

export interface RecommendationsResponse {
  worker_id: string;
  status?: string;
  message?: string;
  average_weekly_premium?: number;
  claims_success_rate?: string;
  recommendations: Recommendation[];
  next_calculation?: string;
  timestamp: string;
}

export interface IncomeLossResponse {
  worker_id: string;
  hourly_earning: number;
  disruption_duration_hours: number;
  disruption_severity: number;
  income_at_risk: number;
  income_loss: number;
  calculation_breakdown: Record<string, string>;
}

export interface FairPayoutResponse {
  worker_id: string;
  zone_id: string;
  disruption_severity: number;
  disruption_duration_hours: number;
  hourly_earning: number;
  income_at_risk: number;
  income_loss: number;
  payout_amount: number;
  coverage_percentage: number;
  platform_buffer: number;
  calculation_details: Record<string, string>;
}

export interface AdminDashboardResponse {
  loss_ratio: {
    value: string;
    total_premium: number;
    total_payout: number;
  };
  predictive_analytics: {
    summary: string;
    next_week_forecast: Array<{ zone_id: string; predicted_claim_probability: string; trend: string }>;
  };
  recent_fraud_alerts: Array<{
    worker_id: string;
    anomaly_score: number;
    reason: string;
    action_taken?: string;
    fraud_score_breakdown?: Record<string, number>;
  }>;
  total_active_policies: number;
  timestamp: string;
}

// =============================================================================
// API Functions — Pricing
// =============================================================================

/** Health check for the pricing service */
export const healthCheck = () =>
  apiFetch<{ status: string; ml_models_loaded: boolean; timestamp: string }>(
    '/api/v2/pricing/health'
  );

/** Register a new gig worker */
export const registerWorker = (params: {
  worker_id: string;
  platform_type: string;
  zone_id: string;
  avg_hourly_earnings: number;
}) =>
  apiFetch(`/api/v2/pricing/register-worker${qs(params)}`, {
    method: 'POST',
  });

/** Calculate dynamic weekly premium */
export const calculatePremium = (body: PremiumCalculationRequest) =>
  apiFetch<PremiumCalculationResponse>('/api/v2/pricing/calculate-premium', {
    method: 'POST',
    body: JSON.stringify(body),
  });

/** Get the pricing formula explanation */
export const getPremiumFormula = () =>
  apiFetch('/api/v2/pricing/premium-formula');

/** Get pricing fairness metrics */
export const getPricingFairnessMetrics = () =>
  apiFetch('/api/v2/pricing/pricing-fairness-metrics');

/** Calculate income loss for a disruption event */
export const calculateIncomeLoss = (params: {
  worker_id: string;
  disruption_severity: number;
  disruption_duration_hours: number;
}) =>
  apiFetch<IncomeLossResponse>(
    `/api/v2/pricing/income-loss-calculation${qs(params)}`,
    { method: 'POST' }
  );

/** Calculate fair payout */
export const calculateFairPayout = (params: {
  worker_id: string;
  zone_id: string;
  disruption_severity: number;
  disruption_duration_hours: number;
}) =>
  apiFetch<FairPayoutResponse>(
    `/api/v2/pricing/fair-payout${qs(params)}`,
    { method: 'POST' }
  );

/** Get transparent pricing breakdown with SHAP explanations */
export const getTransparentPricing = (params: {
  worker_id: string;
  features: Record<string, number>;
  delivery_partner?: string;
}) => {
  const queryParams: Record<string, any> = {
    worker_id: params.worker_id,
    ...(params.delivery_partner ? { delivery_partner: params.delivery_partner } : {}),
  };
  return apiFetch(
    `/api/v2/pricing/transparent-pricing-breakdown${qs(queryParams)}`,
    {
      method: 'POST',
      body: JSON.stringify(params.features),
    }
  );
};

// =============================================================================
// API Functions — Claims & Payouts
// =============================================================================

/** Submit a claim for payout */
export const submitClaim = (params: {
  worker_id: string;
  zone_id: string;
  gps_latitude?: number;
  gps_longitude?: number;
}) =>
  apiFetch(`/api/v2/pricing/claims/submit${qs(params)}`, {
    method: 'POST',
  });

/** Get claim history for a worker */
export const getClaimHistory = (workerId: string, limit = 10) =>
  apiFetch<ClaimHistoryResponse>(
    `/api/v2/pricing/claims/history/${workerId}${qs({ limit })}`
  );

/** Get payout status for a worker */
export const getPayoutStatus = (workerId: string) =>
  apiFetch<PayoutStatusResponse>(
    `/api/v2/pricing/payouts/status/${workerId}`
  );

// =============================================================================
// API Functions — Worker Profile & Analytics
// =============================================================================

/** Get detailed worker profile */
export const getWorkerProfile = (workerId: string) =>
  apiFetch<WorkerProfile>(`/api/v2/pricing/worker-profile/${workerId}`);

/** Get AI‑powered suggestions for a worker */
export const getWorkerSuggestions = (workerId: string) =>
  apiFetch<SuggestionsResponse>(`/api/v2/pricing/suggestions/${workerId}`);

/** Get zone analytics */
export const getZoneAnalytics = (zoneId: string) =>
  apiFetch<ZoneAnalytics>(`/api/v2/pricing/zone-analytics/${zoneId}`);

/** Get Admin Dashboard data */
export const getAdminDashboard = () =>
  apiFetch<AdminDashboardResponse>('/api/v2/pricing/admin/dashboard');

/** Execute Admin Action */
export const executeAdminAction = (body: { action: string; worker_id: string; target_id?: string; reason?: string }) =>
  apiFetch<{ status: string; message: string }>('/api/v2/pricing/admin/action', {
    method: 'POST',
    body: JSON.stringify(body)
  });

/** Get system status & health */
export const getSystemStatus = () =>
  apiFetch<SystemStatus>('/api/v2/pricing/system-status');

/** Get personalized premium recommendations */
export const getRecommendations = (workerId: string) =>
  apiFetch<RecommendationsResponse>(
    `/api/v2/pricing/recommendations/${workerId}`
  );

/** Get ML model performance metrics */
export const getMLPerformance = () =>
  apiFetch('/api/v2/pricing/ml-performance');

/** Explain why a premium is at a certain level */
export const explainPremium = (params: {
  worker_id: string;
  base_premium: number;
  adjusted_premium: number;
}) =>
  apiFetch(`/api/v2/pricing/explain-premium${qs(params)}`, {
    method: 'POST',
  });

/** Get global feature importance */
export const getFeatureImportance = () =>
  apiFetch('/api/v2/pricing/feature-importance');

/** Get prediction insight for a worker */
export const getPredictionInsight = (workerId: string) =>
  apiFetch(`/api/v2/pricing/prediction-insight/${workerId}`);

// =============================================================================
// API Functions — Triggers
// =============================================================================

/** Evaluate parametric triggers for a zone */
export const evaluateTriggers = (zoneId: string) =>
  apiFetch<TriggerEvaluationResult>(
    `/api/v2/triggers/evaluate/${zoneId}`,
    { method: 'POST' }
  );

/** Evaluate triggers for all zones */
export const evaluateAllZones = () =>
  apiFetch<{
    total_zones: number;
    triggered_zones: number;
    zones: TriggerEvaluationResult[];
    timestamp: string;
  }>('/api/v2/triggers/evaluate/all');

/** Get trigger history for a zone */
export const getTriggerHistory = (zoneId: string, limit = 10) =>
  apiFetch<TriggerHistoryResponse>(
    `/api/v2/triggers/history/${zoneId}${qs({ limit })}`
  );

/** Get trigger statistics across all zones */
export const getTriggerStatistics = () =>
  apiFetch<TriggerStatistics>('/api/v2/triggers/statistics');

// =============================================================================
// Root-level endpoints
// =============================================================================

/** Root health check */
export const rootHealthCheck = () =>
  apiFetch<{ status: string; timestamp: string; scheduler_running: boolean }>(
    '/health'
  );
