---
name: interactive-app-builder
description: Build interactive web applications, tools, dashboards, games, and visualizations. Use this skill whenever the user wants to create anything interactive—dashboards, games, data visualizations, React components, web experiences, animated tools, or any clickable/dynamic application. The skill intelligently gathers requirements (if ambiguous), recommends the right tech stack, builds production-ready code with explanations, and iteratively refines based on user feedback. Trigger on phrases like "create an interactive tool," "build a dashboard," "make a game," "interactive visualization," "web app," or when the user wants something beyond static output.
---

# Interactive App Builder

A skill for guiding users through the complete journey of building interactive applications—from clarifying intent through production-ready code.

## Workflow Overview

```
1. Assess Clarity → 2. Smart Interview (if needed) → 3. Design Phase
   ↓
4. Tech Recommendation → 5. Build Phase → 6. Auto-Refinement
   ↓
7. Iteration Loop (user feedback) → 8. Polish & Deliver
```

---

## Phase 1: Assess Clarity

**Goal:** Determine if the request is clear enough to proceed directly to building, or if clarifying questions are needed.

**How to decide:**
- **Clear request:** User specifies exactly what they want (e.g., "build a React component that calculates mortgage payments with sliders")
- **Ambiguous request:** User describes intent broadly (e.g., "I need an interactive tool for data analysis")

**Action:**
- **If clear:** Skip to Phase 3 (Design)
- **If ambiguous:** Proceed to Phase 2 (Smart Interview)

---

## Phase 2: Smart Interview (Conditional)

Ask **focused, open-ended questions** to understand:

### Core Requirements
1. **What is it?** Type and primary purpose
   - Dashboard? Game? Visualization? Data tool? Content creator? Educational tool?
2. **Who uses it?** Target audience and technical level
3. **Key features?** 3-5 core features, in priority order
4. **Data source?** Static data, user input, API, database, simulation?
5. **Success criteria?** How will they know it's working?

### Technical Context
6. **Tech preference?** Any constraints or preferences? (React, vanilla JS, specific libraries?)
7. **Visual style?** Modern/minimal? Playful? Professional? Custom brand?
8. **Performance needs?** Real-time? Heavy computation? Large datasets?
9. **Interactivity level?** Simple clicks? Complex state management? Animations?

### Scope & Timeline
10. **MVP or complete?** Are we building everything now, or an MVP first?
11. **Customization?** Will they want to modify/extend it later?

---

## Phase 3: Design Phase

Before writing code, establish the **design blueprint:**

### Conceptual Model
- **User flow:** How does the user interact? (step by step)
- **State management:** What data changes? How?
- **Key screens/states:** Sketch the major views/modes

### Technical Decisions
- **Tech stack recommendation** (see Phase 4)
- **Architecture:** Single-file artifact? Multi-component? Modular?
- **Libraries needed:** UI frameworks, charting, animation, etc.
- **Performance strategy:** Lazy loading? Memoization? Data limits?

### UX/Design
- **Visual direction:** Color palette, typography, layout
- **Responsive behavior:** Mobile? Desktop? Both?
- **Accessibility:** Color contrast, keyboard nav, semantic HTML

---

## Phase 4: Tech Recommendation

Match the use case to the right tech stack. **Always explain why.**

### Decision Tree

#### **React + Tailwind + shadcn/ui** (Most versatile)
- **When:** Complex state, real-time interactivity, reusable components, professional polish needed
- **Examples:** Dashboards, data tools, content creators, SaaS-like apps
- **Why:** Component ecosystem, state management, accessible UI library
- **Setup:** Pre-configured for shadcn/ui in Claude artifacts

#### **Vanilla HTML/CSS/JavaScript**
- **When:** Simple interactivity, no state complexity, lightweight preferred
- **Examples:** Calculators, simple form tools, educational projects, landing pages
- **Why:** No dependencies, fast, works everywhere
- **When to skip:** Avoid for apps needing heavy state or many components

#### **Canvas + p5.js**
- **When:** Visual/generative art, animations, particle systems, drawing tools
- **Examples:** Generative art, interactive visualizations, creative tools
- **Why:** Fine-grained pixel control, animation performance
- **Setup:** p5.js CDN available

#### **Three.js** (3D)
- **When:** 3D visualization, interactive geometry, immersive experiences
- **Examples:** 3D model viewers, spatial visualizations, games
- **Why:** WebGL abstraction, performance, camera controls

#### **Framework specific** (Vue, Svelte, etc.)
- **When:** User explicitly requests or if it's a team standard
- **How:** Adapt the approach; core principles remain the same

---

## Phase 5: Build Phase

### Principles for Production-Ready Code

1. **Clear structure**
   - Single-file artifacts for simple apps (<300 lines)
   - Multi-file/multi-artifact for complex projects (>300 lines)
   - Logical component organization (if React)

2. **Best practices**
   - Semantic HTML
   - Proper state management
   - Performance optimization (no unnecessary re-renders, efficient algorithms)
   - Error handling and edge cases
   - Accessible UI (ARIA labels, keyboard nav, color contrast)

3. **Code quality**
   - **Inline comments:** Explain *why*, not *what*
   - **Naming:** Clear, descriptive variable/function names
   - **No magic numbers:** Extract to constants
   - **DRY principle:** Don't repeat code
   - **Type safety:** Use TypeScript if complex, or JSDoc comments

4. **User experience**
   - Responsive design (mobile-first)
   - Intuitive interactions (no surprises)
   - Clear feedback (loading states, success/error messages)
   - Performance (fast load, smooth interactions)

### Delivery Format

**Single Artifact (simple apps):**
- One .jsx or .html file
- Clear README comments at top
- Inline explanations for key logic

**Multi-Component Project (complex apps):**
- Main artifact with all components
- OR: Multiple related artifacts (if user prefers separation)
- Components clearly labeled with purposes

---

## Phase 6: Auto-Refinement

After building, **proactively suggest 2-3 improvements:**

- **Accessibility:** "Add ARIA labels for screen readers here..."
- **Performance:** "Consider memoizing this component to avoid re-renders..."
- **UX:** "The loading state could show progress with a spinner..."
- **Polish:** "These buttons could fade in with a 200ms delay..."
- **Features:** "You could add a dark mode toggle..."

**Ask:** "Would you like me to implement any of these improvements?"

---

## Phase 7: Iteration Loop

User provides feedback → Implement changes → Show updated code → Repeat

**Common refinement requests:**
- Color/styling adjustments
- Feature additions
- Performance tweaks
- Accessibility improvements
- Code organization

---

## Phase 8: Polish & Deliver

Before final delivery:
- ✅ Code is clean and well-commented
- ✅ All interactive elements work smoothly
- ✅ Mobile responsive (if applicable)
- ✅ Accessibility basics met (contrast, keyboard nav)
- ✅ Performance is acceptable (no janky animations, fast load)
- ✅ User can understand and modify it
- ✅ Learning resources provided

**Final artifact delivery:**
- Clear instructions for use
- Notes on customization points
- Links to relevant docs/resources
- Option to extend or modify

---

## Tech Stack Comparison at a Glance

| Stack | Best For | Setup Time | Learning Curve | Ecosystem |
|-------|----------|------------|-----------------|-----------|
| **React + Tailwind** | Complex apps, dashboards | 2 min | Medium | Massive |
| **Vanilla JS** | Simple tools, prototypes | 1 min | Low | Minimal |
| **Canvas + p5.js** | Visual/generative art | 1 min | Medium | Niche |
| **Three.js** | 3D experiences | 3 min | High | Growing |
| **Vue/Svelte** | Mid-complexity, preference-driven | 2-3 min | Medium | Good |

---

## Adaptive Communication

### Audience Assessment
- **Beginner signals:** "I don't know React", "Keep it simple", asking what libraries are
  - **Approach:** More explanation, simpler patterns, offer vanilla JS
- **Intermediate signals:** Understanding of components, asking about performance
  - **Approach:** Explain briefly, show best practices, offer optimization tips
- **Advanced signals:** Asking about state management, performance optimization, architecture
  - **Approach:** Assume knowledge, focus on elegant solutions

### Explanation Scale
- **Minimal:** Just code comments + one-liner explanations
- **Moderate:** Code comments + brief paragraph explanations
- **Detailed:** Code comments + full explanations + learning resources

---

## Common Patterns & Examples

### State Management (React)
- Simple: `useState` + local state
- Medium: `useReducer` or context
- Complex: External library (Zustand, Redux if needed)

### Styling Approaches
- **Tailwind:** Utility classes (recommended for most apps)
- **CSS modules:** Scoped styles (for complex apps)
- **Inline styles:** Simple, component-level (use sparingly)
- **Styled components:** JS-in-CSS (if user prefers)

### Data Handling
- **Static:** Hardcoded or imported JSON
- **User input:** Forms, drag-and-drop, file upload
- **API:** Fetch or axios with error handling
- **Simulation:** Generate data algorithmically

### Performance Optimization
- `React.memo()` for expensive components
- `useMemo()` for expensive calculations
- `useCallback()` for stable function references
- Code splitting for large apps
- Lazy loading images/components

---

## Checklist for Handoff

Before considering the app "done":

- [ ] App loads and runs without errors
- [ ] All interactive elements function as intended
- [ ] Mobile responsive (if applicable)
- [ ] Keyboard navigation works
- [ ] Color contrast meets accessibility standards
- [ ] Code is commented and understandable
- [ ] User knows how to customize it
- [ ] Performance is acceptable
- [ ] No console warnings/errors
- [ ] Matches the design intent from Phase 3

---

## When to Use This Skill

✅ **Definitely use:**
- "Build me an interactive dashboard"
- "Create a game where..."
- "I need a tool that lets users..."
- "Make a visualization for my data"
- "Build a React component for..."
- "Create an interactive calculator"
- "Make an animated web experience"

✅ **Probably use:**
- "I want a website where users can..." (if interactive/dynamic)
- "Build a tool that..." (if it involves interactivity)

❌ **Probably don't use:**
- "Write a blog post" (use writing skill instead)
- "Create a static landing page" (unless very interactive)
- "Analyze this data" (use analysis skill instead)

---

## Resources & References

### React & Components
- [React Docs](https://react.dev)
- [shadcn/ui Components](https://ui.shadcn.com)
- [Tailwind CSS](https://tailwindcss.com)

### Accessibility
- [Web Content Accessibility Guidelines (WCAG)](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Practices](https://www.w3.org/WAI/ARIA/apg/)

### Performance
- [React Performance Optimization](https://react.dev/reference/react#performance)
- [Web Vitals](https://web.dev/vitals/)

### Design & UX
- [Design Systems](https://www.designsystems.com)
- [Responsive Design](https://web.dev/responsive-web-design-basics/)

---

## Quick Start Template

For reference, here's the general structure for a React app:

```jsx
import { useState } from 'react';

export default function App() {
  const [state, setState] = useState(initialValue);

  const handleInteraction = (e) => {
    // Handle user input, update state, etc.
    setState(newValue);
  };

  return (
    <div className="container mx-auto p-6">
      {/* UI here */}
      <button onClick={handleInteraction}>
        Interact
      </button>
    </div>
  );
}
```

---

## Notes for Claude

When using this skill:

1. **Read the context:** Assess clarity before interviewing
2. **Ask smartly:** Only interview if ambiguous; be conversational
3. **Explain decisions:** Always tell the user why you're choosing a tech stack
4. **Build with purpose:** Every line of code should serve the user's goal
5. **Iterate collaboratively:** Treat suggestions as starting points; user has final say
6. **Over-deliver:** Production-ready beats "it works"
7. **Teach by doing:** Comments + resources help users learn

---

**This skill is philosophy + practice: guide the user toward building great interactive applications, not just getting something to work.**
