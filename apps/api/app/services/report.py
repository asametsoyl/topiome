from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"
_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES)),
    autoescape=select_autoescape(["html", "xml"]),
)


def _spot_svg(spots: list[dict], domains: list[dict], width: int = 840, height: int = 520) -> str:
    if not spots:
        return '<div style="padding:40px;color:#8a938c">No spots to display.</div>'
    xs = [float(s["x"]) for s in spots]
    ys = [float(s["y"]) for s in spots]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max(max_x - min_x, 1e-6)
    span_y = max(max_y - min_y, 1e-6)
    pad = 26
    scale = min((width - 2 * pad) / span_x, (height - 2 * pad) / span_y)
    offset_x = (width - span_x * scale) / 2
    offset_y = (height - span_y * scale) / 2

    colors = {d["id"]: d.get("color", "#8A938C") for d in domains}
    radius = max(1.8, min(4.5, 1600 / max(len(spots) ** 0.5, 1)))

    parts = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" role="img" '
        f'aria-label="Spatial domain map" xmlns="http://www.w3.org/2000/svg">',
        f'<rect width="{width}" height="{height}" fill="#090f0b"/>',
    ]
    for domain_id in colors:
        parts.append(f'<g fill="{escape(colors[domain_id])}" fill-opacity="0.92">')
        for spot in spots:
            if spot["domain"] != domain_id:
                continue
            x = offset_x + (float(spot["x"]) - min_x) * scale
            y = height - (offset_y + (float(spot["y"]) - min_y) * scale)
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.2f}"/>')
        parts.append("</g>")
    parts.append("</svg>")
    return "".join(parts)


def _composition_rows(payload: dict[str, Any], pack: dict[str, Any]) -> list[dict]:
    summary = payload.get("summary", {})
    means = summary.get("composition_mean", {})
    meta = {ct["id"]: ct for ct in pack.get("cell_types", [])}
    rows = [
        {
            "id": key,
            "name": meta.get(key, {}).get("name", key),
            "color": meta.get(key, {}).get("color", "#5FE0C0"),
            "value": float(value),
        }
        for key, value in means.items()
    ]
    rows.sort(key=lambda row: row["value"], reverse=True)
    return rows


def _target_rows(payload: dict[str, Any], pack: dict[str, Any]) -> list[dict]:
    zone_names = {zone["id"]: zone["name"] for zone in pack.get("zones", [])}
    rows = []
    for target in payload.get("target_scores", []):
        by_domain = target.get("by_domain", {})
        top_domain = max(by_domain.items(), key=lambda kv: kv[1])[0] if by_domain else "—"
        rows.append(
            {
                **target,
                "top_domain": zone_names.get(top_domain, top_domain),
            }
        )
    return rows


def _communication_rows(payload: dict[str, Any], pack: dict[str, Any]) -> list[dict]:
    cell_names = {ct["id"]: ct["name"] for ct in pack.get("cell_types", [])}
    zone_names = {zone["id"]: zone["name"] for zone in pack.get("zones", [])}
    rows = []
    for item in payload.get("communication", []):
        rows.append(
            {
                **item,
                "sender_name": cell_names.get(item.get("sender"), item.get("sender")),
                "receiver_name": cell_names.get(item.get("receiver"), item.get("receiver")),
                "top_domain_name": zone_names.get(item.get("top_domain"), item.get("top_domain")),
            }
        )
    return rows


def build_report(
    run,
    payload: dict[str, Any],
    pack: dict[str, Any],
    *,
    approval: dict[str, Any] | None = None,
) -> str:
    """Render the self-contained HTML report.

    ``approval`` is ``{"by", "at", "note"}`` once a person has signed off;
    without it the report renders as a visible draft.
    """
    summary = payload.get("summary", {})
    qc = payload.get("qc", {}).get("summary", {})
    domains = payload.get("domains_summary", [])
    warnings = list(dict.fromkeys(payload.get("warnings", []) + summary.get("warnings", [])))
    metrics = payload.get("metrics") or None
    html = _env.get_template("report.html").render(
        run=run,
        pack=pack,
        summary=summary,
        qc=qc,
        domains=domains,
        composition=_composition_rows(payload, pack),
        targets=_target_rows(payload, pack),
        warnings=warnings,
        metrics=metrics,
        map_svg=_spot_svg(payload.get("spots", []), domains),
        provenance=payload.get("provenance") or getattr(run, "provenance", None),
        communication=_communication_rows(payload, pack),
        concordance=(payload.get("validation") or {}).get("method_concordance"),
        atlas=(payload.get("validation") or {}).get("atlas_check"),
        not_assessed=summary.get("not_assessed") or pack.get("not_assessed", []),
        approval=(
            {
                **approval,
                "at": approval["at"].strftime("%Y-%m-%d %H:%M UTC")
                if isinstance(approval.get("at"), datetime)
                else approval.get("at"),
            }
            if approval
            else None
        ),
        generated_at=datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
        year=datetime.now(UTC).year,
    )
    return html
