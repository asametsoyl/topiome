"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ArrowRight } from "lucide-react";
import { AuthShell } from "@/components/auth/auth-shell";
import { Button } from "@/components/ui/button";
import { Field, Input } from "@/components/ui/input";
import { useAuth } from "@/lib/auth";
import { errorMessage } from "@/lib/utils";

export default function LoginPage() {
  const router = useRouter();
  const { me, loading, login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [totpCode, setTotpCode] = useState("");
  const [requiresMfa, setRequiresMfa] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && me) router.replace("/app");
  }, [loading, me, router]);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await login(email.trim(), password, totpCode || undefined);
      router.push("/app");
    } catch (err) {
      const message = errorMessage(err);
      if (message.toLowerCase().includes("mfa code required")) {
        setRequiresMfa(true);
        setError("Enter the code from your authenticator app, or use a recovery code.");
      } else {
        setError(message);
      }
      setSubmitting(false);
    }
  }

  return (
    <AuthShell
      title="Legacy workspace."
      subtitle="Sign in to view archived spatial-transcriptomics projects and analyses. The new perturbation-response research product is not available yet."
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
        {requiresMfa ? (
          <Field label="Authenticator or recovery code">
            <Input
              inputMode="numeric"
              autoComplete="one-time-code"
              required
              value={totpCode}
              onChange={(event) => setTotpCode(event.target.value)}
              placeholder="123456"
            />
          </Field>
        ) : null}

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

    </AuthShell>
  );
}
