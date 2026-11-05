"use client";

import { useCallback, useEffect, useEffectEvent, useState } from "react";

function sameDeps(a: readonly unknown[], b: readonly unknown[]) {
  return a.length === b.length && a.every((value, index) => Object.is(value, b[index]));
}

export function useApiData<T>(fetcher: () => Promise<T>, deps: unknown[] = []) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [nonce, setNonce] = useState(0);

  // Mark a new request as loading during render when inputs change, so the effect
  // below only talks to the network and never sets state synchronously.
  const key = [...deps, nonce];
  const [lastKey, setLastKey] = useState<unknown[]>(key);
  if (!sameDeps(lastKey, key)) {
    setLastKey(key);
    setLoading(true);
    setError(null);
  }

  const load = useEffectEvent(() => fetcher());

  useEffect(() => {
    let alive = true;
    load()
      .then((value) => {
        if (alive) setData(value);
      })
      .catch((err: unknown) => {
        if (alive) setError(err instanceof Error ? err : new Error("Request failed"));
      })
      .finally(() => {
        if (alive) setLoading(false);
      });
    return () => {
      alive = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, nonce]);

  const reload = useCallback(() => setNonce((value) => value + 1), []);

  return { data, loading, error, reload, setData };
}
