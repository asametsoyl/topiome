"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ArrowRight, Sparkles } from "lucide-react";
import { AuthShell } from "@/components/auth/auth-shell";
import { Button } from "@/components/ui/button";
import { Field, Input } from "@/components/ui/input";
import { useAuth } from "@/lib/auth";
import { useToast } from "@/lib/toast";
import { errorMessage } from "@/lib/utils";

export default function LoginPage() {
  const router = useRouter();
  const { me, loading, login, demoLogin } = useAuth();
  const { toast } = useToast();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [demoSubmitting, setDemoSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && me) router.replace("/app");
  }, [loading, me, router]);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await login(email.trim(), password);
      router.push("/app");
    } catch (err) {
      setError(errorMessage(err));
      setSubmitting(false);
    }
  }

  async function handleDemo() {
    setDemoSubmitting(true);
    setError(null);
    try {
      await demoLogin();
      toast("Demo workspace ready. Exploring synthetic breast data.", "success");
      router.push("/app");
    } catch (err) {
      setError(errorMessage(err));
      setDemoSubmitting(false);
    }
  }

  return (
    <AuthShell
      title="Welcome back."
      subtitle="Sign in to your research workspace to continue an analysis."
      footer={
        <>
          New to Topiome?{" "}
          <Link href="/register" className="font-medium text-acid hover:underline underline-offset-2">
            Create an account
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Email">
          <Input
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="you@lab.edu"
          />
        </Field>
        <Field label="Password">
          <Input
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="••••••••••"
          />
        </Field>

        {error ? (
          <p className="rounded-lg border border-coral/30 bg-coral/[0.06] px-3 py-2 text-xs text-coral">
            {error}
          </p>
        ) : null}

        <Button type="submit" className="w-full" loading={submitting}>
          Sign in
          {!submitting ? <ArrowRight className="size-4" /> : null}
        </Button>
      </form>

      <div className="my-5 flex items-center gap-3">
        <span className="h-px flex-1 bg-line" />
        <span className="font-mono text-[9px] uppercase tracking-[0.14em] text-slate">or</span>
        <span className="h-px flex-1 bg-line" />
      </div>

      <Button
        type="button"
        variant="secondary"
        className="w-full"
        onClick={handleDemo}
        loading={demoSubmitting}
      >
        {!demoSubmitting ? <Sparkles className="size-4 text-acid" /> : null}
        Explore the demo workspace
      </Button>

      <p className="mt-4 text-center text-[11px] leading-relaxed text-slate">
        Demo credentials:{" "}
        <span className="font-mono text-bone-dim">demo@topiome.com</span> /{" "}
        <span className="font-mono text-bone-dim">demo1234</span>
      </p>
    </AuthShell>
  );
}
