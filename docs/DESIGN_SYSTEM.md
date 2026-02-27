# Antigravity Workspace Design System (Pro Max)

## Core Philosophy

- **Modern & Professional**: Clean lines, glassmorphism accents, purpose-built for developers.
- **Dark Mode First**: Optimized for long coding sessions, high contrast where it matters.
- **Fluid & Responsive**: Adapts seamlessly from desktop to tablet.
- **Micro-Interactions**: Subtle feedback on hover/click to enhance perceived responsiveness.

## Color Palette

### Backgrounds

- `bg-primary`: `#0f172a` (Slate 900) - Main application background
- `bg-secondary`: `#1e293b` (Slate 800) - Panels, sidebars, cards
- `bg-tertiary`: `#334155` (Slate 700) - Input fields, active states, borders
- `bg-glass`: `rgba(30, 41, 59, 0.7)` - Floating elements, headers (requires backdrop-filter)

### Text

- `text-primary`: `#f8fafc` (Slate 50) - Headings, main content
- `text-secondary`: `#94a3b8` (Slate 400) - Metadata, labels, descriptions
- `text-muted`: `#64748b` (Slate 500) - Disabled states, placeholders
- `text-accent`: `#3b82f6` (Blue 500) - Links, interactive text

### Accents & Status

- `accent-primary`: `#3b82f6` (Blue 500) - Primary actions, focus rings
- `accent-secondary`: `#8b5cf6` (Violet 500) - Secondary actions, creative elements
- `status-success`: `#10b981` (Emerald 500) - Online, connected, success
- `status-warning`: `#f59e0b` (Amber 500) - Loading, warnings
- `status-error`: `#ef4444` (Red 500) - Offline, errors, critical alerts

### Gradients

- `gradient-primary`: `linear-gradient(135deg, #3b82f6, #8b5cf6)` - Buttons, logos, active tabs
- `gradient-subtle`: `radial-gradient(circle at top right, rgba(59, 130, 246, 0.1), transparent)` - Background nuance

## Typography

### Font Stack

- **Headings/UI**: `Inter`, system-ui, sans-serif
- **Code/Terminal**: `JetBrains Mono`, Fira Code, monospace

### Scale

- `text-xs`: 0.75rem (12px) - Badges, tiny labels
- `text-sm`: 0.875rem (14px) - UI text, buttons
- `text-base`: 1rem (16px) - Body text, chat messages
- `text-lg`: 1.125rem (18px) - Section headers
- `text-xl`: 1.25rem (20px) - Panel titles
- `text-2xl`: 1.5rem (24px) - Main headers

## Components

### Buttons

- **Primary**: Gradient background, white text, slightly rounded corners (8px). Hover: brightens + slight lift.
- **Secondary**: `bg-tertiary`, `text-secondary`. Hover: `bg-secondary` + `text-primary`.
- **Icon Button**: Transparent background, `text-secondary`. Hover: `bg-tertiary` + `text-primary`.

### Cards & Panels

- **Base Card**: `bg-secondary`, `border-color` (rgba(255,255,255,0.08)), rounded-xl (12px).
- **Glass Card**: `bg-glass`, backdrop-blur-md, border-white/10.

### Inputs

- **Text Input**: `bg-tertiary`, `border-color`, rounded-lg. Focus: `border-accent-primary`, ring-2 ring-accent/20.
- **Chat Input**: Floating bar, glass effect, distinct from content.

### Navigation (Tabs)

- **Container**: `bg-primary`, bottom border.
- **Tab Item**: `text-secondary`, padding-x 4, padding-y 2.
- **Active Tab**: `text-primary`, bottom border `accent-primary` (2px). Hover: `text-primary` (transition).

## Windows Experience

### Window Controls

- **Title Bar**: Custom drawn, seamless integration with app header.
- **Traffic Lights (Mac) / Controls (Win)**: Properly spaced, consistent with OS native look but styled.

### Native Integration

- **PyWebView**: Check backend/GUI bridge for native file dialogs, notifications, and system resource hooks.
