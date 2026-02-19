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
        --shopify-black: #212326;
        --ink: #1c1f31;
        --muted: #5c6a79;
        --line: #d2d5d9;
        --panel: #f6f6f7;
        --page-padding: 12mm;
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
        font-family: Arial, Helvetica, sans-serif;
        color: var(--ink);
        background: #ffffff;
        print-color-adjust: exact;
        -webkit-print-color-adjust: exact;
      }}

      .page {{
        width: 210mm;
        height: 297mm;
        padding: var(--page-padding);
        display: grid;
        grid-template-rows: auto auto 1fr auto;
        gap: 3mm;
      }}

      .top-accent {{
        height: 2.5mm;
        background: linear-gradient(90deg, var(--shopify-green), #78a22f);
        border-radius: 999px;
      }}

      .hero {{
        border: 1px solid var(--line);
        border-radius: 3mm;
        background: var(--panel);
        padding: 3.5mm 4mm;
        display: grid;
        grid-template-columns: 1fr;
        gap: 2.5mm;
      }}

      .brand-row {{
        display: flex;
        align-items: center;
        gap: 2.5mm;
      }}

      .partner-logo {{
        max-height: 9mm;
        max-width: 68mm;
        width: auto;
      }}

      .shopify-logo {{
        max-height: 8mm;
        width: auto;
      }}

      .brand-divider {{
        color: var(--muted);
        font-size: 4.4mm;
        font-weight: 700;
      }}

      h1 {{
        margin: 0;
        font-size: 6.5mm;
        line-height: 1.1;
        color: var(--shopify-black);
      }}

      .subtitle {{
        margin: 1mm 0 0;
        font-size: 3.3mm;
        color: var(--muted);
      }}

      .meta-grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 2mm;
      }}

      .meta-card {{
        background: #ffffff;
        border: 1px solid var(--line);
        border-radius: 2.2mm;
        padding: 2.2mm;
      }}

      .meta-label {{
        font-size: 2.55mm;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--muted);
      }}

      .meta-value {{
        margin-top: 0.6mm;
        font-size: 3.1mm;
        line-height: 1.25;
        font-weight: 700;
      }}

      .content-grid {{
        display: grid;
        grid-template-columns: 1.1fr 0.9fr;
        gap: 3mm;
        min-height: 0;
      }}

      .column {{
        display: flex;
        flex-direction: column;
        gap: 3mm;
        min-height: 0;
      }}

      .section {{
        border: 1px solid var(--line);
        border-radius: 2.6mm;
        padding: 3mm;
        background: #ffffff;
      }}

      .section h2 {{
        margin: 0;
        font-size: 4mm;
        line-height: 1.2;
        color: var(--shopify-black);
      }}

      .section-note {{
        margin: 0.8mm 0 0;
        font-size: 2.7mm;
        color: var(--muted);
      }}

      ul {{
        margin: 2.2mm 0 0 4.2mm;
        padding: 0;
      }}

      li {{
        margin: 0 0 1.4mm;
        font-size: 3mm;
        line-height: 1.28;
      }}

      .icp-table {{
        margin-top: 2.2mm;
        border: 1px solid var(--line);
        border-radius: 2mm;
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
        background: var(--panel);
        padding: 2mm 2.2mm;
        font-size: 2.75mm;
        font-weight: 700;
      }}

      .icp-value {{
        padding: 2mm 2.2mm;
        font-size: 2.75mm;
        line-height: 1.35;
      }}

      .story-list {{
        display: grid;
        gap: 2mm;
        margin-top: 2.2mm;
      }}

      .story-card {{
        border: 1px solid var(--line);
        border-left: 1.4mm solid var(--shopify-green);
        border-radius: 2mm;
        padding: 2mm 2.2mm;
        background: #ffffff;
      }}

      .story-heading h3 {{
        margin: 0;
        font-size: 3.1mm;
        color: var(--shopify-black);
      }}

      .story-meta {{
        margin: 0.8mm 0 0;
        font-size: 2.55mm;
        color: var(--muted);
        line-height: 1.25;
      }}

      .story-summary {{
        margin: 1.4mm 0 0;
        font-size: 2.75mm;
        line-height: 1.3;
      }}

      .metric-chip-row {{
        margin-top: 1.4mm;
        display: flex;
        flex-wrap: wrap;
        gap: 1mm;
      }}

      .metric-chip {{
        display: inline-flex;
        align-items: center;
        background: #eef6dd;
        color: #466b17;
        border-radius: 999px;
        padding: 0.65mm 1.5mm;
        font-size: 2.45mm;
        font-weight: 700;
      }}

      .footer {{
        border: 1px solid var(--line);
        border-radius: 2.6mm;
        padding: 3mm;
        background: #ffffff;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 3mm;
      }}

      .footer h2 {{
        margin: 0;
        font-size: 3.8mm;
        color: var(--shopify-black);
      }}

      .contacts {{
        margin-top: 1.4mm;
        display: grid;
        gap: 1mm;
      }}

      .contact-row {{
        display: grid;
        grid-template-columns: 18mm 1fr;
        gap: 1.4mm;
        font-size: 2.9mm;
      }}

      .contact-label {{
        font-weight: 700;
        color: var(--shopify-black);
      }}

      .contact-value {{
        color: var(--ink);
      }}

      .cta {{
        margin-top: 1.6mm;
        background: #eef6dd;
        border-left: 1.4mm solid var(--shopify-green);
        border-radius: 2mm;
        padding: 1.8mm 2mm;
        font-size: 2.95mm;
        font-weight: 700;
        line-height: 1.3;
      }}
    </style>
  </head>
  <body>
    <main class="page">
      <div class="top-accent"></div>

      <section class="hero">
        <div class="brand-row">
          <img class="partner-logo" src="{partner_logo}" alt="Partner logo" />
          <span class="brand-divider">×</span>
          <img class="shopify-logo" src="{shopify_logo}" alt="Shopify logo" />
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
          <article class="section">
            <h2>Strengths</h2>
            <p class="section-note">What makes your team a trusted Shopify execution partner.</p>
            <ul>{strengths}</ul>
          </article>

          <article class="section">
            <h2>Capabilities</h2>
            <p class="section-note">The implementation workstreams you deliver repeatedly.</p>
            <ul>{capabilities}</ul>
          </article>

          <article class="section">
            <h2>Ideal Customer Profile</h2>
            <p class="section-note">Who should engage you first and why.</p>
            <div class="icp-table">{icp}</div>
          </article>
        </div>

        <div class="column">
          <article class="section">
            <h2>Success Stories</h2>
            <p class="section-note">Use concise proof points with business outcomes.</p>
            <div class="story-list">{success_stories}</div>
          </article>

          <article class="section">
            <h2>Delivery Parameters</h2>
            <ul>
              <li><strong>Typical budget:</strong> {_escaped(data.get("target_budget_range"))}</li>
              <li><strong>Implementation timeline:</strong> {_escaped(data.get("delivery_timeline"))}</li>
            </ul>
          </article>
        </div>
      </section>

      <section class="footer">
        <div>
          <h2>How to Engage</h2>
          <ul>{engagement_model}</ul>
          <div class="cta">{_escaped(data.get("cta"))}</div>
        </div>
        <div>
          <h2>Contact</h2>
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
