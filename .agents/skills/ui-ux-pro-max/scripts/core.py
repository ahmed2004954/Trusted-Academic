#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI/UX Pro Max Core - BM25 search engine for UI/UX style guides
"""

import csv
import re
from pathlib import Path
from math import log
from collections import defaultdict

# ============ CONFIGURATION ============
DATA_DIR = Path(__file__).parent.parent / "data"
MAX_RESULTS = 3

CSV_CONFIG = {
    "style": {
        "file": "styles.csv",
        "search_cols": ["Style Category", "Keywords", "Best For", "Type", "AI Prompt Keywords"],
        "output_cols": ["Style Category", "Type", "Keywords", "Primary Colors", "Effects & Animation", "Best For", "Light Mode ✓", "Dark Mode ✓", "Performance", "Accessibility", "Framework Compatibility", "Complexity", "AI Prompt Keywords", "CSS/Technical Keywords", "Implementation Checklist", "Design System Variables"]
    },
    "color": {
        "file": "colors.csv",
        "search_cols": ["Product Type", "Notes"],
        "output_cols": ["Product Type", "Primary", "On Primary", "Secondary", "On Secondary", "Accent", "On Accent", "Background", "Foreground", "Card", "Card Foreground", "Muted", "Muted Foreground", "Border", "Destructive", "On Destructive", "Ring", "Notes"]
    },
    "chart": {
        "file": "charts.csv",
        "search_cols": ["Data Type", "Keywords", "Best Chart Type", "When to Use", "When NOT to Use", "Accessibility Notes"],
        "output_cols": ["Data Type", "Keywords", "Best Chart Type", "Secondary Options", "When to Use", "When NOT to Use", "Data Volume Threshold", "Color Guidance", "Accessibility Grade", "Accessibility Notes", "A11y Fallback", "Library Recommendation", "Interactive Level"]
    },
    "landing": {
        "file": "landing.csv",
        "search_cols": ["Pattern Name", "Keywords", "Conversion Optimization", "Section Order"],
        "output_cols": ["Pattern Name", "Keywords", "Section Order", "Primary CTA Placement", "Color Strategy", "Conversion Optimization"]
    },
    "product": {
        "file": "products.csv",
        "search_cols": ["Product Type", "Keywords", "Primary Style Recommendation", "Key Considerations"],
        "output_cols": ["Product Type", "Keywords", "Primary Style Recommendation", "Secondary Styles", "Landing Page Pattern", "Dashboard Style (if applicable)", "Color Palette Focus"]
    },
    "ux": {
        "file": "ux-guidelines.csv",
        "search_cols": ["Category", "Issue", "Description", "Platform"],
        "output_cols": ["Category", "Issue", "Platform", "Description", "Do", "Don't", "Code Example Good", "Code Example Bad", "Severity"]
    },
    "typography": {
        "file": "typography.csv",
        "search_cols": ["Font Pairing Name", "Category", "Mood/Style Keywords", "Best For", "Heading Font", "Body Font"],
        "output_cols": ["Font Pairing Name", "Category", "Heading Font", "Body Font", "Mood/Style Keywords", "Best For", "Google Fonts URL", "CSS Import", "Tailwind Config", "Notes"]
    },
    "icons": {
        "file": "icons.csv",
        "search_cols": ["Category", "Icon Name", "Keywords", "Best For"],
        "output_cols": ["Category", "Icon Name", "Keywords", "Library", "Import Code", "Usage", "Best For", "Style"]
    },
    "gsap": {
        "file": "motion.csv",
        "search_cols": ["Category", "Intensity Tier", "Keywords", "Trigger"],
        "output_cols": ["Category", "Intensity Tier", "Trigger", "Duration", "Easing", "GSAP Snippet", "Framework Notes", "Do", "Don't", "Performance Notes"]
    },
    "react": {
        "file": "react-performance.csv",
        "search_cols": ["Category", "Issue", "Keywords", "Description"],
        "output_cols": ["Category", "Issue", "Platform", "Description", "Do", "Don't", "Code Example Good", "Code Example Bad", "Severity"]
    },
    "web": {
        "file": "app-interface.csv",
        "search_cols": ["Category", "Issue", "Keywords", "Description"],
        "output_cols": ["Category", "Issue", "Platform", "Description", "Do", "Don't", "Code Example Good", "Code Example Bad", "Severity"]
    },
    "google-fonts": {
        "file": "google-fonts.csv",
        "search_cols": ["Family", "Category", "Stroke", "Classifications", "Keywords", "Subsets", "Designers"],
        "output_cols": ["Family", "Category", "Stroke", "Classifications", "Keywords", "Subsets", "Variants", "Designers", "Popularity Rank"]
    },
}

AVAILABLE_STACKS = [
    "html-tailwind", "react", "nextjs", "astro", "vue", "nuxtjs", "nuxt-ui",
    "svelte", "swiftui", "react-native", "flutter", "shadcn", "jetpack-compose",
    "threejs", "angular", "laravel", "javafx", "wpf", "winui", "avalonia", "uno", "uwp"
]


# ============ BM25 ENGINE ============

def tokenize(text):
    """Tokenize text into lowercase words"""
    if not text:
        return []
    return re.findall(r'\b\w+\b', str(text).lower())


def load_csv(domain):
    """Load CSV file for a domain"""
    config = CSV_CONFIG.get(domain)
    if not config:
        return None, None, f"Unknown domain: {domain}"

    filepath = DATA_DIR / config["file"]
    if not filepath.exists():
        return None, None, f"Data file not found: {filepath}"

    rows = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
    except Exception as e:
        return None, None, f"Error reading {filepath}: {e}"

    return rows, config, None


def bm25_score(query_tokens, doc_tokens, avg_dl, doc_count, df, k1=1.5, b=0.75):
    """Calculate BM25 score for a document"""
    score = 0.0
    dl = len(doc_tokens)

    for term in query_tokens:
        if term not in df:
            continue
        tf = doc_tokens.count(term)
        if tf == 0:
            continue

        idf = log((doc_count - df[term] + 0.5) / (df[term] + 0.5) + 1)
        tf_norm = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avg_dl))
        score += idf * tf_norm

    return score


def search(query, domain="style", max_results=3):
    """Search a domain using BM25 ranking"""
    rows, config, error = load_csv(domain)
    if error:
        return {"error": error}

    if not rows:
        return {"error": f"No data found for domain: {domain}"}

    query_tokens = tokenize(query)
    if not query_tokens:
        return {"error": "Empty query"}

    # Build document tokens
    doc_tokens_list = []
    for row in rows:
        tokens = []
        for col in config["search_cols"]:
            tokens.extend(tokenize(row.get(col, "")))
        doc_tokens_list.append(tokens)

    # Calculate document frequencies
    df = defaultdict(int)
    for tokens in doc_tokens_list:
        seen = set(tokens)
        for token in seen:
            df[token] += 1

    # Calculate average document length
    total_tokens = sum(len(t) for t in doc_tokens_list)
    avg_dl = total_tokens / len(doc_tokens_list) if doc_tokens_list else 1

    # Score documents
    scored = []
    for i, (row, tokens) in enumerate(zip(rows, doc_tokens_list)):
        score = bm25_score(query_tokens, tokens, avg_dl, len(rows), df)
        if score > 0:
            scored.append((score, i, row))

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    # Format output
    results = []
    for score, idx, row in scored[:max_results]:
        result = {}
        for col in config["output_cols"]:
            val = row.get(col, "")
            if val and str(val).strip():
                result[col] = val
        results.append(result)

    return {
        "domain": domain,
        "query": query,
        "count": len(results),
        "results": results
    }


def search_stack(query, stack, max_results=3):
    """Search stack-specific guidelines"""
    stack_file = DATA_DIR / "stacks" / f"{stack}.csv"

    if not stack_file.exists():
        # Fall back to main style search with stack context
        result = search(f"{query} {stack}", "style", max_results)
        result["stack"] = stack
        return result

    rows = []
    try:
        with open(stack_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
    except Exception as e:
        return {"error": f"Error reading {stack_file}: {e}"}

    if not rows:
        return {"error": f"No data for stack: {stack}"}

    query_tokens = tokenize(query)
    headers = list(rows[0].keys()) if rows else []

    # Build tokens and score
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
            scored.append((score, i, row))

    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    for score, idx, row in scored[:max_results]:
        result = {}
        for col in headers:
            val = row.get(col, "")
            if val and str(val).strip():
                result[col] = val
        results.append(result)

    return {
        "stack": stack,
        "query": query,
        "count": len(results),
        "results": results
    }
