import Link from "next/link";
import { ArrowLeft, ShieldAlert } from "lucide-react";
import { Logo } from "@/components/ui/logo";

export function AuthShell({
  title,
  subtitle,
  children,
  footer,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
  footer: React.ReactNode;
}) {
  return (
    <div className="grid min-h-screen lg:grid-cols-[1fr_1.05fr]">
      {/* Brand panel */}
      <aside className="relative hidden overflow-hidden border-r border-line bg-ink-2 lg:flex lg:flex-col lg:justify-between">
        <div className="pointer-events-none absolute inset-0 grid-bg opacity-70" />
        <div className="pointer-events-none absolute -right-24 top-1/3 size-[420px] rounded-full bg-teal/10 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-32 -left-16 size-[360px] rounded-full bg-acid/5 blur-3xl" />

        <div className="relative p-10">
          <Link href="/" className="focus-ring inline-block rounded-lg" aria-label="Topiome home">
            <Logo />
          </Link>
        </div>

        <div className="relative px-10 pb-10">
          <p className="mono-label">Spatial disease atlas platform</p>
          <h2 className="display mt-5 max-w-md text-5xl text-bone">
            Every spot has
            <br />
            a <span className="text-acid">story.</span>
          </h2>
          <p className="mt-5 max-w-sm text-sm leading-relaxed text-bone-dim">
            Cell composition, spatially coherent domains, and target evidence — with uncertainty
            visible on every spot and a report your team can defend.
          </p>

          <div className="mt-10 grid max-w-sm grid-cols-3 gap-px overflow-hidden rounded-xl border border-line bg-line">
            {[
              { k: "6", v: "disease packs" },
              { k: "0.099", v: "breast JSD" },
              { k: "100%", v: "RUO" },
            ].map((item) => (
              <div key={item.v} className="bg-ink-2 px-3 py-3">
                <p className="font-mono text-lg tracking-tight text-bone">{item.k}</p>
                <p className="mt-0.5 text-[10px] leading-tight text-slate">{item.v}</p>
              </div>
            ))}
          </div>

          <div className="mt-8 flex items-start gap-2.5 rounded-xl border border-amber/20 bg-amber/[0.05] px-4 py-3">
            <ShieldAlert className="mt-0.5 size-3.5 shrink-0 text-amber" />
            <p className="text-[11px] leading-relaxed text-amber/80">
              For Research Use Only. Not for diagnosis, prognosis, treatment selection, or
              clinical decision-making.
            </p>
          </div>
        </div>
      </aside>

      {/* Form panel */}
      <main className="relative flex min-h-screen flex-col bg-ink">
        <div className="flex items-center justify-between p-6 lg:justify-end">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-xs text-slate transition hover:text-bone lg:hidden"
          >
            <ArrowLeft className="size-3.5" />
            Back
          </Link>
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-xs text-slate transition hover:text-bone"
          >
            <ArrowLeft className="size-3.5" />
            Back to site
          </Link>
        </div>

        <div className="flex flex-1 items-center justify-center px-6 pb-10">
          <div className="w-full max-w-sm animate-fade-up">
            <div className="lg:hidden">
              <Logo />
            </div>
            <p className="mono-label mt-8 lg:mt-0">Workspace access</p>
            <h1 className="display mt-2 text-4xl text-bone">{title}</h1>
            <p className="mt-2 text-sm leading-relaxed text-bone-dim">{subtitle}</p>

            <div className="mt-8">{children}</div>
            <div className="mt-6 text-center text-xs text-slate">{footer}</div>
          </div>
        </div>

        <div className="border-t border-line px-6 py-4">
          <p className="text-center text-[10px] leading-relaxed text-slate">
            Protected by organization-level isolation and audit logging. Research use only.
          </p>
        </div>
      </main>
    </div>
  );
}
