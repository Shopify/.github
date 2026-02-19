#!/usr/bin/env python3
"""Self-serve web portal for Shopify partner one-pager generation."""

from __future__ import annotations

import importlib.util
import io
import json
import os
import re
import tempfile
from pathlib import Path
from types import ModuleType
from typing import Any

from flask import Flask, render_template, request, send_file
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR.parent / "partner_one_pager_template"
GENERATOR_PATH = TEMPLATE_DIR / "build_partner_one_pager.py"

THEMES = ("graphite", "slate", "aurora")
ALLOWED_LOGO_EXTENSIONS = {".svg", ".png", ".jpg", ".jpeg", ".webp"}


def _load_generator_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("one_pager_generator", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load generator module from {GENERATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GENERATOR = _load_generator_module()


def _parse_lines(raw: str) -> list[str]:
    return [line.strip() for line in (raw or "").splitlines() if line.strip()]


def _parse_tag_list(raw: str) -> list[str]:
    parts = re.split(r"[\n,]+", raw or "")
    return [part.strip() for part in parts if part.strip()]


def _slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return normalized or "partner"


def _load_preset_profile(preset: str) -> dict[str, Any]:
    preset_file = (
        "partner_profile.eshop_guide.sample.json"
        if preset == "sample"
        else "partner_profile.template.json"
    )
    return json.loads((TEMPLATE_DIR / preset_file).read_text(encoding="utf-8"))


def _profile_to_form_data(profile: dict[str, Any], theme: str = "graphite") -> dict[str, Any]:
    icp_rows = profile.get("ideal_customer_profile", [])
    while len(icp_rows) < 4:
        icp_rows.append({"label": "", "value": ""})

    stories = profile.get("success_stories", [])
    while len(stories) < 3:
        stories.append(
            {
                "client": "",
                "industry": "",
                "migration_from": "",
                "summary": "",
                "results": [],
            }
        )

    return {
        "theme": theme if theme in THEMES else "graphite",
        "partner_name": profile.get("partner_name", ""),
        "partner_tagline": profile.get("partner_tagline", ""),
        "segment_focus": profile.get("segment_focus", ""),
        "region": profile.get("region", ""),
        "shopify_partner_since": profile.get("shopify_partner_since", ""),
        "team_size": profile.get("team_size", ""),
        "target_budget_range": profile.get("target_budget_range", ""),
        "delivery_timeline": profile.get("delivery_timeline", ""),
        "cta": profile.get("cta", ""),
        "contact_slack": profile.get("contact", {}).get("slack", ""),
        "contact_email": profile.get("contact", {}).get("email", ""),
        "contact_website": profile.get("contact", {}).get("website", ""),
        "strengths_text": "\n".join(profile.get("strengths", [])),
        "capabilities_text": "\n".join(profile.get("capabilities", [])),
        "engagement_model_text": "\n".join(profile.get("engagement_model", [])),
        "technology_partners_text": ", ".join(
            profile.get("other_technology_partners", [])
        ),
        "icp_rows": [
            {
                "label": icp_rows[index].get("label", ""),
                "value": icp_rows[index].get("value", ""),
            }
            for index in range(4)
        ],
        "success_stories": [
            {
                "client": stories[index].get("client", ""),
                "industry": stories[index].get("industry", ""),
                "migration_from": stories[index].get("migration_from", ""),
                "summary": stories[index].get("summary", ""),
                "results_text": "\n".join(stories[index].get("results", [])),
            }
            for index in range(3)
        ],
    }


def _extract_form_data(form: dict[str, str]) -> dict[str, Any]:
    form_data: dict[str, Any] = {
        "theme": form.get("theme", "graphite").strip().lower() or "graphite",
        "partner_name": form.get("partner_name", "").strip(),
        "partner_tagline": form.get("partner_tagline", "").strip(),
        "segment_focus": form.get("segment_focus", "").strip(),
        "region": form.get("region", "").strip(),
        "shopify_partner_since": form.get("shopify_partner_since", "").strip(),
        "team_size": form.get("team_size", "").strip(),
        "target_budget_range": form.get("target_budget_range", "").strip(),
        "delivery_timeline": form.get("delivery_timeline", "").strip(),
        "cta": form.get("cta", "").strip(),
        "contact_slack": form.get("contact_slack", "").strip(),
        "contact_email": form.get("contact_email", "").strip(),
        "contact_website": form.get("contact_website", "").strip(),
        "strengths_text": form.get("strengths_text", "").strip(),
        "capabilities_text": form.get("capabilities_text", "").strip(),
        "engagement_model_text": form.get("engagement_model_text", "").strip(),
        "technology_partners_text": form.get("technology_partners_text", "").strip(),
        "icp_rows": [],
        "success_stories": [],
    }

    for index in range(1, 5):
        form_data["icp_rows"].append(
            {
                "label": form.get(f"icp_label_{index}", "").strip(),
                "value": form.get(f"icp_value_{index}", "").strip(),
            }
        )

    for index in range(1, 4):
        form_data["success_stories"].append(
            {
                "client": form.get(f"story_{index}_client", "").strip(),
                "industry": form.get(f"story_{index}_industry", "").strip(),
                "migration_from": form.get(f"story_{index}_migration_from", "").strip(),
                "summary": form.get(f"story_{index}_summary", "").strip(),
                "results_text": form.get(f"story_{index}_results", "").strip(),
            }
        )

    if form_data["theme"] not in THEMES:
        form_data["theme"] = "graphite"

    return form_data


def _validate(form_data: dict[str, Any], logo: FileStorage | None) -> list[str]:
    errors: list[str] = []

    required = [
        ("partner_name", "Partner name"),
        ("partner_tagline", "Partner tagline"),
        ("segment_focus", "Segment focus"),
        ("region", "Region"),
        ("shopify_partner_since", "Shopify partner since"),
        ("team_size", "Team size"),
        ("target_budget_range", "Target budget range"),
        ("delivery_timeline", "Delivery timeline"),
        ("contact_email", "Contact email"),
    ]

    for key, label in required:
        if not form_data.get(key):
            errors.append(f"{label} is required.")

    if len(_parse_lines(form_data.get("strengths_text", ""))) < 2:
        errors.append("Please provide at least 2 strengths.")

    if len(_parse_lines(form_data.get("capabilities_text", ""))) < 2:
        errors.append("Please provide at least 2 capabilities.")

    if logo and logo.filename:
        extension = Path(logo.filename).suffix.lower()
        if extension not in ALLOWED_LOGO_EXTENSIONS:
            errors.append(
                "Partner logo must be one of: SVG, PNG, JPG, JPEG, WEBP."
            )

    return errors


def _build_profile_payload(
    form_data: dict[str, Any], logo_path: str | None = None
) -> dict[str, Any]:
    icp_rows = [
        row
        for row in form_data["icp_rows"]
        if row.get("label", "").strip() or row.get("value", "").strip()
    ]
    if not icp_rows:
        icp_rows = [{"label": "Merchant stage", "value": "Define your best-fit merchant profile."}]

    stories = []
    for row in form_data["success_stories"]:
        if not any(
            [
                row["client"],
                row["industry"],
                row["migration_from"],
                row["summary"],
                row["results_text"],
            ]
        ):
            continue
        stories.append(
            {
                "client": row["client"] or "Client",
                "industry": row["industry"] or "Industry",
                "migration_from": row["migration_from"] or "Legacy platform",
                "summary": row["summary"] or "Add a short scope summary.",
                "results": _parse_lines(row["results_text"])[:4],
            }
        )

    if not stories:
        stories = [
            {
                "client": "Success Story 1",
                "industry": "Industry",
                "migration_from": "Legacy platform",
                "summary": "Add one concise scope summary.",
                "results": ["Result 1", "Result 2"],
            }
        ]

    return {
        "partner_name": form_data["partner_name"],
        "partner_tagline": form_data["partner_tagline"],
        "segment_focus": form_data["segment_focus"],
        "region": form_data["region"],
        "shopify_partner_since": form_data["shopify_partner_since"],
        "team_size": form_data["team_size"],
        "target_budget_range": form_data["target_budget_range"],
        "delivery_timeline": form_data["delivery_timeline"],
        "partner_logo_path": logo_path
        or "assets/partner-logo-placeholder.svg",
        "shopify_logo_path": "assets/shopify-logo-full-color.svg",
        "strengths": _parse_lines(form_data["strengths_text"])[:6],
        "capabilities": _parse_lines(form_data["capabilities_text"])[:6],
        "ideal_customer_profile": icp_rows[:4],
        "success_stories": stories[:3],
        "other_technology_partners": _parse_tag_list(
            form_data["technology_partners_text"]
        )[:12],
        "engagement_model": _parse_lines(form_data["engagement_model_text"])[:4],
        "contact": {
            "slack": form_data["contact_slack"],
            "email": form_data["contact_email"],
            "website": form_data["contact_website"],
        },
        "cta": form_data["cta"] or "Get started with our team",
    }


def _save_logo_to_temp(
    logo: FileStorage | None, destination_dir: Path
) -> str | None:
    if not logo or not logo.filename:
        return None

    extension = Path(logo.filename).suffix.lower()
    if extension not in ALLOWED_LOGO_EXTENSIONS:
        return None

    safe_name = secure_filename(logo.filename) or f"partner_logo{extension}"
    file_path = destination_dir / safe_name
    logo.save(file_path)
    return str(file_path)


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024
app.config["SECRET_KEY"] = os.environ.get(
    "PARTNER_PORTAL_SECRET",
    "dev-only-secret-change-in-production",
)


@app.get("/")
def index() -> str:
    preset = request.args.get("preset", "template").strip().lower()
    profile = _load_preset_profile("sample" if preset == "sample" else "template")
    form_data = _profile_to_form_data(profile, theme="graphite")
    return render_template(
        "index.html",
        form_data=form_data,
        themes=THEMES,
        errors=[],
    )


@app.post("/generate")
def generate() -> Any:
    form_data = _extract_form_data(request.form.to_dict(flat=True))
    logo = request.files.get("partner_logo")
    errors = _validate(form_data, logo)

    if errors:
        return (
            render_template(
                "index.html",
                form_data=form_data,
                themes=THEMES,
                errors=errors,
            ),
            400,
        )

    try:
        with tempfile.TemporaryDirectory(prefix="partner-portal-") as tmp_dir:
            working_dir = Path(tmp_dir)
            logo_path = _save_logo_to_temp(logo, working_dir)
            payload = _build_profile_payload(form_data, logo_path=logo_path)

            html_content = GENERATOR.render_html(
                payload,
                input_dir=working_dir,
                template_dir=TEMPLATE_DIR,
                theme=form_data["theme"],
            )

            html_path = working_dir / "partner_profile.html"
            pdf_path = working_dir / "partner_profile.pdf"
            html_path.write_text(html_content, encoding="utf-8")
            GENERATOR._build_pdf(html_path, pdf_path)
            pdf_bytes = pdf_path.read_bytes()
    except Exception as exc:  # noqa: BLE001
        return (
            render_template(
                "index.html",
                form_data=form_data,
                themes=THEMES,
                errors=[f"Failed to generate PDF: {exc}"],
            ),
            500,
        )

    filename = (
        f"{_slugify(form_data['partner_name'])}_shopify_partner_profile_"
        f"{form_data['theme']}.pdf"
    )
    return send_file(
        io.BytesIO(pdf_bytes),
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf",
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
