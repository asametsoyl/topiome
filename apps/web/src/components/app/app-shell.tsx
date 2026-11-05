"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";
import {
  Activity,
  Blocks,
  ChevronDown,
  FlaskConical,
  FolderKanban,
  LayoutDashboard,
  LogOut,
  Menu,
  Settings,
  ShieldAlert,
  X,
} from "lucide-react";
import { Logo } from "@/components/ui/logo";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/progress";
import { useAuth } from "@/lib/auth";
import { useToast } from "@/lib/toast";
import { cn, titleCase } from "@/lib/utils";

const nav = [
  { href: "/app", label: "Dashboard", icon: LayoutDashboard, exact: true },
  { href: "/app/projects", label: "Projects", icon: FolderKanban },
  { href: "/app/runs", label: "Runs", icon: Activity },
  { href: "/app/packs", label: "Disease packs", icon: Blocks },
  { href: "/app/settings", label: "Settings", icon: Settings },
];

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { me, loading, logout } = useAuth();
  const { toast } = useToast();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    if (!loading && !me) router.replace("/login");
  }, [loading, me, router]);

  // Close menus on navigation (state adjusted during render, not in an effect).
  const [menuPath, setMenuPath] = useState(pathname);
  if (menuPath !== pathname) {
    setMenuPath(pathname);
    setMobileOpen(false);
    setMenuOpen(false);
  }

  async function handleLogout() {
    await logout();
    toast("Signed out.", "info");
    router.push("/");
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-ink">
        <div className="flex flex-col items-center gap-3">
          <Spinner />
          <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-slate">
            Loading workspace
          </p>
        </div>
      </div>
    );
  }

  if (!me) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-ink">
        <div className="flex flex-col items-center gap-3">
          <Spinner />
          <p className="text-xs text-slate">Redirecting to sign in…</p>
        </div>
      </div>
    );
  }

  const sidebar = (
    <div className="flex h-full flex-col">
      <div className="flex h-16 items-center justify-between border-b border-line px-5">
        <Link href="/app" className="focus-ring rounded-lg" aria-label="Topiome workspace">
          <Logo />
        </Link>
        <button
          type="button"
          onClick={() => setMobileOpen(false)}
          className="rounded-lg p-1.5 text-slate transition hover:bg-bone/5 hover:text-bone focus-ring lg:hidden"
          aria-label="Close menu"
        >
          <X className="size-4" />
        </button>
      </div>

      <div className="px-4 pt-5">
        <div className="rounded-xl border border-line bg-ink-3/60 px-3 py-2.5">
          <p className="font-mono text-[9px] uppercase tracking-[0.14em] text-slate">Workspace</p>
          <p className="mt-1 truncate text-xs font-medium text-bone">{me.org.name}</p>
          <div className="mt-1.5 flex items-center gap-1.5">
            <Badge variant="outline">{titleCase(me.org.plan)}</Badge>
            <Badge variant="neutral">{titleCase(me.role)}</Badge>
          </div>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-5">
        <p className="mono-label px-3 pb-2">Workspace</p>
        {nav.map((item) => {
          const Icon = item.icon;
          const active = item.exact
            ? pathname === item.href
            : pathname === item.href || pathname.startsWith(`${item.href}/`);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group flex items-center gap-2.5 rounded-xl px-3 py-2 text-xs transition focus-ring",
                active
                  ? "bg-acid/10 text-acid"
                  : "text-bone-dim hover:bg-bone/5 hover:text-bone",
              )}
              aria-current={active ? "page" : undefined}
            >
              <Icon className={cn("size-4 shrink-0", active ? "text-acid" : "text-slate")} />
              <span className="flex-1">{item.label}</span>
              {active ? <span className="size-1 rounded-full bg-acid" /> : null}
            </Link>
          );
        })}

        <p className="mono-label px-3 pb-2 pt-6">Resources</p>
        <Link
          href="/docs"
          className="group flex items-center gap-2.5 rounded-xl px-3 py-2 text-xs text-bone-dim transition hover:bg-bone/5 hover:text-bone focus-ring"
        >
          <FlaskConical className="size-4 shrink-0 text-slate" />
          <span className="flex-1">Methodology</span>
        </Link>
        <Link
          href="/pricing"
          className="group flex items-center gap-2.5 rounded-xl px-3 py-2 text-xs text-bone-dim transition hover:bg-bone/5 hover:text-bone focus-ring"
        >
          <Blocks className="size-4 shrink-0 text-slate" />
          <span className="flex-1">Plans</span>
        </Link>
      </nav>

      <div className="border-t border-line p-3">
        <div className="mb-2 flex items-start gap-2 rounded-xl border border-amber/20 bg-amber/[0.04] px-3 py-2.5">
          <ShieldAlert className="mt-0.5 size-3.5 shrink-0 text-amber" />
          <div>
            <p className="font-mono text-[9px] uppercase tracking-[0.12em] text-amber">
              Research use only
            </p>
            <p className="mt-1 text-[10px] leading-relaxed text-amber/70">
              Not for diagnosis or clinical decisions.
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={() => setMenuOpen((value) => !value)}
          className="flex w-full items-center gap-2.5 rounded-xl px-2 py-2 text-left transition hover:bg-bone/5 focus-ring"
          aria-expanded={menuOpen}
        >
          <span className="flex size-8 shrink-0 items-center justify-center rounded-full border border-line bg-ink-3 text-[11px] font-medium text-acid">
            {me.user.name.slice(0, 2).toUpperCase()}
          </span>
          <span className="min-w-0 flex-1">
            <span className="block truncate text-xs text-bone">{me.user.name}</span>
            <span className="block truncate text-[10px] text-slate">{me.user.email}</span>
          </span>
          <ChevronDown
            className={cn("size-3.5 text-slate transition", menuOpen && "rotate-180")}
          />
        </button>
        {menuOpen ? (
          <button
            type="button"
            onClick={handleLogout}
            className="mt-1 flex w-full items-center gap-2 rounded-lg px-3 py-2 text-xs text-coral transition hover:bg-coral/10 focus-ring"
          >
            <LogOut className="size-3.5" />
            Sign out
          </button>
        ) : null}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-ink">
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-60 border-r border-line bg-ink-2 lg:block">
        {sidebar}
      </aside>

      {mobileOpen ? (
        <div className="fixed inset-0 z-50 lg:hidden">
          <button
            type="button"
            className="absolute inset-0 bg-ink/80 backdrop-blur-sm"
            onClick={() => setMobileOpen(false)}
            aria-label="Close menu overlay"
          />
          <aside className="relative h-full w-72 border-r border-line bg-ink-2">{sidebar}</aside>
        </div>
      ) : null}

      <div className="lg:pl-60">
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between gap-4 border-b border-line bg-ink/90 px-5 backdrop-blur-xl md:px-8">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setMobileOpen(true)}
              className="rounded-lg p-2 text-bone transition hover:bg-bone/5 focus-ring lg:hidden"
              aria-label="Open menu"
            >
              <Menu className="size-5" />
            </button>
            <div className="hidden items-center gap-2 sm:flex">
              <span className="size-1.5 rounded-full bg-teal" />
              <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-slate">
                {me.org.slug}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="hidden items-center gap-1.5 rounded-full border border-amber/30 bg-amber/[0.07] px-2.5 py-1 font-mono text-[9px] uppercase tracking-[0.12em] text-amber sm:inline-flex">
              <ShieldAlert className="size-3" />
              RUO
            </span>
            <Link
              href="/app/projects?new=1"
              className="inline-flex h-9 items-center rounded-xl bg-acid px-3.5 text-xs font-medium text-ink transition hover:bg-[#d6ff6a] focus-ring"
            >
              New project
            </Link>
          </div>
        </header>

        <main className="mx-auto w-full max-w-[1280px] px-5 py-7 md:px-8 md:py-9">
          {children}
        </main>
      </div>
    </div>
  );
}
