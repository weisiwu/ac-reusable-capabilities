---
name: "AC Lab / AC 能力库"
description: "A restrained document system for finding, operating, and understanding reusable capabilities."
colors:
  primary: "#2457d6"
  ink: "#202939"
  muted: "#59677d"
  paper: "#fff"
  surface: "#f5f7fb"
  line: "#dfe4ed"
  control-line: "#bac5d6"
  selected: "#e5edff"
  success-ink: "#1d6140"
  success-surface: "#eff8f2"
  error-ink: "#9c3535"
  error-surface: "#fdf1f1"
  warning-ink: "#7e530f"
  warning-surface: "#fff9ea"
typography:
  headline:
    fontFamily: "-apple-system, BlinkMacSystemFont, \"Segoe UI\", \"PingFang SC\", \"Microsoft YaHei\", sans-serif"
    fontSize: "30px"
    fontWeight: 700
    lineHeight: 1.4
    letterSpacing: "-0.025em"
  page-title:
    fontFamily: "-apple-system, BlinkMacSystemFont, \"Segoe UI\", \"PingFang SC\", \"Microsoft YaHei\", sans-serif"
    fontSize: "2rem"
    fontWeight: 650
    lineHeight: 1.35
    letterSpacing: "-0.025em"
  section-title:
    fontFamily: "-apple-system, BlinkMacSystemFont, \"Segoe UI\", \"PingFang SC\", \"Microsoft YaHei\", sans-serif"
    fontSize: "22px"
    fontWeight: 650
    lineHeight: 1.5
    letterSpacing: "-0.015em"
  subsection-title:
    fontFamily: "-apple-system, BlinkMacSystemFont, \"Segoe UI\", \"PingFang SC\", \"Microsoft YaHei\", sans-serif"
    fontSize: "18px"
    fontWeight: 650
    lineHeight: 1.5
  group-title:
    fontFamily: "-apple-system, BlinkMacSystemFont, \"Segoe UI\", \"PingFang SC\", \"Microsoft YaHei\", sans-serif"
    fontSize: "16px"
    fontWeight: 650
    lineHeight: 1.5
  body:
    fontFamily: "-apple-system, BlinkMacSystemFont, \"Segoe UI\", \"PingFang SC\", \"Microsoft YaHei\", sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.75
  dense-body:
    fontFamily: "-apple-system, BlinkMacSystemFont, \"Segoe UI\", \"PingFang SC\", \"Microsoft YaHei\", sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.65
  action:
    fontFamily: "-apple-system, BlinkMacSystemFont, \"Segoe UI\", \"PingFang SC\", \"Microsoft YaHei\", sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "-apple-system, BlinkMacSystemFont, \"Segoe UI\", \"PingFang SC\", \"Microsoft YaHei\", sans-serif"
    fontSize: "12px"
    fontWeight: 600
    lineHeight: 1.6
  code:
    fontFamily: "ui-monospace, SFMono-Regular, Consolas, monospace"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.7
rounded:
  inline-code: "3px"
  badge: "4px"
  app-navigation: "5px"
  control: "6px"
  result: "8px"
spacing:
  "4": "4px"
  "6": "6px"
  "8": "8px"
  "12": "12px"
  "16": "16px"
  "20": "20px"
  "24": "24px"
  "28": "28px"
  "32": "32px"
  "36": "36px"
  "40": "40px"
  "48": "48px"
  "56": "56px"
  "64": "64px"
  "72": "72px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.paper}"
    typography: "{typography.action}"
    rounded: "{rounded.control}"
    padding: "8px 12px"
  button-secondary:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.action}"
    rounded: "{rounded.control}"
    padding: "8px 12px"
  search-field:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "8px 12px"
  sidebar-navigation:
    textColor: "{colors.ink}"
    rounded: "{rounded.app-navigation}"
    padding: "6px 10px"
  state-badge:
    textColor: "{colors.muted}"
    rounded: "{rounded.badge}"
    padding: "2px 6px"
  result-surface:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.result}"
    padding: "20px"
  status-message:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.muted}"
    rounded: "{rounded.control}"
    padding: "10px 12px"
---

# Design System: AC Lab / AC 能力库

## Overview

**Creative North Star: "The Technical Standards Index"**

AC Lab uses the order of a technical standards index: aligned entries, clear grouping, quiet navigation, and a direct path from a capability to its example or documentation. White is the working page; pale blue-gray separates navigation and results; a single blue identifies links, the current location, and primary actions.

Reading and operating share colors, type, controls, and navigation cues. Their layouts follow the task: the catalog is a compact grouped index, an example is a populated work area, and documentation is a narrower reading column with a chapter outline. System sans-serif type is intentional for these Read and Operate modes; no display-face pairing or illustration is required.

**Key Characteristics:**

- Compact hierarchy with explicit groups and dividers.
- Blue for action and location; semantic color for actual state.
- Flat surfaces, restrained corners, and visible keyboard focus.
- Task-specific layouts within one document vocabulary.

This record is extracted from `site/assets/docs.css` and `site/assets/style.css`, with structures and states verified in `site/index.html`, `site/assets/app.mjs`, `site/assets/docs.js`, and `site/docs_build.py`. The brand commitment comes from `PRODUCT.md`; the implemented artifact is the authority for the values below.

## Colors

The palette is cool, legible, and mostly neutral. The frontmatter is the normative color reference.

### Primary

- **Working Blue** (`primary`) marks links, primary buttons, checked controls, progress, keyboard focus, and the active header destination.
- **Selected Blue Wash** (`selected`) supports current documentation navigation; the showcase uses a closely related pale-blue selection surface.

### Neutral

- **Deep Ink** (`ink`) carries headings, labels, and body text.
- **Slate Text** (`muted`) carries summaries, metadata, supporting navigation, and table headings.
- **White Paper** (`paper`) is the page and control background.
- **Navigation Mist** (`surface`) separates side navigation, results, code blocks, and table headings from the page.
- **Quiet Rule** (`line`) separates sections, list entries, and table rows.
- **Control Stroke** (`control-line`) is stronger than a content divider so fields and buttons remain recognizable.

### Semantic state colors

Success green, error red, and warning amber pair an ink token with a light surface token. They appear in text-bearing messages and compact badges; they are not additional brand accents. Informational messages use the existing blue-gray family.

**The Blue Has Work Rule.** Use the primary blue for links, actions, focus, progress, and current position. Semantic green, amber, and red belong to reported states, rather than decoration.

## Typography

**Display and Body Font:** The same platform sans-serif stack, including Segoe UI, PingFang SC, and Microsoft YaHei. This is a document and tool interface, not a display-led identity.

**Code Font:** The platform monospace stack, including SFMono-Regular and Consolas.

**Character:** Compact headings and generous body leading let Chinese explanations, controls, and structured data coexist without a second typographic voice. The root size is (15px), so the showcase page-title token (2rem) resolves to the same size as the desktop documentation headline.

### Hierarchy

- **Headline:** Documentation page title; slightly heavier and more open than an operating title. At the small-document breakpoint it becomes (26px).
- **Page title:** Catalog, example, and scenario title, kept compact with a short gap to the summary.
- **Section and subsection titles:** Documentation hierarchy. On small screens these become (20px) and (17px).
- **Group title:** Catalog grouping, quieter than a page heading but stronger than entry titles (14px, weight 600).
- **Body:** Reading paragraphs and example summaries, using the frontmatter body role. Showcase introductions are bounded at (72ch).
- **Dense body:** Entry summaries, tables, and result content. Entry summaries are bounded at (64ch).
- **Label:** Supporting groups and metadata. Documentation labels and selected links use weight (650) where extra emphasis is needed.
- **Code:** Inline code and documentation blocks. Example textareas and logs use a denser (12px) variant with leading between (1.75) and (1.8).

**The Reading Rhythm Rule.** Use the shared sans-serif family and modest heading hierarchy. Keep supporting metadata smaller and muted, and reserve monospace for code and logs.

## Layout

The shared sticky header is (64px) high. Header content and main layouts align to a maximum site width of (1512px). A desktop left navigation track is (232px), separated from content by one quiet rule.

The showcase uses a two-track layout: navigation and a flexible workspace. Its main padding is (36px 40px 64px), reducing to (32px) at (1120px). Main sections have an inner maximum of (1240px). Catalog groups are separated by (36px); entries have vertical padding (16px), a top divider, and a subordinate documentation action. Entry lists use two columns from (1121px), otherwise one. The search field is bounded at (640px); advanced filters use four tracks and an action, then two tracks at (1120px), then one at (420px).

Examples replace the main content region with the selected capability. The work area is flat; controls, populated content, feedback, and results establish hierarchy. Field grids use two tracks with (16px 20px) gaps, becoming one at (760px). General split work areas become two columns at (1000px); table-and-result layouts use a (2fr / minmax(260px, 1fr)) split from (1280px).

Documentation uses navigation, a central reading region, and a (200px) chapter-outline track. The reading region is capped at (856px) including (48px) padding on each side, yielding a maximum text width of (760px). It starts with (32px) top and (72px) bottom padding. At (1180px) the outline disappears and horizontal reading padding becomes (40px). At (900px), navigation becomes a collapsible full-width section and reading padding becomes (32px). At (600px), reading padding is (24px 20px 56px); the header source link disappears and heading sizes reduce.

Showcase navigation collapses at (760px), independently from documentation. A full-width menu button controls the navigation panel; an open panel is capped at (60dvh). Main padding becomes (28px 20px 56px), then uses (16px) sides at (420px). Toolbars wrap, results use (16px) padding, and action buttons gain a minimum height of (38px). Wide tables and code retain local horizontal scrolling.

The spacing scale is built from small control gaps, medium content gaps, and larger reading-section intervals. Use the frontmatter steps according to purpose; do not force every measured dimension onto a single arithmetic scale.

## Elevation & Depth

Resting content uses no shadows. Pale backgrounds, one-pixel rules, text hierarchy, and whitespace distinguish navigation, data, and results. The shared header remains opaque while sticky. The only authored shadow is the transient showcase toast: (`0 6px 24px #20293924`), which lifts a short-lived message above the workspace.

**The Flat Work Area Rule.** Keep the page and its index rows flat. Distinguish a result region by its pale surface; do not add a new frame around every operation or nest result panels for decoration.

## Shapes

Controls have gently curved corners using the control radius. Inline code is tighter, badges slightly softer, and result surfaces use the larger result radius. Showcase sidebar links use the app-navigation radius; documentation links use the control radius. All are restrained rectangles. List and table rows remain square and are defined by a bottom or top rule rather than individual boxes. SVG arrows and interface icons are small, single-color line marks.

## Components

### Buttons

Compact, labeled controls with a visible stroke. Primary controls use Working Blue and white text; secondary controls use White Paper, Deep Ink, and Control Stroke. Standard padding is the button token. Example actions use the action type role; general shared controls inherit the body size.

Hover darkens primary actions or adds a pale surface and stronger border to secondary controls. Pressed state darkens further. The shipped demo-action blue states and documentation/link blue states differ slightly; the sidecar preserves the actual demo-button states rather than declaring another brand color family. Disabled controls retain their geometry with opacity (.55) and an unavailable cursor.

Every focusable control and link uses an accent outline (2px) with an offset (3px). States change immediately in the shipped styles. Reduced-motion preferences disable transitions, animations, and smooth scrolling; no animated timing scale is established.

### Inputs / Fields

White controls use the same stroke, radius, and padding as buttons, with dark entered text and muted placeholders. Labels sit above fields with a (6px) gap; supporting help is smaller and muted. Catalog search has a minimum height of (40px). Selects use the same vocabulary. Textareas may grow vertically; code-oriented examples use monospace text. Checkbox, radio, and range accents use Working Blue.

### Navigation

The header uses a (20px), weight (750) wordmark, a (14px) destination row, and a blue underline for the current destination. On small screens the wordmark becomes (19px) and destinations (13px). Sidebar navigation is compact (13px), with small muted group labels, a pale hover surface, and a blue-tinted current item. Current location is represented semantically with `aria-current`; example tabs use their selected state. Mobile navigation expands in normal document flow, with labeled controls and Escape returning focus to the trigger.

### Capability entries

An index entry is an aligned row, not a card. A dark, medium-weight title and small SVG arrow lead to the experience; a muted summary sits below; a quieter documentation link sits alongside. Hover turns the destination blue and adds an underline. Group headings and counts establish order without decorative numbering or extra containers.

### Result surfaces / Containers

Results use Navigation Mist, the result radius, and the result-padding token. They have no border or shadow. Nested result content drops its own surface and padding. Lists and metrics inside a result remain compact. This pattern applies to result content, not to every page section.

### Chips / Status

Badges are compact text labels (11px) with a small radius and light fill. Status messages use a full text line (13px), a restrained border, and the control radius. Success, warning, and error colors communicate actual outcomes. A neutral or informational message stays in the blue-gray family. Empty feedback containers do not occupy space.

### Tables and code

Tables use tabular numbers, pale heading rows, quiet horizontal rules, and (10px 12px) cells; narrow screens use (9px 10px). Data does not shrink to fit the screen: it scrolls in its own region. Documentation code blocks use a pale bordered surface and reserve top space for a compact copy button. Inline code has a tighter radius and a light blue-gray background.

## Do's and Don'ts

### Do:

- **Do** retain the common palette, type family, control shapes, focus treatment, and navigation cues across different task layouts.
- **Do** keep catalog entries aligned and separated by rules, with summaries and documentation links subordinate to the capability title.
- **Do** give documentation a bounded reading column, while allowing operational tables and result areas to use the available workspace.
- **Do** expose actual selected, disabled, success, warning, and error states with text as well as their visual treatment.
- **Do** preserve horizontal scrolling for wide tables and code, and collapse navigation at the breakpoint for its own task layout.

### Don't:

- **Don't** turn the shared visual vocabulary into a requirement that the catalog, examples, and documentation use an identical shell or content width.
- **Don't** replace the grouped index with nested promotional cards or add shadows to resting content surfaces.
- **Don't** introduce a separate display font, decorative color family, or animated reveal without an approved system change.
- **Don't** hide keyboard focus, rely on color alone for status, or shrink code and table columns merely to force them into a narrow viewport.
