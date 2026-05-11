# Vision

**OperaBot** is a local AI knowledge assistant for operational teams.

## Problem

Organizations lose productivity when operational knowledge is fragmented:
- Critical procedures exist only in one person's head
- Onboarding new team members is slow
- Knowledge gets lost when people leave
- External AI APIs are not suitable for sensitive operational data

## Solution

A self-hosted knowledge system where teams can:
1. Build a searchable knowledge base (FAQs, documents)
2. Ask questions about operations in natural language
3. Get answers with source attribution (where the answer came from)
4. Keep all data on-premise (no cloud APIs, 100% local)

## How It Works

1. Upload operational documents (PDFs, FAQs)
2. System automatically indexes them into vectors
3. When someone asks a question, the system:
   - Searches the knowledge base for relevant documents
   - Generates an answer using local AI
   - Shows sources and confidence level
4. Team learns from each interaction

## Key Principles

- **Local first:** 100% local inference (Ollama), no cloud dependency
- **Privacy:** All data stays on-premise
- **Simple:** Minimal setup, Docker-based infrastructure
- **Reliable:** No external API dependencies
- **Transparent:** Sources are shown with answers

