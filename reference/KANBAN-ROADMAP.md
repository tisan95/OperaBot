# 🎯 OperaBot - KANBAN Roadmap
**Last Updated:** 17 de Abril de 2026  
**Release Target:** v0.2 (Estable), v0.3 (Features), v0.4 (Polish)

---

## 📋 ESTRUCTURA KANBAN

```
┌─────────────────────────────────────────────────────────────────────┐
│  🔴 CRITICAL BLOCKERS                                               │
├─────────────────────────────────────────────────────────────────────┤
│  → FIX-001: test_generate_answer_ollama_success                  ✅ │
│  → FIX-002: Pydantic ConfigDict migration                       ⏳ │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  ✅ TODO              ⏳ IN PROGRESS       🔄 REVIEW        ✅ DONE   │
├─────────────────────────────────────────────────────────────────────┤
```

---

## BLOQUE 0: CRÍTICO (Esta semana - 17-21 Abril)

### TODO

```
┌─────────────────────────────────────┐
│ FIX-002                             │
│ Pydantic ConfigDict Migration       │
│ ⏱️  45 min | 🔴 Must fix           │
│                                     │
│ Files:                              │
│ - app/models/*.py                   │
│ - app/api/schemas/*.py              │
│                                     │
│ Action: Replace class Config:       │
│ with model_config = ConfigDict(...) │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ CORE-004                            │
│ Rate Limiting en /chat/messages     │
│ ⏱️  2 horas | 🔴 Security critical │
│                                     │
│ Deps: None                          │
│ Library: slowapi                    │
│ Limit: 10 req/min per IP           │
└─────────────────────────────────────┘
```

### IN PROGRESS

```
┌─────────────────────────────────────┐
│ CORE-001                            │
│ Transaction Rollback Consistency    │
│ ⏱️  3 horas | 🟡 Important         │
│                                     │
│ Status: 70% done                    │
│ Files: chat.py, faq.py              │
│                                     │
│ Todo:                               │
│ - [ ] Audit all error paths         │
│ - [ ] Add rollback() calls          │
│ - [ ] Test each scenario            │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ CORE-005                            │
│ Input Validation (Backend)          │
│ ⏱️  2 horas | 🟡 Data integrity    │
│                                     │
│ Status: 60% done                    │
│ Focus: FAQ, Chat, Auth fields       │
│                                     │
│ Todo:                               │
│ - [ ] String length limits          │
│ - [ ] Email validation              │
│ - [ ] Special char escaping         │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ TEST-005                            │
│ Integration: Chat with FAQ Context  │
│ ⏱️  2.5 horas | 🟡 Coverage       │
│                                     │
│ Status: 80% done                    │
│ Goal: Test LLM + FAQ integration    │
│                                     │
│ Todo:                               │
│ - [ ] Mock LLM response             │
│ - [ ] Test FAQ retrieval in context │
│ - [ ] Verify fallback trigger       │
└─────────────────────────────────────┘
```

### DONE

```
✅ FIX-001: test_generate_answer_ollama_success (FIXED)
✅ Build verification (npm run build)
✅ Frontend CSS refactor (globals.css)
✅ Auth flow (register → login)
✅ FAQ E2E test (create → list)
```

---

## BLOQUE 1: FASE ESTABLE v0.2 (18-28 Abril - 2 semanas)

### TODO

```
┌─────────────────────────────────────┐
│ UI-001                              │
│ ErrorBoundary Component             │
│ ⏱️  1.5 horas | 🟡 Stability      │
│                                     │
│ Location: lib/ErrorBoundary.tsx     │
│ Catch: React render errors          │
│ Fallback: Error page + retry btn    │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ UI-004                              │
│ Toast Notifications                 │
│ ⏱️  2 horas | 🟡 UX feedback      │
│                                     │
│ Library: sonner                     │
│ Implement: Success/error/info       │
│ For: API responses, form submission │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ UI-005                              │
│ Optimistic Updates (FAQ)            │
│ ⏱️  2 horas | 🟡 UX responsiveness│
│                                     │
│ Pattern: Add to UI before API call  │
│ Rollback on error                   │
│ Apply to: FAQ create, future update │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ CORE-006                            │
│ Session Timeout (30min)             │
│ ⏱️  1.5 horas | 🟡 Security      │
│                                     │
│ Backend: Add timeout check          │
│ Frontend: Redirect to login         │
│ Grace period: 5min warning banner   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ TEST-007                            │
│ End-to-End Full User Journey        │
│ ⏱️  4 horas | 🟡 Validation      │
│                                     │
│ Flow:                               │
│ 1. Register user                    │
│ 2. Create FAQ                       │
│ 3. Send chat message                │
│ 4. Rate response                    │
│ 5. Check analytics                  │
└─────────────────────────────────────┘
```

### IN PROGRESS

```
┌─────────────────────────────────────┐
│ UI-002                              │
│ Retry Logic (Exponential Backoff)   │
│ ⏱️  2 horas | 🟡 Resilience      │
│                                     │
│ Status: 30% done                    │
│ Function: lib/api.ts (apiFetch)     │
│                                     │
│ Todo:                               │
│ - [ ] Implement retry wrapper       │
│ - [ ] Exponential backoff (1s,2s...) │
│ - [ ] Max 3 retries                 │
│ - [ ] Don't retry 4xx errors        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ UI-003                              │
│ Loading States                      │
│ ⏱️  1.5 horas | 🟡 UX clarity    │
│                                     │
│ Status: 60% done                    │
│ Add skeletons/spinners for:         │
│ - [ ] FAQ list loading              │
│ - [ ] Chat message sending          │
│ - [ ] Auth endpoints                │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ UI-006                              │
│ Form Validation (Client)            │
│ ⏱️  1.5 horas | 🟡 Data quality  │
│                                     │
│ Status: 40% done                    │
│ Implement on:                       │
│ - [ ] Login form                    │
│ - [ ] Register form                 │
│ - [ ] FAQ create form               │
│ - [ ] Chat input field              │
└─────────────────────────────────────┘
```

---

## BLOQUE 2: FASE FEATURE v0.3 (1-14 Mayo - 2 semanas)

### TODO

```
┌─────────────────────────────────────┐
│ ANALYTICS-002                       │
│ Frontend Analytics Dashboard        │
│ ⏱️  3 horas | 🟢 Feature         │
│                                     │
│ Location: app/(auth)/admin/         │
│ Charts: Chat volume, success rate   │
│ KPIs: Top questions, response time  │
│                                     │
│ Deps: ANALYTICS-001 (backend done)  │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ FAQ-001                             │
│ Update FAQ Endpoint                 │
│ ⏱️  2 horas | 🟢 Feature         │
│                                     │
│ Endpoint: PUT /faqs/{id}            │
│ Fields: question, answer, category  │
│ Test: integration test              │
│ Frontend: Edit form modal            │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ FAQ-002                             │
│ Delete FAQ Endpoint                 │
│ ⏱️  1.5 horas | 🟢 Feature       │
│                                     │
│ Endpoint: DELETE /faqs/{id}         │
│ Soft delete or hard?                │
│ Frontend: Confirm dialog            │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ CHAT-001                            │
│ Chat History Persistence            │
│ ⏱️  3 horas | 🟢 Feature         │
│                                     │
│ Backend: Fetch conversation history │
│ Frontend: Load previous chats       │
│ UI: Chat sidebar with history       │
│ Pagination: Latest 10 chats         │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ DEVOPS-001                          │
│ Docker Containers                   │
│ ⏱️  4 horas | 🟢 Infrastructure  │
│                                     │
│ Build: Multi-stage Dockerfiles      │
│ Backend: Production Python image    │
│ Frontend: Node.js builder           │
│ Compose: docker-compose.yml         │
└─────────────────────────────────────┘
```

---

## BLOQUE 3: FASE POLISH v0.4 (15+ Mayo)

### TODO

```
┌─────────────────────────────────────┐
│ POLISH-001                          │
│ Dark Mode Toggle                    │
│ ⏱️  2 horas | 🔵 Nice-to-have    │
│                                     │
│ Storage: localStorage preference    │
│ System: Respect prefers-color-scheme│
│ CSS: Update theme.css dark vars     │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ POLISH-004                          │
│ Mobile Responsiveness               │
│ ⏱️  3 horas | 🔵 Mobile UX       │
│                                     │
│ Test devices: iPhone 12/14, Android │
│ Focus: Chat, FAQ, Dashboard         │
│ Touch: Tap targets >= 44px          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ PERF-006                            │
│ Caching Strategy (HTTP)             │
│ ⏱️  1.5 horas | 🔵 Performance   │
│                                     │
│ Headers: Cache-Control max-age      │
│ Strategy: 30d for static, 1h API    │
│ CDN: Consider Cloudflare            │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ DEVOPS-002                          │
│ CI/CD Pipeline (GitHub Actions)     │
│ ⏱️  3 horas | 🔵 DevOps         │
│                                     │
│ On: Push to main                    │
│ Steps: Test → Build → Deploy        │
│ Slack: Notifications                │
└─────────────────────────────────────┘
```

---

## 📊 TIMELINE VISUAL

```
Abril 2026
═══════════════════════════════════════════════════════════════

17    Auditoría ✅ (Hoy)
18-21 BLOQUE 0: Critical fixes          ⏳ (Esta semana)
      └─ FIX-001 ✅, FIX-002 ⏳
      └─ CORE-001,004,005 ⏳
      └─ Tests ⏳

22-28 BLOQUE 1: Estable (v0.2)          📋 (Próxima semana)
      └─ UI-001,004,005,006 📋
      └─ CORE-006 📋
      └─ TEST-007 📋

Mayo 2026
═══════════════════════════════════════════════════════════════

1-14  BLOQUE 2: Features (v0.3)        🔮 (Futuro)
      └─ ANALYTICS-002 🔮
      └─ FAQ-001,002 🔮
      └─ CHAT-001 🔮
      └─ DEVOPS-001 🔮

15+   BLOQUE 3: Polish (v0.4+)         🎨 (Later)
      └─ POLISH-001,004 🎨
      └─ PERF-006 🎨
      └─ DEVOPS-002 🎨
```

---

## 🔄 Workflow: Cómo Usar Este Kanban

### Cada Día
1. Revisar tarjeta de TODO principal
2. Mover a IN PROGRESS al empezar
3. Al completar: → DONE
4. Blockers: Reportar en síncronos

### Cada Semana
1. Sprint planning: Asignar bloque
2. Retro: Qué funcionó, qué no
3. Adaptar timeline si es necesario

### Rules
- 🔴 Críticos: No bloquean releases si está mitigado
- 🟡 Importantes: Incluir en release siguiente
- 🟢 Features: Roadmap visible a stakeholders
- 🔵 Polish: Cuando tiempo lo permite

---

## 📌 PINNED ITEMS

```
🚨 WATCH: Timeout issues (Ollama 60s)
🚨 WATCH: Database transaction state
💡 IDEA: Switch to PostgreSQL native for better performance
💡 IDEA: Add Slack integration for alerts
```

---

## 📈 METRICS TO TRACK

| Metric | Current | Target | Responsible |
|--------|---------|--------|-------------|
| Test Coverage | 69% | 90% | Dev |
| Response Time (p95) | TBD | <500ms | Dev |
| Uptime | TBD | 99.5% | DevOps |
| User Satisfaction | TBD | 4.5/5 | Product |

---

**Generated:** 17 de Abril 2026  
**Review Date:** Weekly on Fridays  
**Next Update:** 24 de Abril 2026
