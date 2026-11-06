from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ── Auth ────────────────────────────────────────────────────────────────────


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    org_name: str | None = Field(default=None, max_length=160)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(ORMModel):
    id: str
    email: EmailStr
    name: str
    created_at: datetime


class OrgOut(ORMModel):
    id: str
    name: str
    slug: str
    plan: str


class MeOut(BaseModel):
    user: UserOut
    org: OrgOut
    role: str


# ── Projects ────────────────────────────────────────────────────────────────


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    description: str = ""
    disease_pack: str = Field(min_length=2, max_length=80)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        return value.strip()


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    description: str | None = None
    archived: bool | None = None


class ProjectOut(ORMModel):
    id: str
    name: str
    description: str
    disease_pack: str
    archived: bool
    created_at: datetime
    updated_at: datetime


class ProjectDetail(ProjectOut):
    samples: list[SampleOut] = []
    runs: list[RunOut] = []
    stats: dict[str, Any] = {}


# ── Samples ─────────────────────────────────────────────────────────────────


class SampleOut(ORMModel):
    id: str
    project_id: str
    name: str
    external_id: str
    disease_pack: str
    platform: str
    species: str
    condition: str
    sample_metadata: dict[str, Any]
    status: str
    spot_count: int | None
    created_at: datetime


class SampleDetail(SampleOut):
    files: list[SampleFileOut] = []
    runs: list[RunOut] = []


class SampleFileOut(ORMModel):
    id: str
    filename: str
    kind: str
    size_bytes: int
    created_at: datetime


# ── Runs ────────────────────────────────────────────────────────────────────


class RunCreate(BaseModel):
    disease_pack: str | None = None
    params: dict[str, Any] = {}


class RunOut(ORMModel):
    id: str
    project_id: str
    sample_id: str
    disease_pack: str
    pack_version: str
    pipeline_version: str
    status: str
    stage: str
    progress: float
    summary: dict[str, Any] | None
    error_code: str | None
    error_message: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime


class ReportStatusOut(BaseModel):
    status: str
    created_at: datetime
    approved_at: datetime | None = None
    approved_by_name: str | None = None
    approval_note: str = ""


class ReportApproveRequest(BaseModel):
    # The approver confirms they read the report and its Research Use Only limits.
    confirm_ruo: bool
    note: str = Field(default="", max_length=1000)


class RunDetail(RunOut):
    params: dict[str, Any]
    provenance: dict[str, Any] | None = None
    sample: SampleOut | None = None
    report: ReportStatusOut | None = None


class ResultOut(BaseModel):
    run_id: str
    payload: dict[str, Any]


# ── Run comparison ──────────────────────────────────────────────────────────


class CompareRunSide(BaseModel):
    label: str
    run_id: str
    sample_id: str
    sample_name: str | None
    project_id: str
    disease_pack: str
    pack_name: str
    pack_version: str
    pipeline_version: str
    created_at: datetime
    finished_at: datetime | None
    synthetic: bool
    n_spots: int
    modeled_spots: int
    n_domains: int
    n_cell_types: int
    method_agreement: float | None
    tested_interactions: int
    significant_interactions: int
    warnings: list[str]
    not_assessed: list[str]


class CompositionDelta(BaseModel):
    cell_type: str
    a: float | None  # mean proportion in run A; None if A's pack lacks this cell type
    b: float | None
    delta: float | None  # b - a


class DomainShare(BaseModel):
    id: str
    name: str
    color: str | None
    a_count: int | None  # None if A's pack does not define this domain
    a_pct: float | None  # % of spots
    b_count: int | None
    b_pct: float | None
    delta_pct: float | None  # b_pct - a_pct, percentage points


class InteractionSide(BaseModel):
    tested: bool
    score: float | None
    p_value: float | None
    q_value: float | None
    significant: bool
    missing: list[str]


class InteractionCompare(BaseModel):
    id: str
    name: str
    ligand: str
    receptor: str
    sender: str
    receiver: str
    category: str
    a: InteractionSide | None  # None if A's pack does not define this pair
    b: InteractionSide | None


class RunComparisonOut(BaseModel):
    a: CompareRunSide
    b: CompareRunSide
    same_pack: bool
    same_pack_version: bool
    warnings: list[str]
    composition: list[CompositionDelta]
    domains: list[DomainShare]
    communication: list[InteractionCompare]
    note: str


# ── Dashboard / org ─────────────────────────────────────────────────────────


class DashboardSummary(BaseModel):
    projects: int
    samples: int
    runs: int
    completed_runs: int
    failed_runs: int
    spots_analyzed: int
    recent_runs: list[RunOut]
    disease_packs: list[dict[str, Any]]


class MemberOut(BaseModel):
    id: str
    user_id: str
    name: str
    email: EmailStr
    role: str
    created_at: datetime


class AuditLogOut(ORMModel):
    id: str
    action: str
    resource_type: str
    resource_id: str
    ip: str
    log_metadata: dict[str, Any]
    created_at: datetime


ProjectDetail.model_rebuild()
SampleDetail.model_rebuild()
