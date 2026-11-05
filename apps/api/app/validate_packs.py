from __future__ import annotations

import sys

from .disease_packs import load_packs


def main() -> int:
    try:
        packs = load_packs(force=True)
    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1
    for pack_id, pack in packs.items():
        print(
            f"OK  {pack_id:14s} v{pack['version']:<7s} {pack['status']:<9s} "
            f"{len(pack['cell_types'])} cell types, {len(pack['zones'])} zones, "
            f"{len(pack['targets'])} targets"
        )
    print(f"\n{len(packs)} packs validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
