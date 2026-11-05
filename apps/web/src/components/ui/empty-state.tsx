import { cn } from "@/lib/utils";
import { FlaskConical } from "lucide-react";

export function EmptyState({
  title,
  description,
  action,
  className,
  compact = false,
}: {
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
  compact?: boolean;
}) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center rounded-xl border border-dashed border-line bg-ink-2/60 text-center",
        compact ? "px-4 py-8" : "px-6 py-14",
        className,
      )}
    >
      <span className="mb-3 flex size-10 items-center justify-center rounded-full border border-line bg-ink-3 text-teal">
        <FlaskConical className="size-4" />
      </span>
      <p className="text-sm font-medium text-bone">{title}</p>
      {description ? (
        <p className="mt-1 max-w-sm text-xs leading-relaxed text-slate">{description}</p>
      ) : null}
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}
