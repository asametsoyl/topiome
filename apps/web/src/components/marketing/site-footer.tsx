import Link from "next/link";
import { Logo } from "@/components/ui/logo";

const groups = [
  {
    title: "Research",
    links: [
      { href: "/#research", label: "Scientific question" },
      { href: "/#method", label: "Validation approach" },
      { href: "/#status", label: "Project status" },
    ],
  },
  {
    title: "Methods",
    links: [
      { href: "/docs", label: "Research plan" },
      { href: "/docs#benchmark", label: "Benchmark design" },
      { href: "/docs#data", label: "Data sources" },
      { href: "/docs#limits", label: "Limitations" },
    ],
  },
  {
    title: "Company",
    links: [
      { href: "mailto:hello@topiome.com", label: "Contact" },
      { href: "/legal/ruo", label: "RUO policy" },
      { href: "/legal/privacy", label: "Privacy" },
      { href: "/legal/terms", label: "Terms" },
    ],
  },
];

export function SiteFooter() {
  return (
    <footer className="border-t border-line bg-ink-2">
      <div className="container-page py-14">
        <div className="grid gap-10 md:grid-cols-[1.4fr_repeat(3,1fr)]">
          <div>
            <Logo />
            <p className="mt-4 max-w-xs text-xs leading-relaxed text-slate">
              Computational research into cellular responses to defined interventions, with evidence and uncertainty made explicit.
            </p>
            <p className="mt-4 font-mono text-[10px] uppercase tracking-[0.14em] text-amber">
              For research use only
            </p>
          </div>
          {groups.map((group) => (
            <div key={group.title}>
              <p className="mono-label">{group.title}</p>
              <ul className="mt-3 space-y-2">
                {group.links.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      className="text-xs text-bone-dim transition hover:text-acid"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 flex flex-col gap-3 border-t border-line pt-6 text-[11px] text-slate md:flex-row md:items-center md:justify-between">
          <p>© {new Date().getFullYear()} Topiome. All rights reserved.</p>
          <p className="max-w-2xl leading-relaxed">
            Topiome is not intended for diagnosis, prognosis, treatment selection, or clinical
            decision-making. Results are computational inferences from research data and must be
            independently validated.
          </p>
        </div>
      </div>
    </footer>
  );
}
