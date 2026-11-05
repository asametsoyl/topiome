import { cn } from "@/lib/utils";

export function Logo({
  className,
  markOnly = false,
}: {
  className?: string;
  markOnly?: boolean;
}) {
  return (
    <span className={cn("inline-flex items-center gap-2.5", className)}>
      <svg
        viewBox="0 0 32 32"
        className="size-7 shrink-0"
        fill="none"
        aria-hidden="true"
      >
        <path
          d="M16 2.6 27 9v14L16 29.4 5 23V9L16 2.6Z"
          stroke="currentColor"
          strokeWidth="1.1"
          opacity="0.55"
        />
        <path
          d="M10.2 19.5c0-3.2 2.6-5.8 5.8-5.8s5.8 2.6 5.8 5.8"
          stroke="var(--color-acid)"
          strokeWidth="1.4"
          strokeLinecap="round"
        />
        <path
          d="M12.9 22.1c0-1.7 1.4-3.1 3.1-3.1s3.1 1.4 3.1 3.1"
          stroke="var(--color-teal)"
          strokeWidth="1.4"
          strokeLinecap="round"
        />
        <circle cx="16" cy="21.4" r="1.5" fill="var(--color-acid)" />
      </svg>
      {markOnly ? null : (
        <span className="text-[19px] font-semibold tracking-[-0.04em] text-bone">
          topiome
        </span>
      )}
    </span>
  );
}
