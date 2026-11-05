"use client";

import { cn } from "@/lib/utils";
import { useState } from "react";

interface Tab {
  id: string;
  label: string;
  content: React.ReactNode;
}

export function Tabs({
  tabs,
  defaultTab,
  className,
}: {
  tabs: Tab[];
  defaultTab?: string;
  className?: string;
}) {
  const [active, setActive] = useState(defaultTab ?? tabs[0]?.id);
  const current = tabs.find((tab) => tab.id === active) ?? tabs[0];

  return (
    <div className={className}>
      <div className="flex flex-wrap gap-1 border-b border-line">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActive(tab.id)}
            className={cn(
              "relative px-3 py-2.5 text-xs font-medium transition focus-ring",
              active === tab.id ? "text-bone" : "text-slate hover:text-bone-dim",
            )}
          >
            {tab.label}
            {active === tab.id ? (
              <span className="absolute inset-x-2 -bottom-px h-px bg-acid" />
            ) : null}
          </button>
        ))}
      </div>
      <div className="pt-4">{current?.content}</div>
    </div>
  );
}
