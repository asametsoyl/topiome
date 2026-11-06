export class ApiError extends Error {
  status: number;
  code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

const BASE = "/api/v1";

type RequestOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
  raw?: boolean;
};

export async function api<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { body, raw, headers, ...rest } = options;
  const isFormData = body instanceof FormData;

  const response = await fetch(`${BASE}${path}`, {
    ...rest,
    credentials: "include",
    headers: {
      ...(isFormData ? {} : body !== undefined ? { "Content-Type": "application/json" } : {}),
      ...headers,
    },
    body: isFormData ? body : body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    let code: string | undefined;
    try {
      const data = await response.json();
      if (typeof data?.detail === "string") {
        message = data.detail;
      } else if (data?.detail?.message) {
        message = data.detail.message;
        code = data.detail.code;
      }
    } catch {
      // Keep the generic message.
    }
    throw new ApiError(message, response.status, code);
  }

  if (response.status === 204) return undefined as T;
  if (raw) return (await response.text()) as T;
  return (await response.json()) as T;
}

export const apiClient = {
  me: () => api<import("./types").Me>("/auth/me"),
  login: (body: { email: string; password: string }) =>
    api<import("./types").Me>("/auth/login", { method: "POST", body }),
  register: (body: { name: string; email: string; password: string; org_name?: string }) =>
    api<import("./types").Me>("/auth/register", { method: "POST", body }),
  demo: () => api<import("./types").Me>("/auth/demo", { method: "POST" }),
  logout: () => api<{ ok: boolean }>("/auth/logout", { method: "POST" }),

  dashboard: () => api<import("./types").DashboardSummary>("/dashboard/summary"),
  packs: () => api<import("./types").DiseasePack[]>("/disease-packs"),
  pack: (id: string) => api<import("./types").DiseasePack>(`/disease-packs/${id}`),

  projects: () => api<import("./types").Project[]>("/projects"),
  project: (id: string) => api<import("./types").ProjectDetail>(`/projects/${id}`),
  createProject: (body: { name: string; description?: string; disease_pack: string }) =>
    api<import("./types").Project>("/projects", { method: "POST", body }),
  updateProject: (id: string, body: Partial<{ name: string; description: string; archived: boolean }>) =>
    api<import("./types").Project>(`/projects/${id}`, { method: "PATCH", body }),
  archiveProject: (id: string) =>
    api<{ ok: boolean }>(`/projects/${id}`, { method: "DELETE" }),

  samples: (projectId: string) =>
    api<import("./types").Sample[]>(`/projects/${projectId}/samples`),
  sample: (id: string) => api<import("./types").SampleDetail>(`/samples/${id}`),
  createSample: (projectId: string, form: FormData) =>
    api<import("./types").SampleDetail>(`/projects/${projectId}/samples`, {
      method: "POST",
      body: form,
    }),
  deleteSample: (id: string) =>
    api<{ ok: boolean }>(`/samples/${id}`, { method: "DELETE" }),

  runs: (params?: { project_id?: string; sample_id?: string; status?: string }) => {
    const query = new URLSearchParams();
    if (params?.project_id) query.set("project_id", params.project_id);
    if (params?.sample_id) query.set("sample_id", params.sample_id);
    if (params?.status) query.set("status", params.status);
    const suffix = query.size ? `?${query.toString()}` : "";
    return api<import("./types").Run[]>(`/runs${suffix}`);
  },
  run: (id: string) => api<import("./types").RunDetail>(`/runs/${id}`),
  createRun: (sampleId: string, body: { disease_pack?: string; params?: Record<string, unknown> }) =>
    api<import("./types").Run>(`/samples/${sampleId}/runs`, { method: "POST", body }),
  compareRuns: (a: string, b: string) =>
    api<import("./types").RunComparison>(
      `/runs/compare?${new URLSearchParams({ a, b }).toString()}`,
    ),
  results: (id: string) =>
    api<{ run_id: string; payload: import("./types").ResultPayload }>(`/runs/${id}/results`),
  retryRun: (id: string) => api<import("./types").Run>(`/runs/${id}/retry`, { method: "POST" }),
  cancelRun: (id: string) =>
    api<{ ok: boolean }>(`/runs/${id}/cancel`, { method: "POST" }),
  approveReport: (id: string, body: { confirm_ruo: boolean; note?: string }) =>
    api<import("./types").ReportState>(`/runs/${id}/report/approve`, { method: "POST", body }),

  org: () => api<import("./types").Organization>("/org"),
  members: () => api<import("./types").Member[]>("/org/members"),
  auditLogs: () => api<import("./types").AuditLog[]>("/org/audit-logs"),
  updateOrg: (body: { name: string }) =>
    api<import("./types").Organization>("/org", { method: "PATCH", body }),
};
