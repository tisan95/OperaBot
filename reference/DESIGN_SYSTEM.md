# OperaBot Design System v1.0

## 🎨 Color Palette

### Primary Colors
- **Indigo-600** `#4f46e5` - Primary CTAs, links, and interactive elements
- **Indigo-700** `#4338ca` - Hover states
- **Indigo-100** `#e0e7ff` - Light backgrounds for emphasis

### Secondary Colors
- **Slate-500** `#64748b` - Secondary actions
- **Slate-100** `#f1f5f9` - Card backgrounds
- **Slate-50** `#f8fafc` - Page backgrounds

### Accent Colors
- **Cyan-500** `#06b6d4` - Highlights and attention
- **Emerald-500** `#10b981` - Success states
- **Amber-500** `#f59e0b` - Warning states
- **Red-500** `#ef4444` - Error states

### Text Colors
- **Slate-900** `#0f172a` - Primary text
- **Slate-700** `#475569` - Secondary text
- **Slate-400** `#94a3b8` - Tertiary text
- **Slate-50** `#f8fafc` - Text on dark backgrounds

## 📐 Typography

### Heading System
- **H1** `text-4xl font-bold` - Page titles
- **H2** `text-3xl font-bold` - Section titles
- **H3** `text-2xl font-semibold` - Subsection titles
- **H4** `text-xl font-semibold` - Card titles
- **H5** `text-lg font-semibold` - Emphasis text
- **H6** `text-base font-semibold` - Labels

### Body Text
- **Body** `text-base leading-relaxed` - Default text
- **Small** `text-sm` - Secondary information
- **Extra Small** `text-xs` - Tertiary information

### Font Stack
```
-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", 
"Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", 
"Helvetica Neue", sans-serif
```

## 🎯 Component Styles

### Buttons
All buttons use consistent styling with hover and focus states.

#### Button Types
- **Primary** `.btn-primary` - Main CTA, Indigo background
- **Secondary** `.btn-secondary` - Alternative action, Slate background
- **Ghost** `.btn-ghost` - Minimal, text-only
- **Danger** `.btn-danger` - Destructive actions, Red background

#### Button Sizes
- **Small** `.btn-sm` - Compact buttons
- **Medium** `.btn` - Default size
- **Large** `.btn-lg` - Prominent buttons

### Chat Bubbles
- **User Message** `.chat-bubble-user` - Indigo background, white text, right-aligned
- **Bot Message** `.chat-bubble-bot` - Light Slate background, border, left-aligned
- **Fallback Message** `.chat-bubble-fallback` - Amber background, warning styling

### Cards
- **Standard Card** `.card` - White background, subtle shadow, border
- **With Padding** `.card-padding` - 1.5rem padding

### Forms
- **Input** `.input` - Consistent styling with focus ring
- **Focus State** - Indigo ring, transparent border on focus
- **Disabled State** - Light Slate background, reduced opacity

### Badges
- **Primary** `.badge-primary` - Indigo-tinted
- **Success** `.badge-success` - Green-tinted
- **Warning** `.badge-warning` - Amber-tinted
- **Error** `.badge-error` - Red-tinted

## 🎬 Animations

### Loading States
- **Spinner** - Indigo rotating border
- **Bounce Dots** - Three dots with staggered animation
- **Pulse** - Subtle opacity pulse for focus

### Transitions
- **Fade In** - 0.3s smooth appearance
- **Slide Up** - 0.5s upward motion
- **All Transitions** - 0.2s ease-in-out

### Hover Effects
- **Buttons** - Background color shift + shadow enhancement
- **Cards** - Shadow increase on hover
- **Links** - Color shift + underline

## 🌐 Layout System

### Containers
- **Full Width** - Full page width with padding
- **Max Width** - `.max-w-7xl` for content, `.max-w-2xl` for chat/forms

### Spacing Scale
- **xs** `0.25rem` (4px)
- **sm** `0.5rem` (8px)
- **md** `1rem` (16px)
- **lg** `1.5rem` (24px)
- **xl** `2rem` (32px)
- **2xl** `3rem` (48px)

### Grid System
- **2 Column** `grid-cols-1 md:grid-cols-2`
- **3 Column** `grid-cols-1 md:grid-cols-3`
- **Gap** `gap-4` to `gap-6` for consistency

## 💻 CSS Classes Reference

### Layout
```
.container-max     /* max-w-7xl mx-auto */
.container-md      /* max-w-2xl mx-auto */
.divider           /* border-t border-slate-200 */
```

### Components
```
.btn               /* Base button */
.btn-primary       /* Primary button */
.btn-secondary     /* Secondary button */
.btn-ghost         /* Ghost button */
.btn-danger        /* Danger button */

.input             /* Form input */
.input-error       /* Error input styling */

.card              /* Card component */
.card-padding      /* Card with padding */

.chat-bubble       /* Base chat bubble */
.chat-bubble-user  /* User message bubble */
.chat-bubble-bot   /* Bot message bubble */
```

### Animations
```
.animate-fadeIn    /* Fade in 0.3s */
.animate-slideUp   /* Slide up 0.5s */
.animate-spin      /* Continuous rotation */
.animate-pulse     /* Opacity pulse */
```

## 📱 Responsive Design

### Breakpoints (Tailwind)
- **Mobile** `< 640px` (default)
- **Tablet** `md: 768px`
- **Desktop** `lg: 1024px`
- **Wide** `xl: 1280px`

### Responsive Patterns
- **Mobile First** - Default styles apply to mobile
- **Stack on Mobile** - Single column layout
- **Expand on Desktop** - Multi-column for desktop
- **Hide on Mobile** - `.hidden sm:block` for secondary info

## 🔍 Usage Examples

### Chat Page
- Header: Sticky, shadow, clear navigation
- Messages: Animated fade-in, color-coded bubbles
- Input: Full-width with button, focus ring visible
- Loading: Animated dots with stagger

### Dashboard
- Hero Section: Large heading, subtext
- Cards: Gradient backgrounds, hover shadows
- CTAs: Gradient buttons with icons
- Info Banner: Accent background, icon list

### Authentication
- Forms: Consistent input styling
- Buttons: Primary CTA, full-width
- Links: Subtle color, hover effect
- Errors: Red badge background

## 📋 Best Practices

1. **Use CSS Variables** - Color values via `var(--color-primary)`
2. **Leverage Tailwind Classes** - Don't duplicate styles
3. **Maintain Spacing Consistency** - Use scale (sm, md, lg)
4. **Focus States Always** - Keyboard navigation essential
5. **Dark Mode Ready** - CSS variables support dark mode
6. **Animations Subtle** - Avoid overstimulation
7. **Accessibility First** - WCAG AA standard minimum

