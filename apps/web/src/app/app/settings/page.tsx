"use client";

import Link from "next/link";
import { useState } from "react";
import {
  ArrowUpRight,
  Building2,
  CheckCircle2,
  ClipboardList,
  CreditCard,
  Mail,
  ShieldAlert,
  ShieldCheck,
  Users,
  TriangleAlert,
} from "lucide-react";
import { PageHeader } from "@/components/app/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Field, Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/progress";
import { Tabs } from "@/components/ui/tabs";
import { apiClient } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useToast } from "@/lib/toast";
import type { AuditLog, Member, Organization } from "@/lib/types";
import { errorMessage, formatDateTime, relativeTime, titleCase } from "@/lib/utils";
import { useApiData } from "@/lib/use-api";

export default function SettingsPage() {
  const { me, refresh } = useAuth();
  const { toast } = useToast();

  const { data: org, loading: orgLoading, reload: reloadOrg } = useApiData<Organization>(
    () => apiClient.org(),
  );
  const { data: members, loading: membersLoading } = useApiData<Member[]>(() =>
    apiClient.members(),
  );
  const { data: auditLogs, loading: auditLoading } = useApiData<AuditLog[]>(() =>
    apiClient.auditLogs(),
  );

  const [name, setName] = useState("");
  const [saving, setSaving] = useState(false);

  // Prefill the form once the org loads (state adjusted during render, not in an effect).
  const [loadedOrgName, setLoadedOrgName] = useState<string | null>(null);
  if (org && org.name !== loadedOrgName) {
    setLoadedOrgName(org.name);
    setName(org.name);
  }

  const canManage = me?.role === "owner" || me?.role === "admin";

  async function handleSave(event: React.FormEvent) {
    event.preventDefault();
    if (!name.trim()) return;
    setSaving(true);
    try {
      await apiClient.updateOrg({ name: name.trim() });
      toast("Organization updated.", "success");
      reloadOrg();
      await refresh();
    } catch (err) {
      toast(errorMessage(err), "error");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Workspace"
        title="Settings"
        description="Organization profile, members, audit history, and plan. Data is isolated per organization."
        actions={<Badge variant="outline">{titleCase(me?.role ?? "member")}</Badge>}
      />

      <Tabs
        tabs={[
          {
            id: "organization",
            label: "Organization",
            content: (
              <div className="grid gap-5 lg:grid-cols-[1.3fr_1fr]">
                <Card>
                  <CardHeader
                    title="Organization profile"
                    description="Shown across the workspace and on shared reports."
                    action={<Building2 className="size-4 text-slate" />}
                  />
                  <CardBody>
                    {orgLoading || !org ? (
                      <div className="space-y-3">
                        <Skeleton className="h-10" />
                        <Skeleton className="h-10" />
                      </div>
                    ) : (
                      <form onSubmit={handleSave} className="space-y-4">
                        <Field label="Organization name">
                          <Input
                            value={name}
                            onChange={(event) => setName(event.target.value)}
                            disabled={!canManage}
                            minLength={2}
                          />
                        </Field>
                        <div className="grid gap-4 sm:grid-cols-2">
                          <Field label="Workspace slug">
                            <Input value={org.slug} disabled readOnly />
                          </Field>
                          <Field label="Plan">
                            <Input value={titleCase(org.plan)} disabled readOnly />
                          </Field>
                        </div>
                        <Field label="Workspace ID">
                          <Input value={org.id} disabled readOnly className="font-mono text-xs" />
                        </Field>
                        {canManage ? (
                          <div className="flex justify-end">
                            <Button type="submit" loading={saving} disabled={name.trim() === org.name}>
                              Save changes
                            </Button>
                          </div>
                        ) : (
                          <p className="text-[11px] text-slate">
                            Only owners and admins can edit organization settings.
                          </p>
                        )}
                      </form>
                    )}
                  </CardBody>
                </Card>

                <div className="space-y-5">
                  <Card>
                    <CardHeader title="Isolation & security" />
                    <CardBody className="space-y-2.5">
                      {[
                        "Organization-level data isolation",
                        "Role-based access control",
                        "Audit logging on writes",
                        "HttpOnly session cookies",
                        "Hashed credentials",
                      ].map((item) => (
                        <p
                          key={item}
                          className="flex items-center gap-2 text-[11px] text-bone-dim"
                        >
                          <CheckCircle2 className="size-3.5 shrink-0 text-teal" />
                          {item}
                        </p>
                      ))}
                      <Link
                        href="/legal/privacy"
                        className="mt-1 inline-flex items-center gap-1.5 border-t border-line pt-3 text-[11px] text-acid"
                      >
                        Privacy policy
                        <ArrowUpRight className="size-3" />
                      </Link>
                    </CardBody>
                  </Card>

                  <div className="flex items-start gap-2.5 rounded-xl border border-amber/20 bg-amber/[0.04] px-4 py-3">
                    <ShieldAlert className="mt-0.5 size-4 shrink-0 text-amber" />
                    <p className="text-[10px] leading-relaxed text-amber/80">
                      Research use only. Do not upload identifiable patient data without an
                      appropriate agreement and ethics approval.
                    </p>
                  </div>
                </div>
              </div>
            ),
          },
          {
            id: "members",
            label: "Members",
            content: (
              <Card className="overflow-hidden">
                <CardHeader
                  title="Members"
                  description="People with access to this workspace and their roles."
                  action={<Badge variant="outline">{members?.length ?? 0} seats</Badge>}
                />
                {membersLoading ? (
                  <div className="space-y-2 p-4">
                    {Array.from({ length: 2 }).map((_, index) => (
                      <Skeleton key={index} className="h-12" />
                    ))}
                  </div>
                ) : members && members.length > 0 ? (
                  <div className="divide-y divide-line-soft">
                    {members.map((member) => (
                      <div
                        key={member.id}
                        className="flex flex-col gap-2 px-4 py-3.5 sm:flex-row sm:items-center sm:px-5"
                      >
                        <span className="flex size-9 shrink-0 items-center justify-center rounded-full border border-line bg-ink-3 text-[11px] font-medium text-acid">
                          {member.name.slice(0, 2).toUpperCase()}
                        </span>
                        <div className="min-w-0 flex-1">
                          <div className="flex flex-wrap items-center gap-2">
                            <p className="text-xs font-medium text-bone">{member.name}</p>
                            {member.user_id === me?.user.id ? (
                              <Badge variant="acid">You</Badge>
                            ) : null}
                          </div>
                          <p className="mt-0.5 truncate font-mono text-[10px] text-slate">
                            {member.email}
                          </p>
                        </div>
                        <Badge variant={member.role === "owner" ? "teal" : "outline"}>
                          {titleCase(member.role)}
                        </Badge>
                        <span className="font-mono text-[9px] text-slate">
                          joined {relativeTime(member.created_at)}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-5">
                    <EmptyState compact title="No members" description="No members in this workspace." />
                  </div>
                )}
                <div className="flex flex-col gap-3 border-t border-line bg-ink-3/40 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
                  <p className="text-[10px] leading-relaxed text-slate">
                    Seat provisioning is manual during the pilot. Contact us to add or remove
                    members.
                  </p>
                  <a
                    href="mailto:hello@topiome.com?subject=Workspace%20seats"
                    className="inline-flex h-8 shrink-0 items-center gap-1.5 rounded-lg border border-line px-3 text-[10px] text-bone-dim transition hover:border-[#3a4d41] hover:text-bone"
                  >
                    <Mail className="size-3" />
                    Request seats
                  </a>
                </div>
              </Card>
            ),
          },
          {
            id: "audit",
            label: "Audit log",
            content: (
              <Card className="overflow-hidden">
                <CardHeader
                  title="Audit log"
                  description="Write actions recorded for this organization."
                  action={<Badge variant="outline">{auditLogs?.length ?? 0} events</Badge>}
                />
                {auditLoading ? (
                  <div className="space-y-2 p-4">
                    {Array.from({ length: 4 }).map((_, index) => (
                      <Skeleton key={index} className="h-10" />
                    ))}
                  </div>
                ) : auditLogs && auditLogs.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full min-w-[640px] text-left text-xs">
                      <thead className="border-b border-line bg-ink-3/40 font-mono text-[9px] uppercase tracking-[0.12em] text-slate">
                        <tr>
                          <th className="px-4 py-2.5 font-normal">Action</th>
                          <th className="px-4 py-2.5 font-normal">Resource</th>
                          <th className="px-4 py-2.5 font-normal">IP</th>
                          <th className="px-4 py-2.5 font-normal">When</th>
                        </tr>
                      </thead>
                      <tbody>
                        {auditLogs.map((log) => (
                          <tr key={log.id} className="border-b border-line-soft last:border-0">
                            <td className="px-4 py-3 font-mono text-[10px] text-bone-dim">
                              {log.action}
                            </td>
                            <td className="px-4 py-3">
                              <p className="font-mono text-[10px] text-slate">{log.resource_type}</p>
                              <p className="font-mono text-[9px] text-slate/70">
                                {log.resource_id.slice(0, 8)}
                              </p>
                            </td>
                            <td className="px-4 py-3 font-mono text-[10px] text-slate">
                              {log.ip || "—"}
                            </td>
                            <td className="px-4 py-3">
                              <p className="font-mono text-[10px] text-bone-dim">
                                {relativeTime(log.created_at)}
                              </p>
                              <p className="font-mono text-[9px] text-slate">
                                {formatDateTime(log.created_at)}
                              </p>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="p-5">
                    <EmptyState
                      compact
                      title="No audit events yet"
                      description="Project, sample, and run actions appear here as they happen."
                    />
                  </div>
                )}
              </Card>
            ),
          },
          {
            id: "plan",
            label: "Plan",
            content: (
              <div className="grid gap-5 lg:grid-cols-[1.2fr_1fr]">
                <Card className="overflow-hidden">
                  <div className="h-1 w-full bg-gradient-to-r from-teal via-acid to-amber" />
                  <CardHeader
                    title={titleCase(org?.plan ?? "academic")}
                    description="Current workspace plan."
                    action={<Badge variant="teal">Active</Badge>}
                  />
                  <CardBody className="space-y-4">
                    <div className="grid grid-cols-2 gap-3">
                      {[
                        ["Projects", "Seeded demo"],
                        ["Members", `${members?.length ?? 0} seat${members?.length === 1 ? "" : "s"}`],
                        ["Support", org?.plan === "academic" ? "Community" : "Priority"],
                        ["Billing", org?.plan === "academic" ? "Free" : "Annual"],
                      ].map(([key, value]) => (
                        <div key={key} className="rounded-xl border border-line bg-ink-3/50 px-3 py-2.5">
                          <p className="mono-label">{key}</p>
                          <p className="mt-1 text-xs text-bone-dim">{value}</p>
                        </div>
                      ))}
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <Link
                        href="/pricing"
                        className="inline-flex h-9 items-center gap-1.5 rounded-xl bg-acid px-3.5 text-xs font-medium text-ink transition hover:bg-[#d6ff6a]"
                      >
                        Compare plans
                        <ArrowUpRight className="size-3.5" />
                      </Link>
                      <a
                        href="mailto:hello@topiome.com?subject=Topiome%20institution%20plan"
                        className="inline-flex h-9 items-center gap-1.5 rounded-xl border border-line px-3.5 text-xs text-bone-dim transition hover:border-[#3a4d41] hover:text-bone"
                      >
                        <Mail className="size-3.5" />
                        Contact sales
                      </a>
                    </div>
                  </CardBody>
                </Card>

                <div className="space-y-5">
                  <Card>
                    <CardHeader title="Usage" description="This demo workspace." />
                    <CardBody className="space-y-2.5">
                      {[
                        ["Projects", "2"],
                        ["Members", `${members?.length ?? 0}`],
                        ["Audit events", `${auditLogs?.length ?? 0}`],
                        ["Disease packs", "6"],
                      ].map(([key, value]) => (
                        <div key={key} className="flex items-center justify-between text-[11px]">
                          <span className="text-slate">{key}</span>
                          <span className="font-mono text-bone-dim">{value}</span>
                        </div>
                      ))}
                    </CardBody>
                  </Card>

                  <div className="flex items-start gap-2.5 rounded-xl border border-line bg-ink-2/60 px-4 py-3">
                    <ShieldCheck className="mt-0.5 size-4 shrink-0 text-teal" />
                    <p className="text-[10px] leading-relaxed text-slate">
                      Academic plan eligibility requires an institutional email and approval.
                      Pilot pricing is available for the first three institutions per region.
                    </p>
                  </div>
                </div>
              </div>
            ),
          },
        ]}
      />

      <div className="flex flex-wrap items-center gap-x-5 gap-y-2 border-t border-line pt-4 text-[10px] text-slate">
        <span className="inline-flex items-center gap-1.5">
          <Users className="size-3" />
          {members?.length ?? 0} member{(members?.length ?? 0) === 1 ? "" : "s"}
        </span>
        <span className="inline-flex items-center gap-1.5">
          <ClipboardList className="size-3" />
          {auditLogs?.length ?? 0} audit events
        </span>
        <span className="inline-flex items-center gap-1.5">
          <CreditCard className="size-3" />
          {titleCase(org?.plan ?? "academic")} plan
        </span>
        <span className="inline-flex items-center gap-1.5 text-amber/80">
          <TriangleAlert className="size-3" />
          Research use only
        </span>
      </div>
    </div>
  );
}
