import { Badge } from "@/components/ui/badge";
import type { RunStatus } from "@/lib/types";

const config: Record<
  RunStatus,
  { label: string; variant: "neutral" | "acid" | "teal" | "amber" | "coral" }
> = {
  queued: { label: "Queued", variant: "neutral" },
  running: { label: "Running", variant: "amber" },
  succeeded: { label: "Completed", variant: "teal" },
  failed: { label: "Failed", variant: "coral" },
  cancelled: { label: "Cancelled", variant: "neutral" },
};

export function StatusBadge({ status }: { status: RunStatus | string }) {
  const item = config[status as RunStatus] ?? {
    label: status,
    variant: "neutral" as const,
  };
  return <Badge variant={item.variant}>{item.label}</Badge>;
}
