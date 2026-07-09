#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI/UX Pro Max Search - BM25 search engine for UI/UX style guides
Usage: python search.py "<query>" [--domain <domain>] [--stack <stack>] [--max-results 3]
       python search.py "<query>" --design-system [-p "Project Name"]
       python search.py "<query>" --design-system --persist [-p "Project Name"] [--page "dashboard"]
       python search.py "<query>" --design-system --variance 8 --motion 9 --density 7

Domains: style, prompt, color, chart, landing, product, ux, typography, google-fonts, gsap
Stacks: react, nextjs, vue, svelte, astro, swiftui, react-native, flutter, nuxtjs, nuxt-ui, html-tailwind, shadcn, jetpack-compose, threejs, angular, laravel, javafx, wpf, winui, avalonia, uno, uwp

Design dials (1-10, only with --design-system):
  --variance   DESIGN_VARIANCE: 1=centered/minimal, 10=bold/asymmetric
  --motion     MOTION_INTENSITY: 1=subtle, 10=complex; attaches a GSAP snippet from motion.csv
  --density    VISUAL_DENSITY: 1=spacious, 10=dense/dashboard; overrides the spacing scale

Persistence (Master + Overrides pattern):
  --persist    Save design system to design-system/MASTER.md
  --page       Also create a page-specific override file in design-system/pages/
"""

import argparse
import sys
import io
from core import CSV_CONFIG, AVAILABLE_STACKS, MAX_RESULTS, search, search_stack
from design_system import generate_design_system, persist_design_system

# Force UTF-8 for stdout/stderr to handle emojis on Windows (cp1252 default)
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def format_output(result):
    """Format results for Claude consumption (token-optimized)"""
    if "error" in result:
        return f"Error: {result['error']}"

    output = []
    if result.get("stack"):
        output.append(f"## UI Pro Max Stack Guidelines")
        output.append(f"**Stack:** {result['stack']} | **Query:** {result['query']}")
    else:
        output.append(f"## UI Pro Max Search Results")
        output.append(f"**Domain:** {result['domain']} | **Query:** {result['query']} | **Results:** {result['count']}")

    for i, item in enumerate(result.get("results", []), 1):
        output.append(f"\n### Result {i}")
        if isinstance(item, dict):
            for key, value in item.items():
                if value and str(value).strip():
                    output.append(f"**{key}:** {value}")
        else:
            output.append(str(item))

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="UI/UX Pro Max Search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--domain", "-d", default="style",
                        choices=list(CSV_CONFIG.keys()),
                        help="Search domain")
    parser.add_argument("--stack", "-s", default=None,
                        choices=AVAILABLE_STACKS,
                        help="Tech stack for guidelines")
    parser.add_argument("--max-results", "-n", type=int, default=MAX_RESULTS,
                        help="Maximum results to return")
    parser.add_argument("--design-system", action="store_true",
                        help="Generate complete design system")
    parser.add_argument("-p", "--project", default=None,
                        help="Project name for design system")
    parser.add_argument("--persist", action="store_true",
                        help="Save design system to file")
    parser.add_argument("--page", default=None,
                        help="Page-specific override")
    parser.add_argument("--variance", type=int, default=None,
                        help="Design variance dial (1-10)")
    parser.add_argument("--motion", type=int, default=None,
                        help="Motion intensity dial (1-10)")
    parser.add_argument("--density", type=int, default=None,
                        help="Visual density dial (1-10)")

    args = parser.parse_args()

    if args.design_system:
        dials = {}
        if args.variance is not None:
            dials['variance'] = max(1, min(10, args.variance))
        if args.motion is not None:
            dials['motion'] = max(1, min(10, args.motion))
        if args.density is not None:
            dials['density'] = max(1, min(10, args.density))

        result = generate_design_system(args.query, project_name=args.project, dials=dials)
        print(result)

        if args.persist:
            persist_result = persist_design_system(result, project_name=args.project, page=args.page)
            print(f"\n{persist_result}")
    elif args.stack:
        result = search_stack(args.query, args.stack, max_results=args.max_results)
        print(format_output(result))
    else:
        result = search(args.query, args.domain, max_results=args.max_results)
        print(format_output(result))


if __name__ == "__main__":
    main()
