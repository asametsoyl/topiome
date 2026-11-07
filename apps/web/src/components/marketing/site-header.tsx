"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { Menu, X } from "lucide-react";
import { Logo } from "@/components/ui/logo";
import { RuoNotice } from "@/components/ui/ruo-notice";
import { cn } from "@/lib/utils";

const links = [
  { href: "/#research", label: "Research" },
  { href: "/#method", label: "Validation" },
  { href: "/#status", label: "Status" },
  { href: "/docs", label: "Docs" },
];

export function SiteHeader() {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    const frame = window.requestAnimationFrame(onScroll);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      window.cancelAnimationFrame(frame);
      window.removeEventListener("scroll", onScroll);
    };
  }, []);

  // Close the mobile menu on navigation (state adjusted during render, not in an effect).
  const [menuPath, setMenuPath] = useState(pathname);
  if (menuPath !== pathname) {
    setMenuPath(pathname);
    setOpen(false);
  }

  return (
    <>
      <div className="border-b border-line bg-ink-2/80">
        <div className="container-page flex items-center justify-center py-1.5">
          <RuoNotice compact className="border-none bg-transparent px-0 py-0 text-[8px]" />
        </div>
      </div>
      <header
        className={cn(
          "sticky top-0 z-40 border-b transition-colors",
          scrolled
            ? "border-line bg-ink/90 backdrop-blur-xl"
            : "border-transparent bg-transparent",
        )}
      >
        <div className="container-page flex h-16 items-center justify-between gap-6">
          <Link href="/" className="focus-ring rounded-lg" aria-label="Topiome home">
            <Logo />
          </Link>

          <nav className="hidden items-center gap-6 lg:flex">
            {links.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="text-xs text-bone-dim transition hover:text-bone"
              >
                {link.label}
              </Link>
            ))}
          </nav>

          <div className="hidden items-center gap-2 sm:flex">
            <Link
              href="/#status"
              className="inline-flex h-9 items-center rounded-xl bg-teal px-4 text-xs font-medium text-white transition hover:bg-[#125f50]"
            >
              Research preview
            </Link>
          </div>

          <button
            type="button"
            onClick={() => setOpen((value) => !value)}
            className="rounded-lg p-2 text-bone transition hover:bg-bone/5 focus-ring lg:hidden"
            aria-label="Toggle menu"
            aria-expanded={open}
          >
            {open ? <X className="size-5" /> : <Menu className="size-5" />}
          </button>
        </div>

        {open ? (
          <div className="border-t border-line bg-ink px-5 py-4 lg:hidden">
            <nav className="flex flex-col gap-1">
              {links.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="rounded-lg px-3 py-2.5 text-sm text-bone-dim transition hover:bg-bone/5 hover:text-bone"
                >
                  {link.label}
                </Link>
              ))}
            </nav>
            <div className="mt-3 flex gap-2 border-t border-line pt-3">
              <Link
                href="/#status"
                className="flex h-10 flex-1 items-center justify-center rounded-xl bg-teal text-xs font-medium text-white"
              >
                Research preview
              </Link>
            </div>
          </div>
        ) : null}
      </header>
    </>
  );
}
