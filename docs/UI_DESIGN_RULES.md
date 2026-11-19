# UI Design Rules & Guidelines

**Visual Theme:** Operating Systems Research Workbench  
**Tone:** Functional, precise, editorial, and instrument-like.

---

## 1. Color Palette

Every color must carry functional meaning rather than serving purely decorative purposes.

| Token | Hex Code | Purpose |
|---|---|---|
| **Canvas** | `#F3F5F6` | Cool paper grey background |
| **Main Surface** | `#FFFFFF` | Card & content background |
| **Primary Text** | `#17232D` | High contrast interface text |
| **Secondary Text** | `#5E6B75` | Captions, metadata, subtitles |
| **Border** | `#D9E0E4` | Crisp, low-contrast structural dividers |
| **Primary Accent** | `#147D78` | Research teal for primary controls & SJF |
| **Secondary Accent**| `#345F86` | Classical slate blue for Priority |
| **Highlight / Caution** | `#C17A24`| Amber for warnings, quantum highlights & RR |
| **Error / Alert** | `#B64D4D` | Run failures & destructive confirmations |
| **Success / Valid** | `#34765A` | Passed checks, finished runs |

### Fixed Policy-to-Color Mapping for All Visualizations
- **FCFS:** Slate Grey (`#7F8C8D`)
- **SJF:** Deep Teal (`#147D78`)
- **Round Robin:** Warm Amber (`#C17A24`)
- **Priority:** Slate Blue (`#345F86`)
- **ML Recommender:** Forest Jade (`#1B4D3E` with prominent marker/border)
- **CPU Idle:** Light Stippled Grey (`#E2E8F0`)

---

## 2. Typography

- **Interface Text:** IBM Plex Sans (fallback: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif)
- **Numeric & Code Data:** IBM Plex Mono (fallback: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace)
- Numbers in tables and metric panels MUST use tabular figures for strict vertical alignment.

---

## 3. Structural Layout & Spacing

- Desktop-first layout optimized for $\ge 1366\text{px}$, responsive down to standard tablet viewports.
- Persistent left navigation sidebar (230–250px wide).
- Compact top environment & status bar (56–64px height).
- Maximum main content width: 1440px with 24–32px outer padding.
- Dense, readable data tables with explicit units in column headers.

---

## 4. Anti-Patterns & Prohibitions

1. **NO Generic AI SaaS Aesthetics:** Absolutely no purple/blue radial gradients, glassmorphism, floating blur blobs, or glowing card borders.
2. **NO Oversized Vanity Metrics:** No giant numbers without units, comparative baselines, or sample size counts.
3. **NO Decorative Emojis:** Do not use random rocket ships, lightning bolts, or brain emojis in headings or status badges.
4. **NO Fabricated Results:** Never show placeholder charts as real findings. Always display clear, informative empty states with reproduction steps when no runs exist.
5. **NO Unlabeled Visuals:** Every plot must have explicit axis titles, units of measure, policy legends, and hover tooltips.
6. **NO Accidental Recomputation:** The UI reads immutable results from the experiment store; it must not compute different scientific values in frontend presentation code.
