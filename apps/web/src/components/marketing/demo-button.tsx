"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { ArrowRight } from "lucide-react";
import { Button, type ButtonProps } from "@/components/ui/button";
import { useAuth } from "@/lib/auth";
import { useToast } from "@/lib/toast";
import { errorMessage } from "@/lib/utils";

export function DemoButton({
  children = "Launch live demo",
  className,
  variant = "primary",
  size = "lg",
  showArrow = true,
}: {
  children?: React.ReactNode;
  className?: string;
  variant?: ButtonProps["variant"];
  size?: ButtonProps["size"];
  showArrow?: boolean;
}) {
  const router = useRouter();
  const { demoLogin } = useAuth();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);

  async function handleDemo() {
    setLoading(true);
    try {
      await demoLogin();
      router.push("/app");
    } catch (error) {
      toast(errorMessage(error), "error");
      setLoading(false);
    }
  }

  return (
    <Button
      onClick={handleDemo}
      loading={loading}
      variant={variant}
      size={size}
      className={className}
    >
      {children}
      {showArrow && !loading ? <ArrowRight className="size-4" /> : null}
    </Button>
  );
}
