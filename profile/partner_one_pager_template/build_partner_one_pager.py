#!/usr/bin/env python3
"""Generate an A4 Shopify partner one-pager from JSON data."""

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


def render_html(data: dict[str, Any], input_dir: Path, template_dir: Path) -> str:
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
        --shopify-green: #95bf47;
        --ink-0: #0f1424;
        --ink-1: #151b31;
        --ink-2: #1c2544;
        --ink-3: #28335c;
        --text-strong: #f5f8ff;
        --text-muted: #b8c2e3;
        --line: rgba(168, 177, 235, 0.38);
        --violet: #6754ff;
        --cyan: #29c9ff;
        --teal: #33ede2;
        --pink: #ea4ef2;
        --green-bright: #70d50e;
        --page-padding: 10mm;
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
        background: var(--ink-0);
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
        background:
          radial-gradient(circle at 14% 8%, rgba(103, 84, 255, 0.27), transparent 32%),
          radial-gradient(circle at 88% 6%, rgba(41, 201, 255, 0.2), transparent 29%),
          radial-gradient(circle at 86% 96%, rgba(234, 78, 242, 0.16), transparent 32%),
          linear-gradient(168deg, #101528 0%, #131a30 48%, #11162a 100%);
      }}

      .top-accent {{
        height: 2.1mm;
        background: linear-gradient(
          90deg,
          var(--shopify-green) 0%,
          var(--green-bright) 22%,
          var(--teal) 44%,
          var(--cyan) 66%,
          var(--violet) 84%,
          var(--pink) 100%
        );
        border-radius: 999px;
      }}

      .hero {{
        border: 1px solid var(--line);
        border-radius: 3.2mm;
        background: linear-gradient(
          150deg,
          rgba(32, 43, 76, 0.92) 0%,
          rgba(23, 30, 54, 0.94) 68%,
          rgba(21, 28, 49, 0.96) 100%
        );
        padding: 3.1mm 3.6mm;
        display: grid;
        gap: 2.4mm;
      }}

      .hero-top-row {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 2.4mm;
      }}

      .brand-row {{
        display: flex;
        align-items: center;
        gap: 1.5mm;
      }}

      .logo-pill {{
        background: rgba(255, 255, 255, 0.95);
        border-radius: 1.7mm;
        padding: 1.2mm 1.8mm;
        border: 1px solid rgba(210, 213, 217, 0.8);
        display: inline-flex;
        align-items: center;
      }}

      .logo-pill.shopify-pill {{
        padding: 1.3mm 1.9mm;
      }}

      .partner-logo {{
        max-height: 7.6mm;
        max-width: 55mm;
        width: auto;
      }}

      .shopify-logo {{
        max-height: 6.8mm;
        width: auto;
      }}

      .brand-divider {{
        color: var(--text-muted);
        font-size: 4.1mm;
        font-weight: 700;
      }}

      .doc-badge {{
        display: inline-flex;
        align-items: center;
        background: rgba(103, 84, 255, 0.18);
        color: #d9d4ff;
        border: 1px solid rgba(103, 84, 255, 0.45);
        border-radius: 999px;
        padding: 0.9mm 2.2mm;
        font-size: 2.5mm;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        white-space: nowrap;
      }}

      .eyebrow {{
        margin: 0;
        color: #a8b1eb;
        font-size: 2.35mm;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }}

      h1 {{
        margin: 1.1mm 0 0;
        font-size: 6.4mm;
        line-height: 1.03;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #ffffff;
      }}

      .subtitle {{
        margin: 1.2mm 0 0;
        font-size: 3.02mm;
        line-height: 1.3;
        color: var(--text-muted);
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
        background: rgba(28, 37, 68, 0.85);
        padding: 2.2mm 2.2mm 2.1mm;
      }}

      .meta-card::before {{
        content: "";
        position: absolute;
        inset: 0 0 auto;
        height: 0.95mm;
        background: linear-gradient(90deg, var(--shopify-green), var(--green-bright));
      }}

      .meta-card:nth-child(2)::before {{
        background: linear-gradient(90deg, var(--cyan), var(--teal));
      }}

      .meta-card:nth-child(3)::before {{
        background: linear-gradient(90deg, var(--violet), #423eff);
      }}

      .meta-card:nth-child(4)::before {{
        background: linear-gradient(90deg, var(--pink), #ff7bc4);
      }}

      .meta-label {{
        margin-top: 0.6mm;
        font-size: 2.35mm;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        color: #a8b1eb;
        font-weight: 700;
      }}

      .meta-value {{
        margin-top: 0.8mm;
        font-size: 3.06mm;
        line-height: 1.2;
        font-weight: 700;
        color: #ffffff;
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
        background: rgba(28, 37, 68, 0.82);
      }}

      .section.strengths {{
        background: linear-gradient(
            155deg,
            rgba(112, 213, 14, 0.18) 0%,
            rgba(28, 37, 68, 0.9) 48%,
            rgba(28, 37, 68, 0.84) 100%
          );
      }}

      .section.capabilities {{
        background: linear-gradient(
            155deg,
            rgba(103, 84, 255, 0.18) 0%,
            rgba(28, 37, 68, 0.9) 52%,
            rgba(28, 37, 68, 0.84) 100%
          );
      }}

      .section.icp {{
        background: linear-gradient(
            155deg,
            rgba(51, 237, 226, 0.16) 0%,
            rgba(28, 37, 68, 0.9) 52%,
            rgba(28, 37, 68, 0.84) 100%
          );
      }}

      .section.stories {{
        background: linear-gradient(
            155deg,
            rgba(41, 201, 255, 0.18) 0%,
            rgba(28, 37, 68, 0.9) 44%,
            rgba(28, 37, 68, 0.84) 100%
          );
      }}

      .section.delivery {{
        background: linear-gradient(
            155deg,
            rgba(234, 78, 242, 0.16) 0%,
            rgba(28, 37, 68, 0.9) 54%,
            rgba(28, 37, 68, 0.84) 100%
          );
      }}

      .section.tech {{
        background: linear-gradient(
            155deg,
            rgba(41, 201, 255, 0.14) 0%,
            rgba(28, 37, 68, 0.9) 54%,
            rgba(28, 37, 68, 0.84) 100%
          );
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
        stroke: #ffffff;
        stroke-width: 1.85;
        stroke-linecap: round;
        stroke-linejoin: round;
      }}

      .icon-strengths {{
        background: linear-gradient(135deg, var(--shopify-green), var(--green-bright));
      }}

      .icon-capabilities {{
        background: linear-gradient(135deg, #423eff, var(--violet));
      }}

      .icon-icp {{
        background: linear-gradient(135deg, #1cd9d9, var(--teal));
      }}

      .icon-stories {{
        background: linear-gradient(135deg, var(--cyan), #00b4cd);
      }}

      .icon-delivery {{
        background: linear-gradient(135deg, var(--pink), #6754ff);
      }}

      .icon-tech {{
        background: linear-gradient(135deg, var(--cyan), var(--violet));
      }}

      .icon-engage {{
        background: linear-gradient(135deg, var(--shopify-green), #33ede2);
      }}

      .icon-contact {{
        background: linear-gradient(135deg, var(--violet), var(--pink));
      }}

      .section h2 {{
        margin: 0;
        font-size: 3.85mm;
        line-height: 1.2;
        color: #ffffff;
        letter-spacing: -0.01em;
      }}

      .section-note {{
        margin: 1.1mm 0 0;
        font-size: 2.45mm;
        line-height: 1.35;
        color: #a8b1eb;
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
        color: #e4e9ff;
      }}

      li::before {{
        content: "";
        position: absolute;
        left: 0;
        top: 1.1mm;
        width: 1.35mm;
        height: 1.35mm;
        border-radius: 999px;
        background: linear-gradient(135deg, var(--shopify-green), var(--teal));
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
        border: 1px solid rgba(168, 177, 235, 0.45);
        border-radius: 1.8mm;
        overflow: hidden;
      }}

      .icp-row {{
        display: grid;
        grid-template-columns: 34% 66%;
        border-bottom: 1px solid rgba(168, 177, 235, 0.28);
      }}

      .icp-row:last-child {{
        border-bottom: 0;
      }}

      .icp-label {{
        background: rgba(168, 177, 235, 0.14);
        padding: 1.7mm 1.9mm;
        font-size: 2.5mm;
        line-height: 1.25;
        font-weight: 700;
        color: #ebeeff;
      }}

      .icp-value {{
        padding: 1.7mm 1.9mm;
        font-size: 2.46mm;
        line-height: 1.3;
        color: #dde3ff;
      }}

      .story-list {{
        display: grid;
        gap: 1.65mm;
        margin-top: 1.8mm;
      }}

      .story-card {{
        border: 1px solid rgba(168, 177, 235, 0.42);
        border-left: 1.2mm solid var(--shopify-green);
        border-radius: 1.8mm;
        padding: 1.75mm 1.95mm;
        background: rgba(20, 27, 49, 0.78);
      }}

      .story-card:nth-child(2) {{
        border-left-color: var(--cyan);
      }}

      .story-card:nth-child(3) {{
        border-left-color: var(--pink);
      }}

      .story-heading h3 {{
        margin: 0;
        font-size: 2.9mm;
        color: #ffffff;
        line-height: 1.2;
      }}

      .story-meta {{
        margin: 0.65mm 0 0;
        font-size: 2.35mm;
        color: #a8b1eb;
        line-height: 1.25;
      }}

      .story-summary {{
        margin: 1mm 0 0;
        font-size: 2.45mm;
        line-height: 1.3;
        color: #dde3ff;
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
        background: rgba(112, 213, 14, 0.2);
        color: #d5f8a6;
        border: 1px solid rgba(112, 213, 14, 0.38);
      }}

      .story-card:nth-child(2) .metric-chip {{
        background: rgba(41, 201, 255, 0.18);
        border-color: rgba(41, 201, 255, 0.36);
        color: #baf0ff;
      }}

      .story-card:nth-child(3) .metric-chip {{
        background: rgba(234, 78, 242, 0.18);
        border-color: rgba(234, 78, 242, 0.36);
        color: #ffd1fd;
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
        border: 1px solid rgba(103, 84, 255, 0.45);
        background: rgba(103, 84, 255, 0.2);
        color: #ddd8ff;
        padding: 0.7mm 1.5mm;
        font-size: 2.35mm;
        font-weight: 700;
        line-height: 1.2;
      }}

      .footer {{
        border: 1px solid var(--line);
        border-radius: 2.5mm;
        padding: 2.65mm;
        background: rgba(28, 37, 68, 0.82);
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
        color: #ebeeff;
      }}

      .contact-value {{
        color: #dde3ff;
      }}

      .cta {{
        margin-top: 1.5mm;
        background: linear-gradient(
          130deg,
          rgba(149, 191, 71, 0.22) 0%,
          rgba(51, 237, 226, 0.18) 58%,
          rgba(41, 201, 255, 0.2) 100%
        );
        border: 1px solid rgba(149, 191, 71, 0.45);
        border-left: 1.2mm solid var(--shopify-green);
        border-radius: 1.8mm;
        padding: 1.45mm 1.75mm;
        font-size: 2.6mm;
        font-weight: 700;
        line-height: 1.28;
        color: #f3ffd5;
      }}
    </style>
  </head>
  <body>
    <main class="page">
      <div class="top-accent"></div>

      <section class="hero">
        <div class="hero-top-row">
          <div class="brand-row">
            <div class="logo-pill">
              <img class="partner-logo" src="{partner_logo}" alt="Partner logo" />
            </div>
            <span class="brand-divider">×</span>
            <div class="logo-pill shopify-pill">
              <img class="shopify-logo" src="{shopify_logo}" alt="Shopify logo" />
            </div>
          </div>
          <span class="doc-badge">Partner profile</span>
        </div>
        <div>
          <p class="eyebrow">Shopify ecosystem one-pager</p>
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
    html_content = render_html(data, input_dir=input_path.parent, template_dir=template_dir)

    output_html.parent.mkdir(parents=True, exist_ok=True)
    output_html.write_text(html_content, encoding="utf-8")

    if not args.skip_pdf:
        output_pdf.parent.mkdir(parents=True, exist_ok=True)
        _build_pdf(output_html, output_pdf)

    print(f"Rendered HTML: {output_html}")
    if not args.skip_pdf:
        print(f"Generated PDF: {output_pdf}")


if __name__ == "__main__":
    main()
