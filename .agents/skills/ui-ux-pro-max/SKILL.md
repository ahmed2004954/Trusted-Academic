---
name: ui-ux-pro-max
description: "AI-powered design intelligence with 84 UI styles, 161 color palettes, 73 font pairings, 99 UX guidelines, 25 chart types, and 161 reasoning rules across 22 tech stacks. Use when building user interfaces, selecting design systems, choosing color palettes, picking fonts, designing landing pages, creating dashboards, or generating complete design systems. Actions: search styles, search colors, search fonts, search charts, search UX guidelines, generate design system, search landing page patterns, search GSAP animations."
argument-hint: "[query] [--domain style|color|typography|landing|product|ux|chart|gsap]"
license: MIT
metadata:
  author: NextLevelBuilder
  version: "2.6.2"
  repository: "https://github.com/nextlevelbuilder/ui-ux-pro-max-skill"
---

# UI/UX Pro Max

AI-powered design intelligence toolkit with searchable databases of UI styles, color palettes, font pairings, chart types, UX guidelines, and a design system generator.

## When to Use

- Building any user interface (web, mobile, desktop)
- Selecting a UI style (glassmorphism, minimalism, brutalism, etc.)
- Choosing color palettes for a product type
- Picking font pairings with Google Fonts
- Designing landing pages with conversion optimization
- Creating dashboards with chart recommendations
- Reviewing UX best practices and anti-patterns
- Generating complete, tailored design systems
- Adding GSAP animations

## Search Command

```bash
python .agents/skills/ui-ux-pro-max/scripts/search.py "<query>" --domain <domain> [-n <max_results>]
```

**NOTE (Windows):** Use `python` instead of `python3`.

### Available Domains

| Domain | Description | Records |
|--------|-------------|---------|
| `product` | Product type recommendations (SaaS, e-commerce, portfolio) | 161 |
| `style` | UI styles (glassmorphism, minimalism, brutalism) + AI prompts & CSS keywords | 84 |
| `typography` | Font pairings with Google Fonts imports | 73 |
| `color` | Color palettes by product type | 161 |
| `landing` | Page structure and CTA strategies | 24 |
| `chart` | Chart types and library recommendations | 25 |
| `ux` | Best practices and anti-patterns | 99 |
| `gsap` | GSAP animation skeletons by intensity tier | varies |
| `icons` | Icon recommendations by category | varies |
| `react` | React performance patterns | varies |
| `web` | Web app interface patterns | varies |
| `google-fonts` | Full Google Fonts database search | 1700+ |

### Examples

```bash
# Search for a UI style
python .agents/skills/ui-ux-pro-max/scripts/search.py "modern saas dashboard" --domain style

# Find color palettes for fintech
python .agents/skills/ui-ux-pro-max/scripts/search.py "fintech banking" --domain color

# Get font pairings for a luxury brand
python .agents/skills/ui-ux-pro-max/scripts/search.py "luxury elegant serif" --domain typography

# Landing page patterns for e-commerce
python .agents/skills/ui-ux-pro-max/scripts/search.py "e-commerce product" --domain landing

# UX guidelines for forms
python .agents/skills/ui-ux-pro-max/scripts/search.py "form validation error" --domain ux

# Chart recommendations for time series
python .agents/skills/ui-ux-pro-max/scripts/search.py "time series trend" --domain chart
```

## Design System Generator

Generate a complete, tailored design system based on project requirements:

```bash
python .agents/skills/ui-ux-pro-max/scripts/search.py "<project description>" --design-system [-p "Project Name"]
```

### Design Dials (optional, 1-10)

```bash
python .agents/skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system --variance <1-10> --motion <1-10> --density <1-10>
```

- `--variance` — 1=centered/minimal, 10=bold/asymmetric
- `--motion` — 1=subtle, 10=complex GSAP animations
- `--density` — 1=spacious, 10=dense/dashboard

### Persistence (Master + Overrides)

```bash
python .agents/skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist [-p "Project Name"] [--page "dashboard"]
```

## Stack-Specific Search

Get implementation guidelines for a specific tech stack:

```bash
python .agents/skills/ui-ux-pro-max/scripts/search.py "<query>" --stack <stack>
```

Available stacks: `html-tailwind` (default), `react`, `nextjs`, `astro`, `vue`, `nuxtjs`, `nuxt-ui`, `svelte`, `swiftui`, `react-native`, `flutter`, `shadcn`, `jetpack-compose`, `threejs`, `angular`, `laravel`, `javafx`, `wpf`, `winui`, `avalonia`, `uno`, `uwp`

## Architecture

```
.agents/skills/ui-ux-pro-max/
├── SKILL.md              # This file
├── scripts/
│   ├── search.py         # CLI entry point
│   ├── core.py           # BM25 search engine
│   └── design_system.py  # Design system generator
└── data/
    ├── products.csv      # 161 product types
    ├── styles.csv        # 84 UI styles
    ├── colors.csv        # 161 color palettes
    ├── typography.csv    # 73 font pairings
    ├── landing.csv       # 24 landing page patterns
    ├── charts.csv        # 25 chart types
    ├── ux-guidelines.csv # 99 UX guidelines
    ├── motion.csv        # GSAP animations
    ├── icons.csv         # Icon recommendations
    ├── design.csv        # Design reasoning rules
    ├── ui-reasoning.csv  # 161 reasoning rules
    ├── google-fonts.csv  # Google Fonts database
    ├── react-performance.csv # React patterns
    ├── app-interface.csv # Web app patterns
    └── stacks/           # Stack-specific guides
```

## Pre-Delivery Checklist (from Design System)

- [ ] No emojis as icons (use SVG: Heroicons/Lucide)
- [ ] `cursor-pointer` on all clickable elements
- [ ] Hover states with smooth transitions (150-300ms)
- [ ] Light mode: text contrast 4.5:1 minimum
- [ ] Focus states visible for keyboard navigation
- [ ] `prefers-reduced-motion` respected
- [ ] Responsive: 375px, 768px, 1024px, 1440px
