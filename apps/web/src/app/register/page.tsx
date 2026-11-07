import Link from "next/link";
import { ArrowLeft, ArrowRight, FlaskConical } from "lucide-react";
import { SiteHeader } from "@/components/marketing/site-header";
import { SiteFooter } from "@/components/marketing/site-footer";

export const metadata = { title: "Research preview" };

export default function RegisterPage() {
  return (
    <div className="min-h-screen">
      <SiteHeader />
      <main className="container-page flex min-h-[65vh] items-center justify-center py-16">
        <section className="card w-full max-w-xl p-7 sm:p-9">
          <span className="flex size-11 items-center justify-center rounded-2xl bg-[#edf4ef] text-teal"><FlaskConical className="size-5" /></span>
          <p className="mono-label mt-6">Research preview</p>
          <h1 className="display mt-3 text-4xl text-bone">New workspace access is paused.</h1>
          <p className="mt-4 text-sm leading-7 text-bone-dim">
            Topiome is rebuilding its research product around cellular perturbation-response modeling. The prediction workflow is not available yet, so new accounts are not being opened for the archived spatial-analysis workspace.
          </p>
          <div className="mt-7 flex flex-wrap gap-3">
            <Link href="/" className="inline-flex h-10 items-center gap-2 rounded-xl bg-teal px-4 text-xs font-medium text-white hover:bg-[#125f50]">View research direction <ArrowRight className="size-3.5" /></Link>
            <Link href="/login" className="inline-flex h-10 items-center gap-2 rounded-xl border border-line px-4 text-xs text-bone-dim hover:text-bone"><ArrowLeft className="size-3.5" /> Existing account</Link>
          </div>
        </section>
      </main>
      <SiteFooter />
    </div>
  );
}
