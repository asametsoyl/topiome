"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { ArrowRight } from "lucide-react";
import { AuthShell } from "@/components/auth/auth-shell";
import { Button } from "@/components/ui/button";
import { Field, Input } from "@/components/ui/input";
import { apiClient } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { errorMessage } from "@/lib/utils";

export default function InvitationForm({ token }: { token: string }) {
  const router = useRouter();
  const { refresh } = useAuth();
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [totpCode, setTotpCode] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function accept(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await apiClient.acceptInvitation({
        token,
        name: name.trim() || undefined,
        password: password || undefined,
        totp_code: totpCode || undefined,
      });
      await refresh();
      router.replace("/app");
    } catch (cause) {
      setError(errorMessage(cause));
      setBusy(false);
    }
  }

  return (
    <AuthShell
      title="Join your team."
      subtitle="Accept the workspace invitation to continue. New accounts need a name and a secure password."
      footer={<>Already have access? <Link href="/login" className="text-acid hover:underline">Sign in</Link></>}
    >
      {token ? (
        <form onSubmit={accept} className="space-y-4">
          <Field label="Full name" hint="Leave blank if you already have a Topiome account.">
            <Input autoComplete="name" minLength={2} value={name} onChange={(event) => setName(event.target.value)} />
          </Field>
          <Field label="Create password" hint="Leave blank for an existing account. At least 10 characters.">
            <Input type="password" autoComplete="new-password" minLength={10} value={password} onChange={(event) => setPassword(event.target.value)} />
          </Field>
          <Field label="Authenticator code" hint="Required only for accounts with MFA enabled. A recovery code also works.">
            <Input inputMode="numeric" autoComplete="one-time-code" value={totpCode} onChange={(event) => setTotpCode(event.target.value)} />
          </Field>
          {error ? <p className="rounded-lg border border-coral/30 bg-coral/[0.06] px-3 py-2 text-xs text-coral">{error}</p> : null}
          <Button type="submit" className="w-full" loading={busy}>
            Accept invitation {!busy ? <ArrowRight className="size-4" /> : null}
          </Button>
        </form>
      ) : (
        <p className="rounded-lg border border-coral/30 bg-coral/[0.06] px-3 py-2 text-xs text-coral">
          This invitation link is missing its token. Ask the workspace admin to send a new invitation.
        </p>
      )}
      <p className="mt-5 text-center text-[10px] leading-relaxed text-slate">
        Research Use Only. Not for diagnosis, prognosis, treatment selection, or clinical decision-making.
      </p>
    </AuthShell>
  );
}
