#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI/UX Pro Max Design System Generator
Generates complete, tailored design systems using multi-domain BM25 search
"""

import json
import os
from pathlib import Path
from core import search, DATA_DIR, load_csv, tokenize, bm25_score
from collections import defaultdict
from math import log


def generate_design_system(query, project_name=None, dials=None):
    """
    Generate a complete design system based on project description.
    Runs parallel searches across: product, style, color, typography, landing
    Then synthesizes into a unified design system recommendation.
    """
    if dials is None:
        dials = {}

    variance = dials.get('variance', 5)
    motion = dials.get('motion', 3)
    density = dials.get('density', 5)

    # Run multi-domain searches
    product_results = search(query, "product", max_results=3)
    style_results = search(query, "style", max_results=5)
    color_results = search(query, "color", max_results=3)
    typography_results = search(query, "typography", max_results=3)
    landing_results = search(query, "landing", max_results=2)

    # Also search reasoning rules if available
    reasoning_results = _search_reasoning(query)

    # Motion search if dial is set
    motion_results = None
    if motion and motion > 1:
        motion_query = _motion_query_from_dial(motion, query)
        motion_results = search(motion_query, "gsap", max_results=2)

    # Build the design system output
    output = []
    name = project_name or "Project"

    output.append(f"+{'=' * 80}+")
    output.append(f"| TARGET: {name} - RECOMMENDED DESIGN SYSTEM")
    output.append(f"+{'=' * 80}+")
    output.append("")

    # === PATTERN ===
    if landing_results and landing_results.get("results"):
        landing = landing_results["results"][0]
        output.append("PATTERN:")
        if landing.get("Pattern Name"):
            output.append(f"  Layout: {landing['Pattern Name']}")
        if landing.get("Section Order"):
            output.append(f"  Sections: {landing['Section Order']}")
        if landing.get("Primary CTA Placement"):
            output.append(f"  CTA: {landing['Primary CTA Placement']}")
        if landing.get("Conversion Optimization"):
            output.append(f"  Conversion: {landing['Conversion Optimization']}")
        output.append("")

    # === STYLE ===
    if style_results and style_results.get("results"):
        style = style_results["results"][0]
        output.append("STYLE:")
        if style.get("Style Category"):
            output.append(f"  Category: {style['Style Category']}")
        if style.get("Keywords"):
            output.append(f"  Keywords: {style['Keywords']}")
        if style.get("Best For"):
            output.append(f"  Best For: {style['Best For']}")
        if style.get("Performance"):
            output.append(f"  Performance: {style['Performance']}")
        if style.get("Accessibility"):
            output.append(f"  Accessibility: {style['Accessibility']}")
        if style.get("CSS/Technical Keywords"):
            output.append(f"  CSS Keywords: {style['CSS/Technical Keywords']}")
        if style.get("Design System Variables"):
            output.append(f"  Variables: {style['Design System Variables']}")
        if style.get("Implementation Checklist"):
            output.append(f"  Checklist: {style['Implementation Checklist']}")

        # Show secondary styles if variance is high
        if variance >= 7 and len(style_results["results"]) > 1:
            alt_style = style_results["results"][1]
            if alt_style.get("Style Category"):
                output.append(f"  Alt Style: {alt_style['Style Category']} ({alt_style.get('Keywords', '')})")
        output.append("")

    # === COLORS ===
    if color_results and color_results.get("results"):
        color = color_results["results"][0]
        output.append("COLORS:")
        for key in ["Primary", "On Primary", "Secondary", "On Secondary", "Accent", "On Accent",
                     "Background", "Foreground", "Card", "Card Foreground", "Muted", "Muted Foreground",
                     "Border", "Destructive", "On Destructive", "Ring"]:
            val = color.get(key, "")
            if val:
                output.append(f"  {key}: {val}")
        if color.get("Notes"):
            output.append(f"  Notes: {color['Notes']}")
        output.append("")

    # === TYPOGRAPHY ===
    if typography_results and typography_results.get("results"):
        typo = typography_results["results"][0]
        output.append("TYPOGRAPHY:")
        if typo.get("Font Pairing Name"):
            output.append(f"  Pairing: {typo['Font Pairing Name']}")
        if typo.get("Heading Font"):
            output.append(f"  Heading: {typo['Heading Font']}")
        if typo.get("Body Font"):
            output.append(f"  Body: {typo['Body Font']}")
        if typo.get("Mood/Style Keywords"):
            output.append(f"  Mood: {typo['Mood/Style Keywords']}")
        if typo.get("Best For"):
            output.append(f"  Best For: {typo['Best For']}")
        if typo.get("Google Fonts URL"):
            output.append(f"  Google Fonts: {typo['Google Fonts URL']}")
        if typo.get("CSS Import"):
            output.append(f"  CSS Import: {typo['CSS Import']}")
        if typo.get("Tailwind Config"):
            output.append(f"  Tailwind: {typo['Tailwind Config']}")
        output.append("")

    # === PRODUCT CONTEXT ===
    if product_results and product_results.get("results"):
        product = product_results["results"][0]
        output.append("PRODUCT CONTEXT:")
        if product.get("Product Type"):
            output.append(f"  Type: {product['Product Type']}")
        if product.get("Primary Style Recommendation"):
            output.append(f"  Recommended Style: {product['Primary Style Recommendation']}")
        if product.get("Secondary Styles"):
            output.append(f"  Alt Styles: {product['Secondary Styles']}")
        if product.get("Landing Page Pattern"):
            output.append(f"  Landing Pattern: {product['Landing Page Pattern']}")
        if product.get("Color Palette Focus"):
            output.append(f"  Color Focus: {product['Color Palette Focus']}")
        output.append("")

    # === KEY EFFECTS ===
    if style_results and style_results.get("results"):
        style = style_results["results"][0]
        if style.get("Effects & Animation"):
            output.append("KEY EFFECTS:")
            output.append(f"  {style['Effects & Animation']}")
            output.append("")

    # === MOTION ===
    if motion_results and motion_results.get("results"):
        output.append(f"MOTION (Intensity: {motion}/10):")
        for m in motion_results["results"][:2]:
            if m.get("GSAP Snippet"):
                output.append(f"  [{m.get('Category', 'animation')}] {m.get('Trigger', 'on-load')}")
                output.append(f"  Duration: {m.get('Duration', '0.3s')} | Easing: {m.get('Easing', 'ease')}")
                output.append(f"  Code: {m['GSAP Snippet'][:200]}")
            if m.get("Performance Notes"):
                output.append(f"  Performance: {m['Performance Notes']}")
        output.append("")

    # === DENSITY ===
    if density != 5:
        output.append(f"DENSITY ({density}/10):")
        if density <= 3:
            output.append("  Spacing: Generous padding, wide margins, breathing room")
            output.append("  Scale: 1rem base, 1.5-2x multipliers")
        elif density >= 7:
            output.append("  Spacing: Compact, efficient use of space, dashboard-ready")
            output.append("  Scale: 0.75rem base, 1-1.25x multipliers")
        else:
            output.append("  Spacing: Balanced, standard padding")
        output.append("")

    # === REASONING RULES ===
    if reasoning_results:
        output.append("REASONING (Industry-Specific):")
        for rule in reasoning_results[:2]:
            for key, val in rule.items():
                if val and str(val).strip():
                    output.append(f"  {key}: {val}")
        output.append("")

    # === ANTI-PATTERNS ===
    output.append("AVOID (Anti-patterns):")
    output.append("  - Generic colors (plain red, blue, green)")
    output.append("  - Browser default typography")
    output.append("  - Missing hover states")
    output.append("  - Missing focus indicators")
    output.append("  - Emojis as icons (use SVG: Heroicons/Lucide)")
    if style_results and style_results.get("results"):
        style = style_results["results"][0]
        if "dark" in query.lower() and style.get("Light Mode ✓"):
            output.append("  - Low contrast text on dark backgrounds")
    output.append("")

    # === PRE-DELIVERY CHECKLIST ===
    output.append("PRE-DELIVERY CHECKLIST:")
    output.append("  [ ] No emojis as icons (use SVG: Heroicons/Lucide)")
    output.append("  [ ] cursor-pointer on all clickable elements")
    output.append("  [ ] Hover states with smooth transitions (150-300ms)")
    output.append("  [ ] Light mode: text contrast 4.5:1 minimum")
    output.append("  [ ] Focus states visible for keyboard nav")
    output.append("  [ ] prefers-reduced-motion respected")
    output.append("  [ ] Responsive: 375px, 768px, 1024px, 1440px")
    output.append("")

    output.append(f"+{'=' * 80}+")

    return "\n".join(output)


def _search_reasoning(query):
    """Search UI reasoning rules if available"""
    reasoning_file = DATA_DIR / "ui-reasoning.csv"
    if not reasoning_file.exists():
        return []

    import csv
    rows = []
    try:
        with open(reasoning_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
    except Exception:
        return []

    if not rows:
        return []

    query_tokens = tokenize(query)
    headers = list(rows[0].keys())

    doc_tokens_list = []
    for row in rows:
        tokens = []
        for col in headers:
            tokens.extend(tokenize(row.get(col, "")))
        doc_tokens_list.append(tokens)

    df = defaultdict(int)
    for tokens in doc_tokens_list:
        seen = set(tokens)
        for token in seen:
            df[token] += 1

    total_tokens = sum(len(t) for t in doc_tokens_list)
    avg_dl = total_tokens / len(doc_tokens_list) if doc_tokens_list else 1

    scored = []
    for i, (row, tokens) in enumerate(zip(rows, doc_tokens_list)):
        score = bm25_score(query_tokens, tokens, avg_dl, len(rows), df)
        if score > 0:
            scored.append((score, row))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [row for _, row in scored[:3]]


def _motion_query_from_dial(motion_level, base_query):
    """Map motion dial to search terms"""
    if motion_level <= 2:
        return f"{base_query} subtle hover fade"
    elif motion_level <= 4:
        return f"{base_query} smooth transition entrance"
    elif motion_level <= 6:
        return f"{base_query} scroll reveal stagger"
    elif motion_level <= 8:
        return f"{base_query} parallax page transition complex"
    else:
        return f"{base_query} cinematic immersive loading sequence"


def persist_design_system(design_system_text, project_name=None, page=None):
    """Save design system to file(s)"""
    output_dir = Path.cwd() / "design-system"
    output_dir.mkdir(exist_ok=True)

    # Write master file
    master_file = output_dir / "MASTER.md"
    name = project_name or "Project"

    content = f"# {name} Design System\n\n"
    content += f"Generated by UI/UX Pro Max\n\n"
    content += "```\n"
    content += design_system_text
    content += "\n```\n"

    with open(master_file, 'w', encoding='utf-8') as f:
        f.write(content)

    result = f"Saved design system to {master_file}"

    # Write page-specific override if requested
    if page:
        pages_dir = output_dir / "pages"
        pages_dir.mkdir(exist_ok=True)
        page_file = pages_dir / f"{page}.md"

        page_content = f"# {name} - {page.title()} Page Overrides\n\n"
        page_content += f"Inherits from: ../MASTER.md\n\n"
        page_content += "## Page-Specific Overrides\n\n"
        page_content += "<!-- Add page-specific design overrides here -->\n"

        with open(page_file, 'w', encoding='utf-8') as f:
            f.write(page_content)

        result += f"\nSaved page override to {page_file}"

    return result
