"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ArrowRight, Check } from "lucide-react";
import { AuthShell } from "@/components/auth/auth-shell";
import { Button } from "@/components/ui/button";
import { Field, Input } from "@/components/ui/input";
import { useAuth } from "@/lib/auth";
import { useToast } from "@/lib/toast";
import { errorMessage } from "@/lib/utils";

const MIN_PASSWORD = 10;

export default function RegisterPage() {
  const router = useRouter();
  const { me, loading, register } = useAuth();
  const { toast } = useToast();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [orgName, setOrgName] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && me) router.replace("/app");
  }, [loading, me, router]);

  const passwordOk = password.length >= MIN_PASSWORD;
  const matches = password.length > 0 && password === confirm;

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    if (!passwordOk) {
      setError(`Password must be at least ${MIN_PASSWORD} characters.`);
      return;
    }
    if (!matches) {
      setError("Passwords do not match.");
      return;
    }
    setSubmitting(true);
    try {
      await register({
        name: name.trim(),
        email: email.trim(),
        password,
        org_name: orgName.trim() || undefined,
      });
      toast("Workspace created. Welcome to Topiome.", "success");
      router.push("/app");
    } catch (err) {
      setError(errorMessage(err));
      setSubmitting(false);
    }
  }

  return (
    <AuthShell
      title="Create your lab."
      subtitle="Start with the synthetic demo, then bring your own Visium data."
      footer={
        <>
          Already have an account?{" "}
          <Link href="/login" className="font-medium text-acid hover:underline underline-offset-2">
            Sign in
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Full name">
          <Input
            autoComplete="name"
            required
            minLength={2}
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="Ada Lovelace"
          />
        </Field>
        <Field label="Work email">
          <Input
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="you@lab.edu"
          />
        </Field>
        <Field label="Lab or organization" hint="Optional — we will name the workspace for you.">
          <Input
            autoComplete="organization"
            value={orgName}
            onChange={(event) => setOrgName(event.target.value)}
            placeholder="Spatial Biology Lab"
          />
        </Field>
        <Field
          label="Password"
          hint={
            <span className="inline-flex items-center gap-1">
              {password.length > 0 ? (
                passwordOk ? (
                  <Check className="size-3 text-teal" />
                ) : null
              ) : null}
              At least {MIN_PASSWORD} characters.
            </span>
          }
        >
          <Input
            type="password"
            autoComplete="new-password"
            required
            minLength={MIN_PASSWORD}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="••••••••••"
          />
        </Field>
        <Field
          label="Confirm password"
          hint={confirm.length > 0 && !matches ? "Passwords do not match." : undefined}
        >
          <Input
            type="password"
            autoComplete="new-password"
            required
            value={confirm}
            onChange={(event) => setConfirm(event.target.value)}
            placeholder="••••••••••"
          />
        </Field>

        {error ? (
          <p className="rounded-lg border border-coral/30 bg-coral/[0.06] px-3 py-2 text-xs text-coral">
            {error}
          </p>
        ) : null}

        <Button type="submit" className="w-full" loading={submitting}>
          Create workspace
          {!submitting ? <ArrowRight className="size-4" /> : null}
        </Button>
      </form>

      <p className="mt-4 text-center text-[10px] leading-relaxed text-slate">
        By creating an account you agree to the{" "}
        <Link href="/legal/terms" className="text-bone-dim underline underline-offset-2">
          terms
        </Link>{" "}
        and{" "}
        <Link href="/legal/privacy" className="text-bone-dim underline underline-offset-2">
          privacy policy
        </Link>
        . Research use only.
      </p>
    </AuthShell>
  );
}
