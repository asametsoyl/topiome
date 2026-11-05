"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Play } from "lucide-react";
import { Button, type ButtonProps } from "@/components/ui/button";
import { apiClient } from "@/lib/api";
import { useToast } from "@/lib/toast";
import { errorMessage } from "@/lib/utils";

export function RunSampleButton({
  sampleId,
  diseasePack,
  label = "Run",
  variant = "primary",
  size = "sm",
  className,
}: {
  sampleId: string;
  diseasePack?: string;
  label?: string;
  variant?: ButtonProps["variant"];
  size?: ButtonProps["size"];
  className?: string;
}) {
  const router = useRouter();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);

  async function handleRun() {
    setLoading(true);
    try {
      const run = await apiClient.createRun(sampleId, {
        disease_pack: diseasePack,
        params: {},
      });
      toast("Run queued. The atlas will open when the pipeline starts.", "success");
      router.push(`/app/runs/${run.id}`);
    } catch (error) {
      toast(errorMessage(error), "error");
      setLoading(false);
    }
  }

  return (
    <Button
      type="button"
      size={size}
      variant={variant}
      loading={loading}
      onClick={handleRun}
      className={className}
    >
      {!loading ? <Play className="size-3.5" /> : null}
      {label}
    </Button>
  );
}
