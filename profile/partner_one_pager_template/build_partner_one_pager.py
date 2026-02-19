#!/usr/bin/env python3
"""Generate themed A4 Shopify partner one-pagers from JSON data."""

from __future__ import annotations

import argparse
import html
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


def _escaped(value: Any) -> str:
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def _is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https", "file"}


def _to_uri(raw_path: str, input_dir: Path, template_dir: Path) -> str:
    if _is_url(raw_path):
        return raw_path

    candidate_from_input = (input_dir / raw_path).resolve()
    if candidate_from_input.exists():
        return candidate_from_input.as_uri()

    candidate_from_template = (template_dir / raw_path).resolve()
    return candidate_from_template.as_uri()


def _list_items(items: list[str], class_name: str = "") -> str:
    safe_items = [_escaped(item) for item in items if str(item).strip()]
    class_attr = f' class="{class_name}"' if class_name else ""
    return "".join(f"<li{class_attr}>{item}</li>" for item in safe_items)


def _chip_items(items: list[str], class_name: str = "") -> str:
    safe_items = [_escaped(item) for item in items if str(item).strip()]
    class_attr = f' class="{class_name}"' if class_name else ""
    return "".join(f"<span{class_attr}>{item}</span>" for item in safe_items)


def _success_story_card(story: dict[str, Any]) -> str:
    results = story.get("results", [])
    metrics = "".join(
        f'<span class="metric-chip">{_escaped(metric)}</span>'
        for metric in results
        if str(metric).strip()
    )

    return f"""
      <article class="story-card">
        <div class="story-heading">
          <h3>{_escaped(story.get("client", "Client"))}</h3>
          <p class="story-meta">{_escaped(story.get("industry", "Industry"))} • Migrated from {_escaped(story.get("migration_from", "Legacy platform"))}</p>
        </div>
        <p class="story-summary">{_escaped(story.get("summary", ""))}</p>
        <div class="metric-chip-row">{metrics}</div>
      </article>
    """


def _icp_rows(rows: list[dict[str, Any]]) -> str:
    rendered_rows = []
    for row in rows:
        rendered_rows.append(
            f"""
            <div class="icp-row">
              <div class="icp-label">{_escaped(row.get("label", ""))}</div>
              <div class="icp-value">{_escaped(row.get("value", ""))}</div>
            </div>
            """
        )
    return "".join(rendered_rows)


def _normalized_theme(theme: str) -> str:
    normalized = (theme or "aurora").strip().lower()
    return normalized if normalized in {"aurora", "slate", "graphite"} else "aurora"


def render_html(
    data: dict[str, Any],
    input_dir: Path,
    template_dir: Path,
    theme: str = "aurora",
) -> str:
    theme_key = _normalized_theme(theme)
    theme_label = {
        "aurora": "Aurora",
        "slate": "Slate",
        "graphite": "Graphite",
    }[theme_key]

    partner_logo = _to_uri(
        data.get("partner_logo_path", "assets/partner-logo-placeholder.svg"),
        input_dir=input_dir,
        template_dir=template_dir,
    )
    shopify_logo = _to_uri(
        data.get("shopify_logo_path", "assets/shopify-logo-full-color.svg"),
        input_dir=input_dir,
        template_dir=template_dir,
    )

    strengths = _list_items(data.get("strengths", []))
    capabilities = _list_items(data.get("capabilities", []))
    engagement_model = _list_items(data.get("engagement_model", []))
    technology_partners = _chip_items(
        data.get("other_technology_partners", []),
        "tech-chip",
    )
    if not technology_partners:
        technology_partners = '<span class="tech-chip">Add technology partners</span>'
    success_stories = "".join(
        _success_story_card(story) for story in data.get("success_stories", [])[:3]
    )
    icp = _icp_rows(data.get("ideal_customer_profile", []))
    contact = data.get("contact", {})

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{_escaped(data.get("partner_name", "Partner"))} x Shopify - One Pager</title>
    <style>
      :root {{
        --page-padding: 10mm;
      }}

      body.theme-aurora {{
        --body-bg: #101528;
        --page-bg: radial-gradient(circle at 14% 8%, rgba(103, 84, 255, 0.27), transparent 32%),
          radial-gradient(circle at 88% 6%, rgba(41, 201, 255, 0.2), transparent 29%),
          radial-gradient(circle at 86% 96%, rgba(234, 78, 242, 0.16), transparent 32%),
          linear-gradient(168deg, #101528 0%, #131a30 48%, #11162a 100%);
        --text-strong: #f5f8ff;
        --text-muted: #b8c2e3;
        --line: rgba(168, 177, 235, 0.38);
        --hero-bg: linear-gradient(150deg, rgba(32, 43, 76, 0.92) 0%, rgba(23, 30, 54, 0.94) 68%, rgba(21, 28, 49, 0.96) 100%);
        --top-accent: linear-gradient(90deg, #95bf47 0%, #70d50e 22%, #33ede2 44%, #29c9ff 66%, #6754ff 84%, #ea4ef2 100%);
        --logo-shell-bg: rgba(255, 255, 255, 0.96);
        --logo-shell-border: rgba(210, 213, 217, 0.85);
        --badge-bg: rgba(103, 84, 255, 0.2);
        --badge-border: rgba(103, 84, 255, 0.48);
        --badge-text: #ddd8ff;
        --eyebrow: #a8b1eb;
        --title: #ffffff;
        --subtitle: #b8c2e3;
        --meta-bg: rgba(28, 37, 68, 0.86);
        --meta-label: #a8b1eb;
        --meta-value: #ffffff;
        --meta-accent-1: linear-gradient(90deg, #95bf47, #70d50e);
        --meta-accent-2: linear-gradient(90deg, #29c9ff, #33ede2);
        --meta-accent-3: linear-gradient(90deg, #6754ff, #423eff);
        --meta-accent-4: linear-gradient(90deg, #ea4ef2, #ff7bc4);
        --section-base-bg: rgba(28, 37, 68, 0.82);
        --section-strengths-bg: linear-gradient(155deg, rgba(112, 213, 14, 0.18) 0%, rgba(28, 37, 68, 0.9) 50%, rgba(28, 37, 68, 0.84) 100%);
        --section-capabilities-bg: linear-gradient(155deg, rgba(103, 84, 255, 0.18) 0%, rgba(28, 37, 68, 0.9) 52%, rgba(28, 37, 68, 0.84) 100%);
        --section-icp-bg: linear-gradient(155deg, rgba(51, 237, 226, 0.16) 0%, rgba(28, 37, 68, 0.9) 52%, rgba(28, 37, 68, 0.84) 100%);
        --section-stories-bg: linear-gradient(155deg, rgba(41, 201, 255, 0.18) 0%, rgba(28, 37, 68, 0.9) 46%, rgba(28, 37, 68, 0.84) 100%);
        --section-delivery-bg: linear-gradient(155deg, rgba(234, 78, 242, 0.16) 0%, rgba(28, 37, 68, 0.9) 54%, rgba(28, 37, 68, 0.84) 100%);
        --section-tech-bg: linear-gradient(155deg, rgba(41, 201, 255, 0.14) 0%, rgba(28, 37, 68, 0.9) 56%, rgba(28, 37, 68, 0.84) 100%);
        --heading: #ffffff;
        --section-note: #a8b1eb;
        --list-text: #e4e9ff;
        --bullet-bg: linear-gradient(135deg, #95bf47, #33ede2);
        --icon-strengths-bg: linear-gradient(135deg, #95bf47, #70d50e);
        --icon-capabilities-bg: linear-gradient(135deg, #423eff, #6754ff);
        --icon-icp-bg: linear-gradient(135deg, #1cd9d9, #33ede2);
        --icon-stories-bg: linear-gradient(135deg, #29c9ff, #00b4cd);
        --icon-delivery-bg: linear-gradient(135deg, #ea4ef2, #6754ff);
        --icon-tech-bg: linear-gradient(135deg, #29c9ff, #6754ff);
        --icon-engage-bg: linear-gradient(135deg, #95bf47, #33ede2);
        --icon-contact-bg: linear-gradient(135deg, #6754ff, #ea4ef2);
        --icon-stroke: #ffffff;
        --icp-label-bg: rgba(168, 177, 235, 0.14);
        --icp-label-text: #ebeeff;
        --icp-value-text: #dde3ff;
        --story-card-bg: rgba(20, 27, 49, 0.78);
        --story-border: rgba(168, 177, 235, 0.42);
        --story-left-1: #95bf47;
        --story-left-2: #29c9ff;
        --story-left-3: #ea4ef2;
        --story-meta: #a8b1eb;
        --story-summary: #dde3ff;
        --metric-chip-bg-1: rgba(112, 213, 14, 0.2);
        --metric-chip-border-1: rgba(112, 213, 14, 0.38);
        --metric-chip-text-1: #d5f8a6;
        --metric-chip-bg-2: rgba(41, 201, 255, 0.18);
        --metric-chip-border-2: rgba(41, 201, 255, 0.36);
        --metric-chip-text-2: #baf0ff;
        --metric-chip-bg-3: rgba(234, 78, 242, 0.18);
        --metric-chip-border-3: rgba(234, 78, 242, 0.36);
        --metric-chip-text-3: #ffd1fd;
        --tech-chip-bg: rgba(103, 84, 255, 0.2);
        --tech-chip-border: rgba(103, 84, 255, 0.45);
        --tech-chip-text: #ddd8ff;
        --footer-bg: rgba(28, 37, 68, 0.82);
        --contact-text: #dde3ff;
        --cta-bg: linear-gradient(130deg, rgba(149, 191, 71, 0.22) 0%, rgba(51, 237, 226, 0.18) 58%, rgba(41, 201, 255, 0.2) 100%);
        --cta-border: rgba(149, 191, 71, 0.45);
        --cta-text: #f3ffd5;
      }}

      body.theme-slate {{
        --body-bg: #cdd1d8;
        --page-bg: linear-gradient(164deg, #d9dbe0 0%, #cfd2d8 45%, #c3c7cf 100%);
        --text-strong: #171a20;
        --text-muted: #596272;
        --line: rgba(45, 52, 66, 0.2);
        --hero-bg: linear-gradient(145deg, rgba(255, 255, 255, 0.74) 0%, rgba(247, 249, 252, 0.76) 100%);
        --top-accent: linear-gradient(90deg, #95bf47 0%, #8591a3 48%, #495061 100%);
        --logo-shell-bg: rgba(255, 255, 255, 0.95);
        --logo-shell-border: rgba(62, 69, 82, 0.26);
        --badge-bg: rgba(57, 62, 73, 0.1);
        --badge-border: rgba(57, 62, 73, 0.24);
        --badge-text: #2e3440;
        --eyebrow: #5f6777;
        --title: #151821;
        --subtitle: #454e5f;
        --meta-bg: rgba(255, 255, 255, 0.66);
        --meta-label: #5f6777;
        --meta-value: #171a20;
        --meta-accent-1: linear-gradient(90deg, #343944, #545b68);
        --meta-accent-2: linear-gradient(90deg, #60697a, #7c8596);
        --meta-accent-3: linear-gradient(90deg, #95bf47, #6d9340);
        --meta-accent-4: linear-gradient(90deg, #4b5363, #333943);
        --section-base-bg: rgba(255, 255, 255, 0.62);
        --section-strengths-bg: linear-gradient(155deg, rgba(149, 191, 71, 0.16) 0%, rgba(255, 255, 255, 0.72) 48%, rgba(255, 255, 255, 0.62) 100%);
        --section-capabilities-bg: linear-gradient(155deg, rgba(104, 117, 140, 0.16) 0%, rgba(255, 255, 255, 0.72) 48%, rgba(255, 255, 255, 0.62) 100%);
        --section-icp-bg: linear-gradient(155deg, rgba(110, 124, 143, 0.14) 0%, rgba(255, 255, 255, 0.72) 50%, rgba(255, 255, 255, 0.62) 100%);
        --section-stories-bg: linear-gradient(155deg, rgba(137, 147, 166, 0.16) 0%, rgba(255, 255, 255, 0.72) 46%, rgba(255, 255, 255, 0.62) 100%);
        --section-delivery-bg: linear-gradient(155deg, rgba(113, 123, 138, 0.14) 0%, rgba(255, 255, 255, 0.72) 56%, rgba(255, 255, 255, 0.62) 100%);
        --section-tech-bg: linear-gradient(155deg, rgba(88, 96, 112, 0.14) 0%, rgba(255, 255, 255, 0.72) 56%, rgba(255, 255, 255, 0.62) 100%);
        --heading: #171a20;
        --section-note: #5d6678;
        --list-text: #232a38;
        --bullet-bg: linear-gradient(135deg, #95bf47, #6d9340);
        --icon-strengths-bg: linear-gradient(135deg, #95bf47, #6d9340);
        --icon-capabilities-bg: linear-gradient(135deg, #687085, #4b5262);
        --icon-icp-bg: linear-gradient(135deg, #7f8899, #626b7c);
        --icon-stories-bg: linear-gradient(135deg, #8b95a8, #6f7788);
        --icon-delivery-bg: linear-gradient(135deg, #666f82, #4a5261);
        --icon-tech-bg: linear-gradient(135deg, #7c8595, #5c6576);
        --icon-engage-bg: linear-gradient(135deg, #95bf47, #667280);
        --icon-contact-bg: linear-gradient(135deg, #6d7484, #4b5261);
        --icon-stroke: #ffffff;
        --icp-label-bg: rgba(50, 56, 70, 0.09);
        --icp-label-text: #222a39;
        --icp-value-text: #30384b;
        --story-card-bg: rgba(255, 255, 255, 0.74);
        --story-border: rgba(63, 70, 83, 0.22);
        --story-left-1: #95bf47;
        --story-left-2: #6d7484;
        --story-left-3: #404654;
        --story-meta: #5f6879;
        --story-summary: #31394a;
        --metric-chip-bg-1: rgba(149, 191, 71, 0.18);
        --metric-chip-border-1: rgba(109, 147, 64, 0.4);
        --metric-chip-text-1: #3a571e;
        --metric-chip-bg-2: rgba(109, 116, 132, 0.15);
        --metric-chip-border-2: rgba(109, 116, 132, 0.32);
        --metric-chip-text-2: #3d4454;
        --metric-chip-bg-3: rgba(72, 80, 96, 0.16);
        --metric-chip-border-3: rgba(72, 80, 96, 0.32);
        --metric-chip-text-3: #2f3542;
        --tech-chip-bg: rgba(62, 70, 84, 0.1);
        --tech-chip-border: rgba(62, 70, 84, 0.24);
        --tech-chip-text: #2f3748;
        --footer-bg: rgba(255, 255, 255, 0.64);
        --contact-text: #2f3748;
        --cta-bg: linear-gradient(130deg, rgba(149, 191, 71, 0.2) 0%, rgba(255, 255, 255, 0.66) 100%);
        --cta-border: rgba(109, 147, 64, 0.42);
        --cta-text: #2f4a15;
      }}

      body.theme-graphite {{
        --body-bg: #151922;
        --page-bg: radial-gradient(circle at 85% 10%, rgba(130, 145, 170, 0.14), transparent 34%),
          linear-gradient(168deg, #151922 0%, #171d29 52%, #141925 100%);
        --text-strong: #f1f4fb;
        --text-muted: #b6bfd1;
        --line: rgba(178, 186, 200, 0.34);
        --hero-bg: linear-gradient(150deg, rgba(36, 44, 59, 0.92) 0%, rgba(28, 35, 49, 0.94) 100%);
        --top-accent: linear-gradient(90deg, #95bf47 0%, #78a63a 26%, #7a889f 66%, #9faac0 100%);
        --logo-shell-bg: rgba(250, 252, 255, 0.96);
        --logo-shell-border: rgba(198, 205, 218, 0.88);
        --badge-bg: rgba(130, 145, 170, 0.2);
        --badge-border: rgba(130, 145, 170, 0.44);
        --badge-text: #e4eaf6;
        --eyebrow: #c2c9d8;
        --title: #ffffff;
        --subtitle: #c5ccdc;
        --meta-bg: rgba(34, 41, 55, 0.86);
        --meta-label: #b3bccd;
        --meta-value: #ffffff;
        --meta-accent-1: linear-gradient(90deg, #95bf47, #7ea93b);
        --meta-accent-2: linear-gradient(90deg, #6e7f9c, #8b9dbc);
        --meta-accent-3: linear-gradient(90deg, #5c6f8e, #7a8faf);
        --meta-accent-4: linear-gradient(90deg, #798395, #a0aabe);
        --section-base-bg: rgba(34, 41, 55, 0.82);
        --section-strengths-bg: linear-gradient(155deg, rgba(149, 191, 71, 0.18) 0%, rgba(34, 41, 55, 0.9) 50%, rgba(34, 41, 55, 0.84) 100%);
        --section-capabilities-bg: linear-gradient(155deg, rgba(95, 111, 142, 0.2) 0%, rgba(34, 41, 55, 0.9) 52%, rgba(34, 41, 55, 0.84) 100%);
        --section-icp-bg: linear-gradient(155deg, rgba(122, 143, 175, 0.16) 0%, rgba(34, 41, 55, 0.9) 52%, rgba(34, 41, 55, 0.84) 100%);
        --section-stories-bg: linear-gradient(155deg, rgba(112, 126, 152, 0.2) 0%, rgba(34, 41, 55, 0.9) 46%, rgba(34, 41, 55, 0.84) 100%);
        --section-delivery-bg: linear-gradient(155deg, rgba(120, 130, 148, 0.18) 0%, rgba(34, 41, 55, 0.9) 54%, rgba(34, 41, 55, 0.84) 100%);
        --section-tech-bg: linear-gradient(155deg, rgba(95, 109, 136, 0.18) 0%, rgba(34, 41, 55, 0.9) 56%, rgba(34, 41, 55, 0.84) 100%);
        --heading: #ffffff;
        --section-note: #b8c1d2;
        --list-text: #e6ebf7;
        --bullet-bg: linear-gradient(135deg, #95bf47, #a3b2cc);
        --icon-strengths-bg: linear-gradient(135deg, #95bf47, #7ea93b);
        --icon-capabilities-bg: linear-gradient(135deg, #5f6f8e, #8696b3);
        --icon-icp-bg: linear-gradient(135deg, #7b89a1, #a3afc5);
        --icon-stories-bg: linear-gradient(135deg, #6b7d9c, #8fa1bf);
        --icon-delivery-bg: linear-gradient(135deg, #7f8a9f, #a7b2c7);
        --icon-tech-bg: linear-gradient(135deg, #6b7d9c, #8ea1c0);
        --icon-engage-bg: linear-gradient(135deg, #95bf47, #8696b3);
        --icon-contact-bg: linear-gradient(135deg, #707c94, #95a4bd);
        --icon-stroke: #ffffff;
        --icp-label-bg: rgba(174, 186, 207, 0.16);
        --icp-label-text: #eff3fb;
        --icp-value-text: #e1e7f5;
        --story-card-bg: rgba(24, 31, 43, 0.78);
        --story-border: rgba(178, 186, 200, 0.4);
        --story-left-1: #95bf47;
        --story-left-2: #7f8fa8;
        --story-left-3: #b1bacb;
        --story-meta: #b8c1d2;
        --story-summary: #e1e7f5;
        --metric-chip-bg-1: rgba(149, 191, 71, 0.22);
        --metric-chip-border-1: rgba(149, 191, 71, 0.4);
        --metric-chip-text-1: #d7efab;
        --metric-chip-bg-2: rgba(124, 140, 166, 0.22);
        --metric-chip-border-2: rgba(124, 140, 166, 0.38);
        --metric-chip-text-2: #d8e0ef;
        --metric-chip-bg-3: rgba(159, 170, 190, 0.22);
        --metric-chip-border-3: rgba(159, 170, 190, 0.38);
        --metric-chip-text-3: #e6ebf6;
        --tech-chip-bg: rgba(123, 137, 161, 0.22);
        --tech-chip-border: rgba(123, 137, 161, 0.4);
        --tech-chip-text: #e0e7f4;
        --footer-bg: rgba(34, 41, 55, 0.84);
        --contact-text: #dfe6f4;
        --cta-bg: linear-gradient(130deg, rgba(149, 191, 71, 0.24) 0%, rgba(134, 150, 179, 0.2) 100%);
        --cta-border: rgba(149, 191, 71, 0.44);
        --cta-text: #f0ffd4;
      }}

      * {{
        box-sizing: border-box;
      }}

      @page {{
        size: A4;
        margin: 0;
      }}

      html,
      body {{
        margin: 0;
        width: 210mm;
        height: 297mm;
        font-family: Inter, "Segoe UI", Arial, Helvetica, sans-serif;
        color: var(--text-strong);
        background: var(--body-bg);
        print-color-adjust: exact;
        -webkit-print-color-adjust: exact;
      }}

      .page {{
        width: 210mm;
        height: 297mm;
        padding: var(--page-padding);
        display: grid;
        grid-template-rows: auto auto 1fr auto;
        gap: 2.4mm;
        background: var(--page-bg);
      }}

      .top-accent {{
        height: 2.1mm;
        background: var(--top-accent);
        border-radius: 999px;
      }}

      .hero {{
        border: 1px solid var(--line);
        border-radius: 3.2mm;
        background: var(--hero-bg);
        padding: 3.1mm 3.6mm;
        display: grid;
        gap: 2.4mm;
      }}

      .hero-top-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 2.4mm;
      }}

      .eyebrow {{
        margin: 0;
        color: var(--eyebrow);
        font-size: 2.35mm;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }}

      .doc-badge {{
        display: inline-flex;
        align-items: center;
        background: var(--badge-bg);
        color: var(--badge-text);
        border: 1px solid var(--badge-border);
        border-radius: 999px;
        padding: 0.9mm 2.2mm;
        font-size: 2.5mm;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        white-space: nowrap;
      }}

      .logo-lockup {{
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto minmax(36mm, 44mm);
        align-items: center;
        gap: 1.5mm;
      }}

      .brand-divider {{
        color: var(--text-muted);
        font-size: 4.1mm;
        font-weight: 700;
      }}

      .logo-shell {{
        background: var(--logo-shell-bg);
        border: 1px solid var(--logo-shell-border);
        border-radius: 1.75mm;
        display: inline-flex;
        align-items: center;
        justify-content: center;
      }}

      .logo-shell.partner-shell {{
        min-height: 13mm;
        padding: 1.6mm 2.2mm;
      }}

      .logo-shell.shopify-shell {{
        min-height: 13mm;
        padding: 1.6mm 2mm;
      }}

      .partner-logo {{
        max-height: 9.1mm;
        max-width: 100%;
        width: 100%;
        object-fit: contain;
        object-position: center;
      }}

      .shopify-logo {{
        max-height: 8.3mm;
        max-width: 100%;
        width: 100%;
        object-fit: contain;
      }}

      h1 {{
        margin: 1.5mm 0 0;
        font-size: 6.4mm;
        line-height: 1.03;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: var(--title);
      }}

      .subtitle {{
        margin: 1.2mm 0 0;
        font-size: 3.02mm;
        line-height: 1.3;
        color: var(--subtitle);
      }}

      .meta-grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 1.9mm;
      }}

      .meta-card {{
        position: relative;
        overflow: hidden;
        border-radius: 2.3mm;
        border: 1px solid var(--line);
        background: var(--meta-bg);
        padding: 2.2mm 2.2mm 2.1mm;
      }}

      .meta-card::before {{
        content: "";
        position: absolute;
        inset: 0 0 auto;
        height: 0.95mm;
        background: var(--meta-accent-1);
      }}

      .meta-card:nth-child(2)::before {{
        background: var(--meta-accent-2);
      }}

      .meta-card:nth-child(3)::before {{
        background: var(--meta-accent-3);
      }}

      .meta-card:nth-child(4)::before {{
        background: var(--meta-accent-4);
      }}

      .meta-label {{
        margin-top: 0.6mm;
        font-size: 2.35mm;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        color: var(--meta-label);
        font-weight: 700;
      }}

      .meta-value {{
        margin-top: 0.8mm;
        font-size: 3.06mm;
        line-height: 1.2;
        font-weight: 700;
        color: var(--meta-value);
      }}

      .content-grid {{
        display: grid;
        grid-template-columns: 1.08fr 0.92fr;
        gap: 2.4mm;
        min-height: 0;
      }}

      .column {{
        display: flex;
        flex-direction: column;
        gap: 2.4mm;
        min-height: 0;
      }}

      .section {{
        border: 1px solid var(--line);
        border-radius: 2.5mm;
        padding: 2.65mm;
        background: var(--section-base-bg);
      }}

      .section.strengths {{
        background: var(--section-strengths-bg);
      }}

      .section.capabilities {{
        background: var(--section-capabilities-bg);
      }}

      .section.icp {{
        background: var(--section-icp-bg);
      }}

      .section.stories {{
        background: var(--section-stories-bg);
      }}

      .section.delivery {{
        background: var(--section-delivery-bg);
      }}

      .section.tech {{
        background: var(--section-tech-bg);
      }}

      .section-header {{
        display: flex;
        align-items: center;
        gap: 1.8mm;
      }}

      .icon-wrap {{
        width: 5.2mm;
        height: 5.2mm;
        border-radius: 1.45mm;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
      }}

      .icon-wrap svg {{
        width: 3.05mm;
        height: 3.05mm;
        fill: none;
        stroke: var(--icon-stroke);
        stroke-width: 1.85;
        stroke-linecap: round;
        stroke-linejoin: round;
      }}

      .icon-strengths {{
        background: var(--icon-strengths-bg);
      }}

      .icon-capabilities {{
        background: var(--icon-capabilities-bg);
      }}

      .icon-icp {{
        background: var(--icon-icp-bg);
      }}

      .icon-stories {{
        background: var(--icon-stories-bg);
      }}

      .icon-delivery {{
        background: var(--icon-delivery-bg);
      }}

      .icon-tech {{
        background: var(--icon-tech-bg);
      }}

      .icon-engage {{
        background: var(--icon-engage-bg);
      }}

      .icon-contact {{
        background: var(--icon-contact-bg);
      }}

      .section h2 {{
        margin: 0;
        font-size: 3.85mm;
        line-height: 1.2;
        color: var(--heading);
        letter-spacing: -0.01em;
      }}

      .section-note {{
        margin: 1.1mm 0 0;
        font-size: 2.45mm;
        line-height: 1.35;
        color: var(--section-note);
      }}

      ul {{
        margin: 1.8mm 0 0;
        padding: 0;
        list-style: none;
        display: grid;
        gap: 1mm;
      }}

      li {{
        position: relative;
        margin: 0;
        padding-left: 3.1mm;
        font-size: 2.72mm;
        line-height: 1.3;
        color: var(--list-text);
      }}

      li::before {{
        content: "";
        position: absolute;
        left: 0;
        top: 1.1mm;
        width: 1.35mm;
        height: 1.35mm;
        border-radius: 999px;
        background: var(--bullet-bg);
      }}

      .split-row {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2.4mm;
      }}

      .section.compact {{
        padding: 2.45mm;
      }}

      .section.compact .section-note {{
        margin-top: 0.9mm;
      }}

      .section.compact ul {{
        margin-top: 1.4mm;
        gap: 0.8mm;
      }}

      .section.compact li {{
        font-size: 2.52mm;
      }}

      .section.compact li::before {{
        width: 1.22mm;
        height: 1.22mm;
        top: 1.02mm;
      }}

      .icp-table {{
        margin-top: 1.8mm;
        border: 1px solid var(--line);
        border-radius: 1.8mm;
        overflow: hidden;
      }}

      .icp-row {{
        display: grid;
        grid-template-columns: 34% 66%;
        border-bottom: 1px solid var(--line);
      }}

      .icp-row:last-child {{
        border-bottom: 0;
      }}

      .icp-label {{
        background: var(--icp-label-bg);
        padding: 1.7mm 1.9mm;
        font-size: 2.5mm;
        line-height: 1.25;
        font-weight: 700;
        color: var(--icp-label-text);
      }}

      .icp-value {{
        padding: 1.7mm 1.9mm;
        font-size: 2.46mm;
        line-height: 1.3;
        color: var(--icp-value-text);
      }}

      .story-list {{
        display: grid;
        gap: 1.65mm;
        margin-top: 1.8mm;
      }}

      .story-card {{
        border: 1px solid var(--story-border);
        border-left: 1.2mm solid var(--story-left-1);
        border-radius: 1.8mm;
        padding: 1.75mm 1.95mm;
        background: var(--story-card-bg);
      }}

      .story-card:nth-child(2) {{
        border-left-color: var(--story-left-2);
      }}

      .story-card:nth-child(3) {{
        border-left-color: var(--story-left-3);
      }}

      .story-heading h3 {{
        margin: 0;
        font-size: 2.9mm;
        color: var(--heading);
        line-height: 1.2;
      }}

      .story-meta {{
        margin: 0.65mm 0 0;
        font-size: 2.35mm;
        color: var(--story-meta);
        line-height: 1.25;
      }}

      .story-summary {{
        margin: 1mm 0 0;
        font-size: 2.45mm;
        line-height: 1.3;
        color: var(--story-summary);
      }}

      .metric-chip-row {{
        margin-top: 1.05mm;
        display: flex;
        flex-wrap: wrap;
        gap: 0.8mm;
      }}

      .metric-chip {{
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        padding: 0.55mm 1.3mm;
        font-size: 2.22mm;
        font-weight: 700;
        background: var(--metric-chip-bg-1);
        color: var(--metric-chip-text-1);
        border: 1px solid var(--metric-chip-border-1);
      }}

      .story-card:nth-child(2) .metric-chip {{
        background: var(--metric-chip-bg-2);
        border-color: var(--metric-chip-border-2);
        color: var(--metric-chip-text-2);
      }}

      .story-card:nth-child(3) .metric-chip {{
        background: var(--metric-chip-bg-3);
        border-color: var(--metric-chip-border-3);
        color: var(--metric-chip-text-3);
      }}

      .tech-chip-row {{
        margin-top: 1.5mm;
        display: flex;
        flex-wrap: wrap;
        gap: 0.8mm;
      }}

      .tech-chip {{
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        border: 1px solid var(--tech-chip-border);
        background: var(--tech-chip-bg);
        color: var(--tech-chip-text);
        padding: 0.7mm 1.5mm;
        font-size: 2.35mm;
        font-weight: 700;
        line-height: 1.2;
      }}

      .footer {{
        border: 1px solid var(--line);
        border-radius: 2.5mm;
        padding: 2.65mm;
        background: var(--footer-bg);
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2.4mm;
      }}

      .contacts {{
        margin-top: 1.45mm;
        display: grid;
        gap: 1mm;
      }}

      .contact-row {{
        display: grid;
        grid-template-columns: 15.5mm 1fr;
        gap: 1.2mm;
        font-size: 2.62mm;
        line-height: 1.26;
      }}

      .contact-label {{
        font-weight: 700;
        color: var(--heading);
      }}

      .contact-value {{
        color: var(--contact-text);
      }}

      .cta {{
        margin-top: 1.5mm;
        background: var(--cta-bg);
        border: 1px solid var(--cta-border);
        border-left: 1.2mm solid #95bf47;
        border-radius: 1.8mm;
        padding: 1.45mm 1.75mm;
        font-size: 2.6mm;
        font-weight: 700;
        line-height: 1.28;
        color: var(--cta-text);
      }}
    </style>
  </head>
  <body class="theme-{theme_key}">
    <main class="page">
      <div class="top-accent"></div>

      <section class="hero">
        <div class="hero-top-row">
          <p class="eyebrow">Shopify ecosystem one-pager</p>
          <span class="doc-badge">Partner profile · {theme_label}</span>
        </div>
        <div class="logo-lockup">
          <div class="logo-shell partner-shell">
            <img class="partner-logo" src="{partner_logo}" alt="Partner logo" />
          </div>
          <span class="brand-divider">×</span>
          <div class="logo-shell shopify-shell">
            <img class="shopify-logo" src="{shopify_logo}" alt="Shopify logo" />
          </div>
        </div>
        <div>
          <h1>{_escaped(data.get("partner_name"))}</h1>
          <p class="subtitle">{_escaped(data.get("partner_tagline"))}</p>
        </div>
      </section>

      <section class="meta-grid">
        <article class="meta-card">
          <div class="meta-label">Segment focus</div>
          <div class="meta-value">{_escaped(data.get("segment_focus"))}</div>
        </article>
        <article class="meta-card">
          <div class="meta-label">Region</div>
          <div class="meta-value">{_escaped(data.get("region"))}</div>
        </article>
        <article class="meta-card">
          <div class="meta-label">Shopify partner since</div>
          <div class="meta-value">{_escaped(data.get("shopify_partner_since"))}</div>
        </article>
        <article class="meta-card">
          <div class="meta-label">Team</div>
          <div class="meta-value">{_escaped(data.get("team_size"))}</div>
        </article>
      </section>

      <section class="content-grid">
        <div class="column">
          <article class="section strengths">
            <div class="section-header">
              <span class="icon-wrap icon-strengths">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="m12 3 2.8 5.7 6.2.9-4.5 4.3 1.1 6.1-5.6-3-5.6 3 1.1-6.1L3 9.6l6.2-.9L12 3z" />
                </svg>
              </span>
              <h2>Strengths</h2>
            </div>
            <p class="section-note">What makes your team a trusted Shopify execution partner.</p>
            <ul>{strengths}</ul>
          </article>

          <article class="section capabilities">
            <div class="section-header">
              <span class="icon-wrap icon-capabilities">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M13 2 4 14h6l-1 8 9-12h-6l1-8z" />
                </svg>
              </span>
              <h2>Capabilities</h2>
            </div>
            <p class="section-note">The implementation workstreams you deliver repeatedly.</p>
            <ul>{capabilities}</ul>
          </article>

          <article class="section icp">
            <div class="section-header">
              <span class="icon-wrap icon-icp">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <circle cx="12" cy="12" r="8" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
              </span>
              <h2>Ideal Customer Profile</h2>
            </div>
            <p class="section-note">Who should engage you first and why.</p>
            <div class="icp-table">{icp}</div>
          </article>
        </div>

        <div class="column">
          <article class="section stories">
            <div class="section-header">
              <span class="icon-wrap icon-stories">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M4 18V6M10 18v-7M16 18v-4M22 18v-9" />
                  <path d="m3 9 5-3 4 4 8-5" />
                </svg>
              </span>
              <h2>Success Stories</h2>
            </div>
            <p class="section-note">Use concise proof points with business outcomes.</p>
            <div class="story-list">{success_stories}</div>
          </article>

          <div class="split-row">
            <article class="section delivery compact">
              <div class="section-header">
                <span class="icon-wrap icon-delivery">
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <circle cx="12" cy="12" r="8" />
                    <path d="M12 7v5l3 2" />
                  </svg>
                </span>
                <h2>Delivery Parameters</h2>
              </div>
              <ul>
                <li><strong>Typical budget:</strong> {_escaped(data.get("target_budget_range"))}</li>
                <li><strong>Implementation timeline:</strong> {_escaped(data.get("delivery_timeline"))}</li>
              </ul>
            </article>

            <article class="section tech compact">
              <div class="section-header">
                <span class="icon-wrap icon-tech">
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M8 7V5a2 2 0 1 1 4 0v2h4a2 2 0 0 1 2 2v3h-2a2 2 0 1 0 0 4h2v3a2 2 0 0 1-2 2h-4v-2a2 2 0 1 0-4 0v2H4a2 2 0 0 1-2-2v-4h2a2 2 0 1 0 0-4H2V9a2 2 0 0 1 2-2h4z" />
                  </svg>
                </span>
                <h2>Other Tech Partners</h2>
              </div>
              <p class="section-note">Strategic tools your team integrates often.</p>
              <div class="tech-chip-row">{technology_partners}</div>
            </article>
          </div>
        </div>
      </section>

      <section class="footer">
        <div>
          <div class="section-header">
            <span class="icon-wrap icon-engage">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M3 12h7l2-3 3 6 2-3h4" />
              </svg>
            </span>
            <h2>How to Engage</h2>
          </div>
          <ul>{engagement_model}</ul>
          <div class="cta">{_escaped(data.get("cta"))}</div>
        </div>
        <div>
          <div class="section-header">
            <span class="icon-wrap icon-contact">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M4 6h16v12H4z" />
                <path d="m4 7 8 6 8-6" />
              </svg>
            </span>
            <h2>Contact</h2>
          </div>
          <div class="contacts">
            <div class="contact-row">
              <div class="contact-label">Slack</div>
              <div class="contact-value">{_escaped(contact.get("slack"))}</div>
            </div>
            <div class="contact-row">
              <div class="contact-label">Email</div>
              <div class="contact-value">{_escaped(contact.get("email"))}</div>
            </div>
            <div class="contact-row">
              <div class="contact-label">Website</div>
              <div class="contact-value">{_escaped(contact.get("website"))}</div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </body>
</html>
"""


def _build_pdf(html_path: Path, pdf_path: Path) -> None:
    # Prefer the stable binary directly to avoid local wrapper scripts that
    # force a shared user profile and can hang print-to-pdf commands.
    chrome_bin = shutil.which("google-chrome-stable") or shutil.which("google-chrome")
    if not chrome_bin:
        raise RuntimeError(
            "Google Chrome was not found. Install Chrome or use --skip-pdf."
        )

    with tempfile.TemporaryDirectory(prefix="chrome-pdf-") as tmp_dir:
        user_data_dir = Path(tmp_dir) / "user-data"
        user_data_dir.mkdir(parents=True, exist_ok=True)

        command = [
            chrome_bin,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--allow-file-access-from-files",
            "--no-pdf-header-footer",
            f"--user-data-dir={user_data_dir}",
            f"--print-to-pdf={pdf_path}",
            html_path.as_uri(),
        ]
        try:
            result = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=120,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                "Chrome timed out while generating the PDF. "
                "Please simplify content or rerun."
            ) from exc

    if result.returncode != 0:
        raise RuntimeError(
            "Failed to generate PDF with Chrome.\n"
            f"Command: {' '.join(command)}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate an A4 Shopify partner one-pager from JSON data."
    )
    parser.add_argument(
        "--input",
        default="partner_profile.template.json",
        help="Path to JSON input profile.",
    )
    parser.add_argument(
        "--output-html",
        default="partner_one_pager_a4.html",
        help="Path for rendered HTML output.",
    )
    parser.add_argument(
        "--output-pdf",
        default="partner_one_pager_a4.pdf",
        help="Path for generated PDF output.",
    )
    parser.add_argument(
        "--theme",
        default="aurora",
        choices=["aurora", "slate", "graphite"],
        help="Design theme variant.",
    )
    parser.add_argument(
        "--skip-pdf",
        action="store_true",
        help="Render HTML only and skip PDF generation.",
    )
    args = parser.parse_args()

    template_dir = Path(__file__).resolve().parent
    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = (template_dir / input_path).resolve()

    output_html = Path(args.output_html)
    if not output_html.is_absolute():
        output_html = (template_dir / output_html).resolve()

    output_pdf = Path(args.output_pdf)
    if not output_pdf.is_absolute():
        output_pdf = (template_dir / output_pdf).resolve()

    data = json.loads(input_path.read_text(encoding="utf-8"))
    html_content = render_html(
        data,
        input_dir=input_path.parent,
        template_dir=template_dir,
        theme=args.theme,
    )

    output_html.parent.mkdir(parents=True, exist_ok=True)
    output_html.write_text(html_content, encoding="utf-8")

    if not args.skip_pdf:
        output_pdf.parent.mkdir(parents=True, exist_ok=True)
        _build_pdf(output_html, output_pdf)

    print(f"Theme: {args.theme}")
    print(f"Rendered HTML: {output_html}")
    if not args.skip_pdf:
        print(f"Generated PDF: {output_pdf}")


if __name__ == "__main__":
    main()
