import { SiteHeader } from "@/components/marketing/site-header";
import { SiteFooter } from "@/components/marketing/site-footer";
import { Badge } from "@/components/ui/badge";

export function LegalPage({
  title,
  updated,
  intro,
  children,
  draft = false,
}: {
  title: string;
  updated: string;
  intro: string;
  children: React.ReactNode;
  draft?: boolean;
}) {
  return (
    <div className="min-h-screen">
      <SiteHeader />
      <main>
        <section className="border-b border-line py-14">
          <div className="container-page max-w-3xl">
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="outline">Legal</Badge>
              {draft ? <Badge variant="amber">Draft · legal review pending</Badge> : null}
            </div>
            <h1 className="display mt-5 text-5xl text-bone">{title}</h1>
            <p className="mt-3 font-mono text-[10px] uppercase tracking-[0.14em] text-slate">
              Last updated {updated}
            </p>
            <p className="mt-5 text-sm leading-relaxed text-bone-dim">{intro}</p>
          </div>
        </section>
        <section className="py-12">
          <div className="container-page max-w-3xl space-y-8 text-sm leading-relaxed text-bone-dim">
            {children}
          </div>
        </section>
      </main>
      <SiteFooter />
    </div>
  );
}

export function LegalSection({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section>
      <h2 className="text-base font-medium text-bone">{title}</h2>
      <div className="mt-3 space-y-3 text-sm leading-relaxed text-bone-dim">{children}</div>
    </section>
  );
}
