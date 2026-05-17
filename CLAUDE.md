# Fahad's Global Claude Instructions

## Identity & Context

I am Fahad. My work spans three interconnected domains:

1. **Electrical Contracting & Project Management** — Kuwait-based, covering residential villas (قسيمة سكنية), commercial buildings, and infrastructure projects.
2. **Judicial Engineering Expert Work** — Preparing technical expert reports (تقارير خبرة هندسية) submitted to Kuwaiti courts, covering construction and electrical disputes.
3. **Legal-Technical Consulting** — Supporting dispute analysis under Kuwaiti Civil Law, Public Tenders Law No. 49/2016, and related administrative instruments.

All standards, pricing, legal references, and compliance requirements are **Kuwait-specific** unless explicitly stated otherwise.

---

## Language Rules

- **Code**: always in English (variable names, comments, function names, strings)
- **User-facing content / UI labels / reports**: Arabic by default unless specified otherwise
- **Commit messages**: English
- **Documentation**: Arabic unless stated otherwise
- **RTL layouts**: always apply for Arabic UIs — use `dir="rtl"`, `text-align: right`, RTL-aware flex/grid
- **Arabic register**: formal Modern Standard Arabic (فصحى رسمية) for all court/official documents; Kuwaiti dialect only if explicitly requested for informal content

---

## Code Style & Conventions

### General
- Indentation: **2 spaces** (no tabs)
- Quotes: **single quotes** in JS/TS, double quotes in Python
- Semicolons: **yes** in JS/TS
- Max line length: **100 characters**
- Always use **named exports** (avoid default exports except for React pages/components)
- Prefer **async/await** over `.then()` chains
- Never leave `console.log` in production code — use a logger or remove

### Naming
- Files: `kebab-case` (e.g. `boq-calculator.ts`)
- React components: `PascalCase` (e.g. `BoqTable.tsx`)
- Functions & variables: `camelCase`
- Constants: `UPPER_SNAKE_CASE`
- Database columns: `snake_case`
- Arabic content keys in i18n: `snake_case` English keys (e.g. `total_price`, `project_name`)

### TypeScript
- Strict mode: **on**
- Prefer `interface` over `type` for object shapes
- Always type function return values explicitly
- No `any` — use `unknown` and narrow it

### React
- Functional components only (no class components)
- Hooks at the top of the component, before any logic
- Keep components under ~150 lines; extract if larger
- Use Tailwind CSS for styling — no inline styles except dynamic values
- RTL: always test layouts with Arabic content

---

## Project Structure (Standard Pattern)

```
project-root/
├── src/
│   ├── components/       # Reusable UI components
│   ├── pages/            # Route-level components
│   ├── features/         # Feature modules (self-contained)
│   ├── hooks/            # Custom React hooks
│   ├── utils/            # Pure utility functions
│   ├── types/            # Shared TypeScript types/interfaces
│   ├── constants/        # App-wide constants
│   ├── api/              # API calls and service layer
│   └── i18n/             # Arabic/English translations
├── public/
├── tests/
└── CLAUDE.md             # Project-level overrides go here
```

---

## Common Commands

```bash
# Install
npm install

# Dev server
npm run dev

# Build
npm run build

# Lint / Lint + fix
npm run lint
npm run lint:fix

# Type check
npx tsc --noEmit

# Tests
npm test
npm run test:watch
npm test -- path/to/file.test.ts
```

For Python projects:
```bash
pip install -r requirements.txt
python -m pytest
python -m pytest tests/test_file.py
```

---

## Domain A — Electrical Contracting (Kuwait)

### Standards & Compliance
- Primary authority: **MEW (Ministry of Electricity & Water, Kuwait)**
- International standards in order of preference: **IEC → BS → ISO**
- MEW approval required for all main distribution panels, transformers, and generators
- Cross-reference Saudi standards (SASO, SBC) only when explicitly requested

### Key Document Types
- **BOQ** (Bill of Quantities / جداول الكميات): itemized cost breakdown per work scope
- **مستخلص** (Interim Payment Certificate): progress billing document
- **عقد مقاولة**: main contract
- **عقد مقاولة من الباطن**: subcontract
- **خطاب ضمان**: bank guarantee / letter of guarantee
- **LC** (Letter of Credit): payment instrument in large contracts
- **أوامر تغييرية**: variation/change orders
- **محضر استلام**: handover/acceptance record

### Pricing Context (Kuwait Market)
- Currency: **KWD (Kuwaiti Dinar)**
- Generator brands: **Perkins** (UK) and **CAT** (Caterpillar) — most common in Kuwait
- Transformer supplier: **South Wales Switchgear** frequently referenced
- Labor rates are Kuwait market rates (include MEW-licensed electrician premiums)
- Always separate: material cost / labor cost / overhead / profit in BOQ breakdowns

### Residential Villa Standard (قسيمة سكنية)
- Typical plot: 400–600 m²
- Standard supply: MEW single-phase (small villas) or three-phase
- Earthing system: TN-S per MEW requirements
- DB sizing, cable sizing, and protection coordination per MEW residential specs

---

## Domain B — Judicial Engineering Expert Reports (خبرة قضائية)

### Legal Framework
- Governing law: **Kuwaiti Civil Law**
- Key instruments: Public Tenders Law No. 49/2016, Administrative Decision No. 30/2012, 2024 Expert Procedures Manual (دليل إجراءات الخبرة)
- **Do NOT generate Civil Law article numbers from memory** — ask me to provide or verify before citing any specific article
- Common dispute types: contractor withdrawal, LC non-payment, variation order disputes, subcontracting scope delineation, defective works, incomplete works, non-conforming specifications

### Report Structure (Standard Court Format)
All expert reports follow this structure unless the court order specifies otherwise:

```
1. مقدمة وبيانات الدعوى
2. الإجراءات المتخذة
3. الوقائع والمستندات
4. المعاينة الميدانية (if applicable)
5. التحليل الفني والهندسي
6. الرأي الفني المسبب
7. الخلاصة والتوصية
```

### Expert Report Writing Rules
- Language: formal academic Arabic (فصحى رسمية أكاديمية) — judicial, neutral, precise
- Tone: technical-legal, objective, no emotional or rhetorical language
- Every technical finding must be backed by: field observation, document analysis, or reference to an applicable standard
- When documentation is absent (e.g., no signed handover inventory), address how facts can be established through independent expert assessment or alternative evidentiary methods
- Distinguish clearly between: أعمال منفذة / أعمال ناقصة / أعمال معيبة / أعمال مخالفة للمواصفات
- Outputs must be suitable for court submission without further editing

### Key Technical Terms (always use precise Arabic)
| English | Arabic |
|---|---|
| Bill of Quantities | جداول الكميات |
| Interim payment certificate | مستخلص |
| Variation / Change order | أمر تغييري |
| Field inspection | معاينة ميدانية |
| Engineering inventory | جرد هندسي |
| Defective works | أعمال معيبة |
| Non-conforming works | أعمال مخالفة للمواصفات |
| Incomplete works | أعمال ناقصة |
| Handover record | محضر استلام |
| Subcontractor | مقاول من الباطن |
| Scope of work | نطاق الأعمال |
| Technical specification | المواصفة الفنية |

---

## Domain C — Web & Application Design

### Design Philosophy
All websites and applications must be at a **professional, high-end level** with:
- Animated, beautiful, and creative icons and visual elements
- Smooth micro-interactions and transitions on all interactive elements
- A distinctive, memorable aesthetic — never generic AI-generated look
- RTL-first design for Arabic interfaces

### Design Standards
- **Animations**: Every UI must include meaningful animations — floating elements, scroll-reveal, hover effects, ripple clicks, staggered entrances. No static interfaces.
- **Icons**: Use animated SVG icons or Lucide/Heroicons with CSS animation layered on top. Icons should feel alive, not decorative afterthoughts.
- **Typography**: Choose distinctive, characterful fonts from Google Fonts. Pair a display font with a refined body font. Never use Arial, Roboto, or Inter as the primary face.
- **Color**: Commit to a cohesive theme — rich dark luxury OR soft pastel premium OR bold editorial. CSS variables for all colors. Never timid, evenly-distributed palettes.
- **Backgrounds**: Depth and atmosphere over flat colors — gradient meshes, subtle noise textures, geometric patterns, layered glassmorphism, particle fields.
- **Spatial Composition**: Unexpected layouts — asymmetry, overlapping elements, diagonal flows, generous negative space, grid-breaking accents.
- **Cards & Components**: Always include hover elevation (translateY + shadow upgrade), glassmorphism where appropriate, and smooth border transitions.

### Animation Patterns (always implement)
```css
/* Scroll reveal — apply .reveal class, trigger via IntersectionObserver */
opacity: 0 → 1, scale(0.97) → scale(1), duration 0.6s, cubic-bezier(0.22, 1, 0.36, 1)

/* Floating elements */
translateY: 0 → -6px → 0, 3s–5s, ease-in-out, infinite

/* Card hover */
translateY: -4px, box-shadow upgrade, 0.3s cubic-bezier(0.22, 1, 0.36, 1)

/* Button click — ripple effect via JS */
Expand radial circle from click point, fade out, 0.4s

/* Navbar — load entrance */
translateY(-100%) → translateY(0), 0.5s, backdrop-filter: blur(12px)
```

### Background Bubble / Particle Layer
For full-page designs, always generate a dynamic animated background layer:
- 12–18 floating orbs/bubbles, randomized size (40–120px), staggered delays
- Colors match the page theme (mint/blue/lavender for pastel; gold/teal for luxury; etc.)
- opacity 0.3–0.4, pointer-events: none, z-index: 0

### Arabic UI Requirements
- `dir="rtl"` on `<html>` or root component
- Flex/grid: use `flex-start` = right, account for RTL icon placement
- Numbers: use Arabic-Indic numerals (٠١٢٣) in document/report contexts; Western numerals (0123) in dashboards/code contexts
- Font: use Arabic-compatible fonts — **Cairo**, **Tajawal**, **Noto Kufi Arabic** paired with a display English font where mixed content exists

### Tech Stack Preference
- **Full pages**: pure HTML/CSS/JS single file unless React is requested
- **Components**: React functional components with Tailwind CSS
- **Animations**: CSS-first; JS only for dynamic values (bubble positions, ripple coords)
- **Icons**: Lucide React (in React), or inline animated SVG (in HTML)
- No external animation libraries unless specifically needed (GSAP for complex timelines only)

### Quality Gate — Before Delivering Any UI
- [ ] Animated icons present and feel intentional, not decorative
- [ ] Scroll-reveal on all major sections
- [ ] All buttons: hover scale + ripple click
- [ ] All cards: hover elevation
- [ ] Background has depth (not a flat solid color)
- [ ] At least one floating/pulsing element
- [ ] RTL correctly applied for Arabic content
- [ ] Mobile responsive (flexbox/grid, no fixed widths)
- [ ] No generic fonts (Arial, Roboto, Inter as primary)
- [ ] No purple-gradient-on-white clichés

---

## Output Format Preferences

### General
- Code: always in fenced code blocks with language tag
- Show working step-by-step for calculations (electrical load, cable sizing, penalty calc, etc.)
- Prefer small, reviewable changes over sweeping rewrites

### Arabic Documents (Reports, Contracts, Memos)
- RTL, formal فصحى, structured with clear numbered headings
- Use proper Arabic punctuation (،، ؟ ؛)
- Deliver in both Markdown AND Word (.docx) format when the output is a court document

### BOQ Tables
Columns: رقم | البند | الوحدة | الكمية | سعر الوحدة | الإجمالي
Always include: summary row, unit column, totals per section

### Dispute / Legal Analysis
Sections: الوقائع → التحليل الفني → الرأي الفني المسبب → التوصية

### Electrical Calculations
Always show: formula → substitution → result → unit → interpretation
Reference the applicable standard (MEW / IEC / BS) for each parameter used

---

## Behavior Rules

- **Explain before acting**: always describe what you're about to do before significant changes to existing code or documents
- **Never delete** existing code or content without confirmation
- **Ask before refactoring** — propose first, act only after approval
- **Flag uncertainty**: if unsure about a Kuwait-specific regulation, market price, or legal article — say so explicitly, never guess
- **Legal content**: flag any article number or clause before citing; do not generate Civil Law articles from memory
- **Calculations**: always show working; never give a bare result
- **UI/Design**: never deliver a static, unanimated interface — animation is a baseline requirement, not a feature

---

*Global file: `~/.claude/CLAUDE.md`*
*Project-level overrides: add `CLAUDE.md` in the project root.*
