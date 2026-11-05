import { cn } from "@/lib/utils";
import type { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger" | "outline";
type Size = "sm" | "md" | "lg";

const variants: Record<Variant, string> = {
  primary:
    "bg-acid text-ink hover:bg-[#d6ff6a] active:bg-[#b8e847] border border-acid shadow-[0_0_0_1px_rgba(200,247,81,0.15)]",
  secondary:
    "bg-bone/5 text-bone border border-line hover:border-[#3a4d41] hover:bg-bone/10",
  ghost: "bg-transparent text-bone-dim border border-transparent hover:bg-bone/5 hover:text-bone",
  danger: "bg-coral/10 text-coral border border-coral/40 hover:bg-coral/20",
  outline: "bg-transparent text-acid border border-acid/50 hover:bg-acid/10",
};

const sizes: Record<Size, string> = {
  sm: "h-8 px-3 text-xs gap-1.5 rounded-lg",
  md: "h-10 px-4 text-sm gap-2 rounded-xl",
  lg: "h-12 px-6 text-sm gap-2 rounded-xl",
};

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
}

export function Button({
  className,
  variant = "primary",
  size = "md",
  loading = false,
  disabled,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center font-medium transition-colors focus-ring disabled:cursor-not-allowed disabled:opacity-50",
        variants[variant],
        sizes[size],
        className,
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <span className="size-3.5 animate-spin rounded-full border-2 border-current/30 border-t-current" />
      ) : null}
      {children}
    </button>
  );
}
