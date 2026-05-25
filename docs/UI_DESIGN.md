# CET Tracker — UI Design Specification

## 1. Visual Identity

### Keywords
Modern, clean, restrained, academic, focused.

### Vibe
A well-designed study tool — not flashy, not boring. Think Notion / Linear / Craft Docs aesthetic: intentional whitespace, restrained color, clear typographic hierarchy, subtle depth from shadows rather than heavy borders.

### Anti-Template Policy
This design must NOT look like a generic admin dashboard. Specifically avoid:
- Default card grids with uniform spacing and no hierarchy
- Stock hero sections with centered headline and gradient blob
- Unmodified Element Plus defaults passed off as finished design
- Flat layouts with no layering or depth
- Safe gray-on-white styling with one decorative accent color

### Required Qualities Met
This design delivers:
1. Clear hierarchy through scale contrast (stat numbers vs labels, page titles vs card titles)
2. Intentional rhythm in spacing (24px page padding, 24px section gaps, 20px card padding)
3. Depth through shadows and subtle surface layering
4. Typography with a real pairing strategy (Inter for UI, system monospace for data)
5. Color used semantically (green = mastered/success, amber = learning/warning, red = danger/low accuracy)
6. Hover and focus states that feel designed (card lift, accent border on focus)
7. Data visualization treated as part of the design system (charts share palette with UI)

---

## 2. Color System

### CSS Custom Properties

```css
:root {
  /* Primary — Blue-Indigo */
  --color-primary-50: #EEF1FE;
  --color-primary-100: #DDE3FD;
  --color-primary-200: #BBC7FB;
  --color-primary-300: #99ABF9;
  --color-primary-400: #6D86F6;
  --color-primary-500: #4F6EF7;
  --color-primary-600: #3B54D4;
  --color-primary-700: #2C3FA8;
  --color-primary-800: #1E2B7D;
  --color-primary-900: #131B52;

  /* Semantic colors */
  --color-success-50: #F0FDF4;
  --color-success-500: #22C55E;
  --color-success-600: #16A34A;
  --color-success-700: #15803D;

  --color-warning-50: #FFFBEB;
  --color-warning-500: #F59E0B;
  --color-warning-600: #D97706;

  --color-danger-50: #FEF2F2;
  --color-danger-500: #EF4444;
  --color-danger-600: #DC2626;

  --color-info-50: #EFF6FF;
  --color-info-500: #3B82F6;
  --color-info-600: #2563EB;

  /* Neutrals / Surfaces */
  --color-white: #FFFFFF;
  --color-gray-50: #F8FAFC;
  --color-gray-100: #F1F5F9;
  --color-gray-200: #E2E8F0;
  --color-gray-300: #CBD5E1;
  --color-gray-400: #94A3B8;
  --color-gray-500: #64748B;
  --color-gray-600: #475569;
  --color-gray-700: #334155;
  --color-gray-800: #1E293B;
  --color-gray-900: #0F172A;

  /* Text */
  --color-text-primary: var(--color-gray-900);
  --color-text-secondary: var(--color-gray-600);
  --color-text-disabled: var(--color-gray-400);
  --color-text-inverse: var(--color-white);

  /* Semantic text on backgrounds */
  --color-text-on-primary: var(--color-white);
  --color-text-on-success: var(--color-success-600);
  --color-text-on-warning: var(--color-warning-600);
  --color-text-on-danger: var(--color-danger-600);
  --color-text-on-info: var(--color-info-600);

  /* Backgrounds */
  --bg-app: var(--color-gray-50);
  --bg-surface: var(--color-white);
  --bg-sidebar: var(--color-gray-900);
  --bg-sidebar-hover: var(--color-gray-800);
  --bg-sidebar-active: var(--color-primary-600);

  /* Borders */
  --border-light: 1px solid var(--color-gray-200);
  --border-medium: 1px solid var(--color-gray-300);
}
```

### Color Usage Map

| Context | Color | Example |
|---------|-------|---------|
| Primary buttons, active nav, chart lines, selected states | Primary-500 (#4F6EF7) | "Save" button, sidebar active item, line chart stroke |
| Mastered items, high accuracy (>80%), success states | Success-500 (#22C55E) | "mastered" tag, accuracy >= 80% |
| Learning items, medium accuracy (60-80%), warnings | Warning-500 (#F59E0B) | "learning" tag, accuracy 60-80% |
| Low accuracy (<60%), delete actions, errors | Danger-500 (#EF4444) | "new" tag on low accuracy, delete button |
| New items, neutral info, INACTIVE states | Info-500 (#3B82F6) | "new" familiarity tag, info alerts |
| Card backgrounds | White / Gray-50 | Cards, sections |
| App background | Gray-50 | Behind all content |
| Sidebar | Gray-900 | Navigation |

---

## 3. Typography Scale

```css
:root {
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;

  /* Scale */
  --text-hero:    1.5rem;    /* 24px — Page titles */
  --text-xl:      1.25rem;   /* 20px — Section headers, large stat numbers */
  --text-lg:      1.125rem;  /* 18px — Card titles, section subtitles */
  --text-base:    1rem;      /* 16px — Primary body, button text */
  --text-sm:      0.875rem;  /* 14px — Body text, descriptions */
  --text-xs:      0.75rem;   /* 12px — Captions, labels, tags */
  --text-stat:    1.75rem;   /* 28px — Stat card numbers */

  /* Weights */
  --weight-regular: 400;
  --weight-medium:  500;
  --weight-semibold: 600;
  --weight-bold:    700;

  /* Line heights */
  --leading-tight:  1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
}
```

### Typography Application

| Element | Size | Weight | Line Height | Example |
|---------|------|--------|-------------|---------|
| Page title (h1) | 24px | Bold (700) | 1.25 | "Dashboard", "Sessions", "Settings" |
| Section header (h2) | 18px | Semibold (600) | 1.25 | "Recent Sessions", "Vocabulary Mastery" |
| Card title (h3) | 16px | Medium (500) | 1.25 | Session paper name, note title |
| Body text | 14px | Regular (400) | 1.5 | Descriptions, form labels, table cells |
| Caption / label | 12px | Regular (400) | 1.5 | Tags, badges, chart axis labels, timestamps |
| Stat number | 28px | Bold (700) | 1.25 | "156" in vocabulary count card |
| Code / Markdown | 13px | Regular (400) | 1.6 | Raw Markdown display, JSON preview |
| Vocabulary term | 22px | Bold (700) | 1.25 | "pending" in vocabulary card header |
| IPA Phonetic | 14px | Regular (400) | 1.5 | `/ˈpendɪŋ/` displayed after term. Monospace font stack. Color: --color-text-tertiary. UK/US labels in 11px uppercase. |

---

## 4. Spacing System

Base unit: **4px**.

```css
:root {
  --space-xs:  0.25rem;  /*  4px */
  --space-sm:  0.5rem;   /*  8px */
  --space-md:  0.75rem;  /* 12px */
  --space-lg:  1rem;     /* 16px */
  --space-xl:  1.5rem;   /* 24px */
  --space-2xl: 2rem;     /* 32px */
  --space-3xl: 3rem;     /* 48px */
}
```

### Spacing Application

| Context | Value | Variable |
|---------|-------|----------|
| Inline element gap (tags, chips) | 4px | `--space-xs` |
| Form label → input gap | 8px | `--space-sm` |
| Card internal padding | 20px | custom (use 1.25rem) |
| Between related form fields | 16px | `--space-lg` |
| Between sections on a page | 24px | `--space-xl` |
| Page edge padding | 24px | `--space-xl` |
| Between stat cards in grid | 16px | `--space-lg` |
| Between unrelated content blocks | 32px | `--space-2xl` |
| Top/bottom page margin | 48px | `--space-3xl` |

---

## 5. Border Radius

```css
:root {
  --radius-sm:  4px;   /* Tags, badges, small buttons */
  --radius-md:  8px;   /* Cards, inputs, dropdowns, buttons */
  --radius-lg:  12px;  /* Modals, dialogs, large panels */
  --radius-full: 9999px; /* Pills, avatar-style elements */
}
```

---

## 6. Shadows

```css
:root {
  --shadow-card:       0 1px 3px rgba(0, 0, 0, 0.08),
                       0 1px 2px rgba(0, 0, 0, 0.06);
  --shadow-card-hover: 0 4px 6px rgba(0, 0, 0, 0.07),
                       0 2px 4px rgba(0, 0, 0, 0.06);
  --shadow-dropdown:   0 10px 15px rgba(0, 0, 0, 0.1),
                       0 4px 6px rgba(0, 0, 0, 0.05);
  --shadow-modal:      0 20px 25px rgba(0, 0, 0, 0.1),
                       0 10px 10px rgba(0, 0, 0, 0.04);
}
```

**Application**:
- Cards use `--shadow-card` by default, transition to `--shadow-card-hover` on hover.
- Dropdown menus and select popovers use `--shadow-dropdown`.
- Modals (confirm dialogs, large forms) use `--shadow-modal`.
- Do not use box-shadow on every element — only where depth improves scannability.

---

## 7. Layout System

### Overall Structure

```
┌──────────┬──────────────────────────────────────────────┐
│          │                                              │
│  Sidebar │              Content Area                    │
│  220px   │              flex-grow                       │
│  fixed   │              max-width: 1200px               │
│          │              margin: 0 auto                  │
│          │              padding: 24px                   │
│          │                                              │
└──────────┴──────────────────────────────────────────────┘
```

### Sidebar

- **Width**: 220px, fixed position, full viewport height.
- **Background**: `--bg-sidebar` (gray-900).
- **Logo/Brand area**: Top 64px, app name "CET Tracker" in white, 20px bold, with a small blue-indigo accent dot or underline.
- **Nav items**: Vertical list. Each item: 44px height, 16px left padding, icon (18px) + label (14px), white text at 90% opacity. Active item has `--bg-sidebar-active` background and 100% opacity. Hover has `--bg-sidebar-hover`.
- **Nav items list**: Dashboard, Sessions, Vocabulary, Review, Settings.
- **Bottom**: App version badge, small muted text.

### Content Area

- **Layout**: Flex-grow to fill remaining space, with `max-width: 1200px` centered horizontally.
- **Padding**: 24px on all sides.
- **Background**: `--bg-app` (gray-50).
- **Two-column layouts**: Used on Dashboard and Session Detail pages. Left column (60-65% width), right column (35-40% width), 24px gap.
- **Single-column layouts**: Used on list pages (Sessions, Vocabulary) and Settings.

### Responsive Breakpoints

| Breakpoint | Width | Behavior |
|------------|-------|----------|
| Desktop | >= 1024px | Full layout: sidebar expanded, 2-column grids, normal spacing |
| Tablet | 768px - 1023px | Sidebar collapses to icon-only (56px), 2-column becomes 1-column, stat cards go from 4 to 2 |
| Mobile | < 768px | Not a primary target for MVP. Layout degrades gracefully to single column. Minimum supported width: 768px. |

---

## 8. Component Specifications

### StatCard

A compact card displaying a single key metric.

**Structure**:
```
┌──────────────────────────┐
│  📊  Listening Accuracy  │  ← Icon (20px) + Label (12px, secondary)
│                          │
│         72.5%            │  ← Value (28px, bold, primary)
│                          │
│     ↑ 2.5% from last     │  ← Trend indicator (12px, optional)
└──────────────────────────┘
```

**Specs**:
- Width: flexible (grid column). Min-width: 200px.
- Height: 120px fixed.
- Background: `--bg-surface` (white).
- Border: `--border-light`.
- Border-radius: `--radius-md` (8px).
- Shadow: `--shadow-card`.
- Padding: 20px.
- Icon: 20px, colored per context (blue for sessions, green for accuracy, amber for vocabulary).
- Trend indicator (optional): small arrow + percentage, green for positive, red for negative.

**States**:
- Default: as above.
- Loading: shimmer/skeleton placeholder matching the card dimensions.
- Empty (no data): shows "--" instead of value.

**Grid layout**:
- Desktop (>=1024px): 4 columns.
- Tablet (768-1023px): 2 columns.
- Cards use CSS Grid with `grid-template-columns: repeat(auto-fit, minmax(200px, 1fr))` and `gap: 16px`.

---

### PageHeader

Consistent header at the top of every content page.

**Structure**:
```
┌─────────────────────────────────────────────────────────┐
│  Dashboard                                    [+ New]   │
│  Overview of your CET preparation progress              │
└─────────────────────────────────────────────────────────┘
```

**Specs**:
- Height: auto (fits content).
- Margin-bottom: 24px.
- Title: 24px, bold, `--color-text-primary`.
- Description: 14px, `--color-text-secondary`, below title with 4px gap.
- Action button (optional): Right-aligned, primary button style.

---

### SectionCard

A card used to group related content on detail pages.

```
┌─────────────────────────────────────────┐
│  Listening Results          [Edit]      │  ← Header row
│                                         │
│  Content goes here...                   │  ← Body
│                                         │
└─────────────────────────────────────────┘
```

**Specs**:
- Background: white.
- Border-radius: `--radius-md`.
- Shadow: `--shadow-card`.
- Padding: 20px.
- Header: 16px, medium weight, `--color-text-primary`, with optional action link/button right-aligned.
- Divider: Optional `--border-light` between header and body when header exists.
- Margin-bottom: 24px (when stacked).

---

### StatusTag

Small colored tag/label for categorical data.

**Specs**:
- Display: inline-flex, align-items center.
- Padding: 2px 8px.
- Font-size: 12px, medium weight.
- Border-radius: `--radius-sm` (4px).
- Semi-transparent background based on the semantic color (e.g., `--color-primary-50` background, `--color-primary-600` text).

**Variants**:

| Tag Type | Background | Text Color | Example |
|----------|------------|------------|---------|
| exam_type (CET4/CET6) | `--color-primary-50` | `--color-primary-600` | "CET4", "CET6" |
| session_type | `--color-info-50` | `--color-info-600` | "Full Mock", "Listening" |
| familiarity: mastered | `--color-success-50` | `--color-success-600` | "Mastered" |
| familiarity: learning | `--color-warning-50` | `--color-warning-600` | "Learning" |
| familiarity: familiar | `--color-primary-50` | `--color-primary-600` | "Familiar" |
| familiarity: new | `--color-info-50` | `--color-info-600` | "New" |
| accuracy: high (>=80%) | `--color-success-50` | `--color-success-600` | "80%" |
| accuracy: medium (60-80%) | `--color-warning-50` | `--color-warning-600` | "72%" |
| accuracy: low (<60%) | `--color-danger-50` | `--color-danger-600` | "45%" |
| entry_type | `--color-gray-100` | `--color-gray-600` | "word", "phrase" |

---

### EmptyState

Centered placeholder shown when a list or dashboard has no data.

**Structure**:
```
┌──────────────────────────────────────────┐
│                                          │
│              [Icon / SVG]                │  ← 64px simple line-art illustration
│                                          │
│        No practice sessions yet          │  ← 18px, semibold, text-primary
│                                          │
│   Start tracking your CET preparation    │  ← 14px, text-secondary
│   by creating your first session.        │
│                                          │
│          [ Create First Session ]        │  ← Primary button
│                                          │
└──────────────────────────────────────────┘
```

**Specs**:
- Centered vertically and horizontally in the content area.
- Max-width: 400px.
- Icon: 64px, simple line-art SVG using `--color-gray-300`. Different icon per context (book for sessions, chart for dashboard, document for vocabulary).
- Title: 18px, semibold.
- Description: 14px, `--color-text-secondary`, max 2 lines.
- CTA button: Primary style, 24px below description.
- Overall vertical padding: 80px from top of content area.

**Contextual variants**:

| Page | Title | Description | CTA |
|------|-------|-------------|-----|
| Dashboard | "Start your CET preparation journey" | "Create a practice session or import vocabulary to begin tracking your progress." | "Create First Session" |
| Sessions list | "No practice sessions yet" | "Record your first mock exam or sectional practice to start tracking your CET preparation." | "New Session" |
| Session detail (no results) | "No results recorded" | "Record your listening or reading results for this session." | "Record Results" |
| Vocabulary list | "No vocabulary notes yet" | "Import vocabulary from Markdown notes to build your personal word bank." | "Import Vocabulary" |
| Review | "Nothing to review" | "All vocabulary entries are mastered. Import new vocabulary to continue." | "Import Vocabulary" |

---

### ConfirmDialog

Wrapper around Element Plus `ElMessageBox.confirm`.

**Specs**:
- Title: 18px, semibold.
- Body: 14px, `--color-text-secondary`.
- Confirm button: Danger color (red) for destructive actions, Primary (blue) for non-destructive.
- Cancel button: Default style (gray outline).

**Usage contexts**:
- Delete session → "Are you sure you want to delete this session? All associated results will also be deleted. This cannot be undone."
- Delete vocabulary note → "Are you sure you want to delete this vocabulary note? All {n} entries will also be deleted."
- Import data → "This will replace ALL existing data with the imported file. This cannot be undone. Continue?"

---

## 9. Page Design Specifications

### Dashboard (Landing Page)

**Row 1 — Stat Cards (4 cards)**:
```
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Sessions │ │Listening │ │ Reading  │ │  Vocab   │
│   12     │ │  72.5%   │ │  68.3%   │ │   150    │
│ +3 this  │ │ ↑ 2.5%   │ │ ↓ 1.2%   │ │ 45 new   │
│  week    │ │           │ │           │ │           │
└──────────┘ └──────────┘ └──────────┘ └──────────┘
```

**Row 2 — Trend Charts (2 columns)**:
```
┌───────────────────────────┐ ┌───────────────────────────┐
│  Listening Accuracy Trend │ │  Reading Accuracy Trend   │
│  (Line chart)             │ │  (Line chart)             │
│                           │ │                           │
│   · · ·                   │ │   · · ·                   │
│  ·     ·                  │ │  ·     ·                  │
│ ·       ·──               │ │ ·       ·──               │
│                           │ │                           │
│  Last 10 sessions         │ │  By question type         │
└───────────────────────────┘ └───────────────────────────┘
```

Charts use ECharts or similar library. Styled to match the application color palette. Line color: `--color-primary-500`. Grid lines: `--color-gray-200`. Tooltip on hover. Responsive resizing.

**Row 3 — Recent Sessions + Vocabulary (2 columns)**:
```
┌───────────────────────────┐ ┌───────────────────────────┐
│  Recent Sessions          │ │  Vocabulary Mastery       │
│                           │ │                           │
│  ┌─────────────────────┐  │ │     ┌───────┐            │
│  │ 2024年12月真题卷2   │  │ │     │ Donut │  Pending:  │
│  │ CET4 · Full Mock    │  │ │     │ Chart │   105      │
│  │ L: 75% · R: 72%     │  │ │     └───────┘            │
│  └─────────────────────┘  │ │                           │
│  ┌─────────────────────┐  │ │  New: 60   Learning: 45  │
│  │ 2024年12月真题卷1   │  │ │  Familiar: 30  Mastered:15│
│  │ CET4 · Listening    │  │ │                           │
│  │ L: 70%              │  │ │  [ Start Review ]         │
│  └─────────────────────┘  │ │                           │
│  View all →               │ │                           │
└───────────────────────────┘ └───────────────────────────┘
```

- Recent sessions: list of up to 5 compact cards. Each shows paper name, exam type + session type tags, date, accuracy summary. "View all" link at bottom navigates to Sessions page.
- Vocabulary donut chart: 4 segments (new=info blue, learning=warning amber, familiar=primary blue-indigo, mastered=success green). Center shows pending review count. Legend below with color + label + count. "Start Review" button navigates to Review page if pending > 0.

---

### Sessions List Page

**Filter Bar**:
```
┌─────────────────────────────────────────────────────────┐
│  [CET4 ▾]  [All types ▾]                     [+ New]   │
└─────────────────────────────────────────────────────────┘
```
- Exam type dropdown: All / CET4 / CET6.
- Session type dropdown: All / Full Mock / Listening / Reading / Writing / Translation.
- "New Session" button: Primary, right-aligned.

**Session Cards (vertical list)**:
```
┌─────────────────────────────────────────────────────────┐
│  CET4  Full Mock                          2025-03-15    │
│  2024年6月真题卷1                                       │
│  ⏱ 130 min  ·  📝 Has results (L: 72% · R: 68%)       │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│  CET4  Listening                           2025-03-22   │
│  2024年12月真题卷1                                      │
│  ⏱ 30 min  ·  📝 L: 75%                               │
└─────────────────────────────────────────────────────────┘
```

Each card:
- StatusTag badges: exam_type (left, primary), session_type (left, info).
- Paper name: 16px, medium, text-primary. Truncated to 1 line.
- Date: 12px, text-secondary, right-aligned on same row.
- Meta row: duration (if present), result summary (if results exist). 12px, text-secondary.
- Divider: `--border-light` between cards.
- Padding: 16px.
- Hover: shadow lifts to `--shadow-card-hover`, cursor pointer.
- Click: navigates to session detail page.

---

### Session Detail Page

**Header**:
```
← Back to Sessions

2024年6月真题卷1
CET4 · Full Mock · 2025-03-15
```

**Session Info Card** (top section):
```
┌──────────────────────────────────────────────────┐
│  Session Info                                    │
│                                                  │
│  Paper:    2024年6月真题卷1                      │
│  Type:     Full Mock                             │
│  Exam:     CET4                                  │
│  Date:     March 15, 2025                        │
│  Duration: 130 minutes                           │
│  Notes:    First full mock attempt. Felt         │
│            rushed on the reading section.        │
└──────────────────────────────────────────────────┘
```

**Listening Section**:
```
┌──────────────────────────────────────────────────┐
│  Listening Results                    [Edit]     │
│                                                  │
│  ┌────────────────────────┐                      │
│  │                        │  Accuracy            │
│  │     ● 72%              │  18 / 25 correct     │
│  │   (progress ring)      │                      │
│  └────────────────────────┘                      │
│                                                  │
│  Wrong Questions:  1  5  8  12  15              │
│  (rendered as small tag/chips, each clickable    │
│   to show its mistake tags in a tooltip)         │
│                                                  │
│  Reflection:                                     │
│  Need to improve concentration during long       │
│  passages. Missed several keywords.              │
└──────────────────────────────────────────────────┘
```

**Reading Sections** (one card per question_type):
```
┌──────────────────────────────────────────────────┐
│  仔细阅读                            [Edit]     │
│  ┌────────────────────────┐                      │
│  │     ● 70%              │  7 / 10 correct     │
│  └────────────────────────┘                      │
│  Wrong: 3  7  9                                  │
│  Reflection: Careless with inference questions.  │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  选词填空                            [Edit]     │
│  Accuracy: 60% (6/10)                            │
│  Wrong: 2  4  6  10                              │
│  Reflection: Vocabulary gap is the main issue.   │
└──────────────────────────────────────────────────┘
```

**Recording/Editing Form** (when "Edit" or "Record Result" is clicked, replaces the display card):
```
┌──────────────────────────────────────────────────┐
│  Recording Listening Result                      │
│                                                  │
│  Total Questions:  [25    ]                      │
│  Correct Count:    [18    ]                      │
│  Wrong Questions:  [1,5,8,12,15            ]     │
│  (comma-separated)                               │
│                                                  │
│  Mistake Tags:                                   │
│    Q1: [关键词没抓住 ▾] (multi-select)           │
│    Q5: [单词不认识 ▾]                            │
│    [+ Add question]                              │
│                                                  │
│  Reflection:                                     │
│  [                                  ]            │
│  [                                  ]            │
│                                                  │
│  [Cancel]  [Save]                                │
└──────────────────────────────────────────────────┘
```

**Associated Vocabulary** (bottom section):
```
┌──────────────────────────────────────────────────┐
│  Vocabulary Notes                                │
│                                                  │
│  ┌────────────────────────────────────┐          │
│  │ 2024年6月真题卷1 阅读词汇          │          │
│  │ 25 entries · Created Mar 16        │          │
│  └────────────────────────────────────┘          │
│                                                  │
│  If none: "No vocabulary imported from this      │
│            session yet." [+ Import Vocabulary]   │
└──────────────────────────────────────────────────┘
```

---

### Vocabulary List Page

**Grid/List of Note Cards**:
```
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│ CET4  Reading     │ │ CET4  Listening   │ │ CET6  Reading     │
│                   │ │                   │ │                   │
│ 2024年6月真题卷1  │ │ 2024年12月真题卷1 │ │ 2023年6月真题卷2  │
│ 阅读词汇          │ │ 听力词汇          │ │ 阅读词汇          │
│                   │ │                   │ │                   │
│ 25 entries        │ │ 18 entries        │ │ 32 entries        │
│ Mar 16, 2025      │ │ Mar 23, 2025      │ │ Mar 30, 2025      │
└───────────────────┘ └───────────────────┘ └───────────────────┘
```

- Grid: 3 columns on desktop, 2 on tablet, 1 on mobile.
- Each card: `--shadow-card`, hover lifts.
- "Import Vocabulary" button: Fixed at top right or inline in the empty state.

---

### Vocabulary Import Page/Modal

```
┌──────────────────────────────────────────────────┐
│  Import Vocabulary                               │
│                                                  │
│  Title *                                         │
│  [2024年6月真题卷1 阅读词汇                ]     │
│                                                  │
│  Source Session (optional)                       │
│  [Select a session... ▾]                         │
│                                                  │
│  Source Section *                                │
│  [Reading ▾]                                     │
│                                                  │
│  Markdown Content *                              │
│  ┌────────────────────────────────────────┐      │
│  │ ## 1. pending                          │      │
│  │                                        │      │
│  │ ### 释义                                │      │
│  │ 等待处理的；悬而未决的                   │      │
│  │                                        │      │
│  │ ### 例句                                │      │
│  │ - The case is still pending. — ...     │      │
│  │                                        │      │
│  └────────────────────────────────────────┘      │
│                                                  │
│  [Preview]  [Cancel]  [Save]                     │
└──────────────────────────────────────────────────┘
```

**Preview result** (shown below the form after clicking Preview):
```
┌──────────────────────────────────────────────────┐
│  Preview: 2 entries found                        │
│                                                  │
│  Entry 1: "pending" — 3 meanings, 2 usages       │
│  Entry 2: "sustainable" — 2 meanings, 1 example  │
│                                                  │
│  If empty: "No entries could be parsed. Check    │
│             the Markdown format and try again.   │
│             The note will still be saved."       │
└──────────────────────────────────────────────────┘
```

**Instructions** (shown persistently above the textarea in a collapsible info box):
- Supported headings: `## <number>. <term>`, `### 释义`, `### 常见用法`, `### 例句`, `### 易错点`, `### 同义替换`, `### 易混词对比`, `### 写作可用句`
- Use `- ` for list items, `English — Chinese` for examples
- See the full format guide for details

---

### Vocabulary Detail Page (KEY PAGE — Most Polished)

This is the showcase page of the application. Every vocabulary entry is a beautifully designed card.

**Page Header**:
```
← Back to Vocabulary

2024年6月真题卷1 阅读词汇
CET4 · Reading · 25 entries · Created Mar 16, 2025

[▸ View Raw Markdown]  (collapsible, shows raw Markdown in a code block)
```

**Entry Cards** (rendered for each vocabulary_entry):

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  pending                        [ word ]  [ new ▾ ]  │   │
│  │                                                      │   │
│  │  ┌──────────────────────────────────────────────┐    │   │
│  │  │ 📖 释义                                       │    │   │
│  │  │                                              │    │   │
│  │  │ 等待处理的；悬而未决的；即将发生的              │    │   │
│  │  └──────────────────────────────────────────────┘    │   │
│  │                                                      │   │
│  │  📎 常见用法                                         │   │
│  │  ┌──────────────┐ ┌──────────────────┐              │   │
│  │  │ pending      │ │ pending approval │              │   │
│  │  │ decision     │ │                  │              │   │
│  │  └──────────────┘ └──────────────────┘              │   │
│  │  ┌──────────────────┐                               │   │
│  │  │ patent pending   │                               │   │
│  │  └──────────────────┘                               │   │
│  │                                                      │   │
│  │  💬 例句                                             │   │
│  │  ┌──────────────────────────────────────────────┐    │   │
│  │  │ The case is still pending.                   │    │   │
│  │  │ 案件仍在审理中。                               │    │   │
│  │  └──────────────────────────────────────────────┘    │   │
│  │  ┌──────────────────────────────────────────────┐    │   │
│  │  │ A final decision is pending.                 │    │   │
│  │  │ 最终决定尚未作出。                             │    │   │
│  │  └──────────────────────────────────────────────┘    │   │
│  │                                                      │   │
│  │  ⚠️ 易错点                                           │   │
│  │  ┌──────────────────────────────────────────────┐    │   │
│  │  │ ⚠ 不是"悬挂"的意思（那是 suspend）             │    │   │
│  │  │ ⚠ pending 常放在名词后面，不是前面             │    │   │
│  │  └──────────────────────────────────────────────┘    │   │
│  │  (warning-colored: amber-50 background,              │   │
│  │   amber-600 left border accent)                      │   │
│  │                                                      │   │
│  │  🔄 同义替换                                         │   │
│  │  ┌──────┐ ┌──────┐ ┌──────────┐ ┌────────┐         │   │
│  │  │await-│ │unde- │ │unresolved│ │imminent│         │   │
│  │  │ ing  │ │cided │ │          │ │        │         │   │
│  │  └──────┘ └──────┘ └──────────┘ └────────┘         │   │
│  │  (info-colored tag chips)                            │   │
│  │                                                      │   │
│  │  🔀 易混词对比                                       │   │
│  │  ┌───────────────────┐ ┌───────────────────┐        │   │
│  │  │ pending           │ │ impending         │        │   │
│  │  │ 等待决定/处理     │ │ 即将发生          │        │   │
│  │  │ （中性）          │ │ （通常不好）      │        │   │
│  │  └───────────────────┘ └───────────────────┘        │   │
│  │  (Two side-by-side comparison cards, light gray      │   │
│  │   background, subtle left border accent per card)    │   │
│  │                                                      │   │
│  │  ✍️ 写作可用句                                       │   │
│  │  ┌──────────────────────────────────────────────┐    │   │
│  │  │ ❝ With the final exam pending, students      │    │   │
│  │  │   are under increasing pressure. ❞           │    │   │
│  │  └──────────────────────────────────────────────┘    │   │
│  │  ┌──────────────────────────────────────────────┐    │   │
│  │  │ ❝ The proposal is still pending approval     │    │   │
│  │  │   from the committee. ❞                     │    │   │
│  │  └──────────────────────────────────────────────┘    │   │
│  │  (Special card with left quote-bar decoration,       │   │
│  │   italic English text, slightly muted background)    │   │
│  │                                                      │   │
│  │  Reviewed: 3 times · Last: Mar 20, 2025              │   │
│  │  (small metadata footer, 12px, text-secondary)       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Entry card design rules**:
1. Card header: term (22px, bold) + entry_type badge + familiarity dropdown (right-aligned).
2. Meanings section: distinct tinted background (primary-50), full width, slightly inset.
3. Usages: tag chips (gray-100 background, gray-700 text, 4px radius).
4. Examples: Each example is a two-line block. English line in italic (14px). Chinese line below (12px, text-secondary).
5. Mistake tips: Warning-colored alert box. Amber-50 background, amber-600 left border (3px), warning icon.
6. Synonyms: Small info-colored tag chips.
7. Comparisons: Two side-by-side cards, each with `--border-light`, gray-50 background, 8px radius, 12px padding.
8. Writing sentences: Special card with a left decorative bar (primary-400, 3px), italic English text, slightly muted background (primary-50).
9. Empty sections are simply not rendered (no "no data" placeholder).
10. Footer: review metadata in small text.

**Familiarity selector**: Element Plus dropdown, compact. Options: New / Learning / Familiar / Mastered. Changing the value sends a PUT request immediately.

---

### Vocabulary Review Page

**Simple Flashcard Mode**:

```
┌──────────────────────────────────────────────────┐
│  Review Mode                                     │
│                                                  │
│  Filter: [All ▾]  [New ▾]  [Learning ▾]          │
│                                                  │
│  Card 3 of 45                                    │
│                                                  │
│  ┌────────────────────────────────────────┐      │
│  │                                        │      │
│  │                                        │      │
│  │            sustainable                 │      │
│  │                                        │      │
│  │        (click to reveal)               │      │
│  │                                        │      │
│  └────────────────────────────────────────┘      │
│                                                  │
│  After reveal:                                   │
│  ┌────────────────────────────────────────┐      │
│  │            sustainable                 │      │
│  │                                        │      │
│  │  可持续的；能维持的                      │      │
│  │                                        │      │
│  │  sustainable development 可持续发展     │      │
│  │                                        │      │
│  │  [← Back]  [Mark Familiar]  [Mastered] │      │
│  └────────────────────────────────────────┘      │
│                                                  │
└──────────────────────────────────────────────────┘
```

- Filter row: Familiarity filter chips. All / New / Learning (Familiar and Mastered are excluded from review by default).
- Card: Large, centered. Term in 28px bold. On click, reveals meanings and examples below with a smooth transition.
- Actions: "Mark Familiar" (warning button), "Mastered" (success button), "Back" (skip, primary outline).
- Progress: "Card 3 of 45" with a thin progress bar below.
- After reviewing all cards, show: "All done! 12 marked familiar, 8 mastered today."

---

### Settings Page

```
┌──────────────────────────────────────────────────┐
│  Settings                                        │
│                                                  │
│  ┌────────────────────────────────────────┐      │
│  │  Export Data                           │      │
│  │                                        │      │
│  │  Download all your data as a JSON      │      │
│  │  file. Use this to back up your        │      │
│  │  progress or transfer to another       │      │
│  │  device.                                │      │
│  │                                        │      │
│  │  [Export JSON]                         │      │
│  └────────────────────────────────────────┘      │
│                                                  │
│  ┌────────────────────────────────────────┐      │
│  │  Import Data                           │      │
│  │                                        │      │
│  │  Restore data from a previously        │      │
│  │  exported JSON file.                   │      │
│  │  ⚠️ This will replace ALL existing     │      │
│  │    data.                                │      │
│  │                                        │      │
│  │  [Choose File] selected-file.json      │      │
│  │                                        │      │
│  │  Preview: 12 sessions, 8 listening,    │      │
│  │  15 reading, 5 vocab notes, 150 entries│      │
│  │                                        │      │
│  │  [Import Data]  (disabled if no file)  │      │
│  └────────────────────────────────────────┘      │
│                                                  │
│  ┌────────────────────────────────────────┐      │
│  │  About                                 │      │
│  │                                        │      │
│  │  CET Tracker v1.0.0                    │      │
│  │  Local-first CET preparation tracker   │      │
│  │  Database: SQLite                      │      │
│  │  Backend: FastAPI + SQLModel           │      │
│  │  Frontend: Vue 3 + Element Plus        │      │
│  └────────────────────────────────────────┘      │
└──────────────────────────────────────────────────┘
```

- Export: "Export JSON" button triggers download.
- Import: File input. On file select, read and validate the JSON, show preview counts, enable the "Import" button. On click, show ConfirmDialog, then on confirm, POST to `/api/import/json`, show success message.
- About: Static info card.

---

## 10. State Design

### Loading State
- **Lists/Cards**: Element Plus `v-loading` directive with skeleton-like shimmer. Alternatively, render card-shaped placeholder blocks with animated gradient.
- **Charts**: Show a centered spinner in the chart container with a "Loading chart data..." label.
- **Buttons after click**: Disable the button and show a spinner inside it (Element Plus `loading` prop on `el-button`).
- **Page transitions**: No artificial loading spinners on page navigation (SPA router is instantaneous). Loading indicators only for data fetches.

### Empty State
- Use the **EmptyState** component as specified in section 8.
- Empty state always includes a contextual CTA, never just a message.
- Charts in empty state: Parent card shows "No data yet" with a simplified chart placeholder (faded grid lines, no data) and text "Complete a practice session to see trends."

### Error State
- **API errors**: Element Plus `ElMessage.error(message)` toast at top-center, auto-dismiss after 5 seconds. Message is the `error` field from the API response envelope.
- **Network errors**: "Unable to connect to the server. Please check that the application is running." with a "Retry" button.
- **Validation errors**: Inline form field errors (red text below the input), using Element Plus form validation.
- **Import failures**: Specific error message in a visible alert box (not a toast), since import is a consequential action. Include details about what went wrong (e.g., "Invalid JSON format" or "Missing required key: sessions").

### Success State
- **Save/Create/Update**: Element Plus `ElMessage.success("Session created successfully")`, green, auto-dismiss 3 seconds.
- **Delete**: `ElMessage.success("Session deleted")`, auto-dismiss 3 seconds.
- **Import**: Show a detailed success message with counts: `ElMessage.success("Imported: 12 sessions, 8 listening results, 15 reading results, 5 vocabulary notes, 150 entries")`.
- **Export**: Browser handles the download; show "Data exported successfully".

### Form State
- **Dirty detection**: Not implemented in MVP. Users rely on the save button. (Simple and sufficient for a local app.)
- **Unsaved changes warning**: Not implemented in MVP.
- **Optimistic updates**: Not implemented. All mutations are confirmed with server response before UI updates.

---

## 11. Responsive Design

### Breakpoint System

| Breakpoint | Width | Name | Behavior |
|------------|-------|------|----------|
| Desktop | >= 1024px | `lg` | Full layout |
| Tablet | 768px - 1023px | `md` | Collapsed sidebar, reduced columns |
| Mobile | < 768px | `sm` | Not primary target. Degrade gracefully. |

### Sidebar
- >= 1024px: Full width (220px), icons + text labels.
- 768px-1023px: Collapsed to icon-only (56px). Icons remain, labels are hidden. Tooltip on hover to reveal item name. Brand area shows only the logo icon.
- < 768px: Sidebar becomes a top navigation bar (48px height, horizontal scrollable tabs).

### StatCards Grid
- >= 1024px: 4 columns (`grid-template-columns: repeat(4, 1fr)`).
- 768px-1023px: 2 columns.
- < 768px: 1 column (full width).

### Two-Column Layouts (Dashboard rows 2 & 3, Session Detail)
- >= 1024px: Side by side, 24px gap.
- < 1024px: Stack vertically, 24px gap between stacked items.

### Vocabulary Note Cards
- >= 1024px: 3 columns.
- 768px-1023px: 2 columns.
- < 768px: 1 column.

### Charts
- Resize responsively using container queries or ResizeObserver.
- Chart labels and axis text reduce in size on smaller containers.

### Typography
- Font sizes remain constant across breakpoints. The scale is already accessible.
- Line lengths naturally constrain within the max-width: 1200px container.

### Minimum Supported Width
The application is designed primarily for laptop/desktop use. The minimum supported viewport width is **768px** (common laptop resolution). Below 768px, layout degrades gracefully but some components may require horizontal scrolling or simplified presentation.

---

## 12. Iconography

Use a consistent icon set. Recommended: **Heroicons** (MIT licensed, 20px and 24px solid/outline variants) or Element Plus Icons.

| Context | Icon |
|---------|------|
| Dashboard nav | `chart-bar` or `presentation-chart` |
| Sessions nav | `document-text` or `book-open` |
| Vocabulary nav | `bookmark` or `collection` |
| Review nav | `refresh` or `academic-cap` |
| Settings nav | `cog` or `adjustments` |
| CET4 tag | Use text, no icon needed |
| CET6 tag | Use text, no icon needed |
| Listening | `headphones` or `volume-up` |
| Reading | `book-open` or `eye` |
| Writing | `pencil` or `pencil-alt` |
| Translation | `translate` or `language` |
| Familiarity: new | `sparkles` or `star` |
| Familiarity: learning | `light-bulb` |
| Familiarity: familiar | `check` |
| Familiarity: mastered | `badge-check` or `shield-check` |
| Delete | `trash` |
| Edit | `pencil` |
| Export | `download` |
| Import | `upload` |
| Preview | `eye` |
| Empty state | Contextual: `document-add` for no sessions, `bookmark` for no vocabulary |
| Search | `search` or `filter` |
