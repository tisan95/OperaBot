# ADR-006: Frontend Framework Selection

**Status**: Accepted  
**Date**: 2026-04-15  
**Author**: Architect  
**Scope**: MVP User & Admin Panels

---

## Context and Problem Statement

OperaBot MVP requires two separate frontend interfaces:
1. **User Panel**: FAQ browser + chat interface (for warehouse/operational staff)
2. **Admin Panel**: Knowledge management + analytics (for operations managers)

**Requirements**:
- Mobile-responsive (warehouse floor staff may use tablets/phones)
- Modern, clean UI (portfolio-ready, not enterprise-heavy)
- Real-time updates (chat messages should appear instantly)
- Component-based (reusable UI components for FAQ, chat, analytics)
- Fast development (MVP timeline 4-6 months)

**Technology Stack Constraint**: React or Next.js

## Decision Drivers

1. **Development Speed**: MVP timeline requires rapid UI development
2. **Component Reusability**: FAQ browser, chat, analytics share components
3. **Real-Time Features**: Chat needs real-time message updates
4. **Deployment**: SPA (Single Page App) or SSR (Server-Side Rendering)?
5. **Mobile Responsiveness**: Warehouse staff may use phones/tablets

## Considered Options

### Option 1: Next.js (CHOSEN)
```
Strategy: Next.js 14+ with TypeScript, Tailwind CSS

Pros:
- Full-stack framework (can handle API routes if needed, but we use FastAPI)
- Built-in optimizations (image, font, code splitting)
- SSR + static generation options
- Great developer experience
- File-based routing (faster development)
- Excellent TypeScript support
- Vercel deployment integration (simple deployment)
- App Router pattern (modern, cleaner)

Cons:
- More opinionated than plain React
- Slight learning curve for team unfamiliar with Next.js
```

### Option 2: React + Vite (SPA)
```
Pros:
- Lightweight, minimal overhead
- Fast builds (Vite is very fast)
- Familiar to React developers

Cons:
- Need to set up own tooling (routing, state management, etc.)
- Slower initial development vs. Next.js
- No built-in server capabilities
```

### Option 3: React + Create React App
```
Pros:
- Standard setup, widely familiar

Cons:
- Slower build times
- More boilerplate
- Not as many built-in optimizations
- Slower development cycle
```

## Decision Outcome

**Choose: Next.js 14+ (App Router, TypeScript, Tailwind CSS)**

**Rationale**:
1. **Development Speed**: Next.js file-based routing + built-in features speed up MVP development
2. **Out-of-the-Box Optimizations**: Image optimization, font optimization, code splitting reduce performance tuning
3. **Mobile-Responsive**: Tailwind CSS makes responsive design fast and consistent
4. **Real-Time Chat**: Next.js with WebSocket integration handles chat updates cleanly
5. **Deployment**: Vercel (made by Next.js creators) offers simple, fast deployment
6. **Future-Proof**: Can add server-side features later if needed (but FastAPI is primary backend)
7. **TypeScript Support**: Built-in TypeScript support reduces bugs

## Architecture

### Project Structure
```
frontend/
  ├── app/                    # Next.js App Router
  │   ├── layout.tsx          # Root layout (nav, auth wrapper)
  │   ├── page.tsx            # Login page
  │   ├── (auth)/             # Protected routes
  │   │   ├── dashboard/      # User dashboard (FAQ + Chat)
  │   │   ├── admin/          # Admin panel (Knowledge + Analytics)
  │   │   └── layout.tsx      # Auth wrapper layout
  │   └── api/                # API routes (auth, health check)
  ├── components/
  │   ├── FAQBrowser.tsx      # FAQ category + search
  │   ├── Chat.tsx            # Chat interface
  │   ├── AdminPanel.tsx      # Admin dashboard
  │   ├── AnalyticsDashboard.tsx
  │   └── shared/             # Shared components (buttons, forms, etc.)
  ├── lib/
  │   ├── api.ts              # FastAPI client (fetch wrapper)
  │   ├── auth.ts             # Auth utilities
  │   └── hooks/              # Custom React hooks
  ├── styles/
  │   └── globals.css         # Tailwind configuration
  ├── public/                 # Static assets
  ├── next.config.js
  ├── tsconfig.json
  └── tailwind.config.js
```

### Technology Stack
```
- Framework: Next.js 14+ (App Router)
- Language: TypeScript
- Styling: Tailwind CSS
- State Management: React Context (simple) or Zustand (if complex)
- HTTP Client: Fetch API + custom wrapper
- Real-Time: WebSocket for chat (native browser API)
- UI Components: Headless UI (optional, for accessibility)
- Icons: Lucide React or Heroicons
```

### API Integration (FastAPI)
```typescript
// frontend/lib/api.ts

export const apiClient = {
  async get(endpoint: string) {
    const response = await fetch(`/api${endpoint}`, {
      method: 'GET',
      credentials: 'include',  // Send cookies (JWT auth)
    });
    return response.json();
  },
  
  async post(endpoint: string, data: any) {
    const response = await fetch(`/api${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
      credentials: 'include',
    });
    return response.json();
  }
};

// Usage in component:
const FAQs = () => {
  const [faqs, setFaqs] = useState([]);
  
  useEffect(() => {
    apiClient.get('/faqs').then(setFaqs);
  }, []);
};
```

### Real-Time Chat via WebSocket
```typescript
// frontend/lib/websocket.ts

export const useChatWebSocket = (conversationId: string) => {
  const [messages, setMessages] = useState([]);
  
  useEffect(() => {
    const ws = new WebSocket(`wss://api.example.com/ws/chat/${conversationId}`);
    
    ws.onmessage = (event) => {
      const newMessage = JSON.parse(event.data);
      setMessages(prev => [...prev, newMessage]);
    };
    
    return () => ws.close();
  }, [conversationId]);
  
  return messages;
};
```

## Consequences

### Good
- Fast development cycle (MVP timeline benefit)
- Modern, clean codebase (portfolio-ready)
- Built-in optimizations (images, fonts, code splitting)
- Excellent TypeScript support
- Simple deployment to Vercel

### Bad
- Team must learn Next.js (if unfamiliar)
- Slightly more opinionated than plain React

### Neutral
- Next.js SSR not used in MVP (FastAPI handles server logic)
- Learning curve minimal if team knows React

## Confirmation

This decision is confirmed by:
1. **Development Benchmark**: Verify Next.js + Tailwind development speed vs. plain React
2. **Performance Testing**: Measure page load time, chat response UI latency
3. **Mobile Testing**: Test on iOS/Android devices for responsive design
4. **Deployment Testing**: Verify Vercel or self-hosted deployment works

## Research Links

- https://nextjs.org/docs — Next.js documentation
- https://nextjs.org/docs/app — Next.js App Router
- https://tailwindcss.com/ — Tailwind CSS
- https://vercel.com/docs — Vercel deployment docs

