"use client";

import { apiFetch } from "@/lib/api";
import { FormEvent, useEffect, useRef, useState } from "react";
import { Send, MessageSquare } from "lucide-react";

interface Source {
  type: string;
  title: string;
  name?: string;
  score: string;
}

interface ChatMessage {
  id: number;
  user_message: string;
  bot_message: string;
  sources: Source[];
  confidence: number;
  created_at: string;
  isLoading?: boolean;
  isRateLimit?: boolean;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadHistory();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const loadHistory = async () => {
    try {
      const response = await apiFetch("/chat/history?limit=50");
      if (Array.isArray(response)) {
        setMessages(response);
      }
    } catch (err) {
      console.error("Failed to load chat history:", err);
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const userMessage = input.trim();
    if (!userMessage) return;

    setError(null);
    setInput("");
    setLoading(true);

    const tempId = Math.random();
    setMessages((prev) => [
      ...prev,
      {
        id: tempId,
        user_message: userMessage,
        bot_message: "",
        sources: [],
        confidence: 0,
        created_at: new Date().toISOString(),
        isLoading: true,
      },
    ]);

    try {
      const response = await apiFetch("/chat/messages", {
        method: "POST",
        body: JSON.stringify({ message: userMessage }),
      });

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === tempId
            ? {
                ...msg,
                id: response.id,
                bot_message: response.bot_message,
                sources: response.sources || [],
                confidence: response.confidence || 0,
                created_at: response.created_at,
                isLoading: false,
              }
            : msg
        )
      );
    } catch (err: any) {
      const isRateLimit = err?.status === 429;
      const message = err instanceof Error ? err.message : "Failed to send message";

      if (isRateLimit) {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === tempId
              ? { ...msg, bot_message: message, isLoading: false, isRateLimit: true }
              : msg
          )
        );
      } else {
        setError(message);
        setMessages((prev) => prev.filter((msg) => msg.id !== tempId));
      }
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return "#38A169";
    if (confidence >= 0.6) return "#C9A84C";
    return "#E53E3E";
  };

  return (
    <div
      className="flex flex-col rounded-xl border"
      style={{
        height: "calc(100vh - 120px)",
        backgroundColor: "#0A0A0A",
        borderColor: "#2A2A2A",
      }}
    >
      {/* Header */}
      <div
        className="border-b px-6 py-4 shrink-0"
        style={{ backgroundColor: "#111111", borderColor: "#2A2A2A" }}
      >
        <h1 className="text-base font-semibold" style={{ color: "#F5F5F5" }}>
          Chat
        </h1>
        <p className="text-xs mt-0.5" style={{ color: "#888888" }}>
          Consulta sobre tu base de conocimiento operacional
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div
                className="w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 border"
                style={{ backgroundColor: "#1A1A1A", borderColor: "#2A2A2A" }}
              >
                <MessageSquare size={20} strokeWidth={1.5} style={{ color: "#C9A84C" }} />
              </div>
              <h2 className="text-base font-semibold mb-2" style={{ color: "#F5F5F5" }}>
                Inicia una conversación
              </h2>
              <p className="text-sm max-w-xs" style={{ color: "#888888" }}>
                Pregunta sobre FAQs, documentos o procedimientos operacionales.
              </p>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className="space-y-3 animate-fadeIn">
            {/* User bubble */}
            <div className="flex justify-end">
              <div
                className="max-w-2xl rounded-2xl rounded-br-none px-4 py-3 border"
                style={{
                  backgroundColor: "#2A2000",
                  borderColor: "rgba(201,168,76,0.25)",
                  color: "#F5F5F5",
                }}
              >
                <p className="text-sm">{msg.user_message}</p>
              </div>
            </div>

            {/* Bot bubble */}
            <div className="flex justify-start">
              <div
                className="max-w-2xl rounded-2xl rounded-bl-none p-4 space-y-3 border"
                style={{
                  backgroundColor: msg.isRateLimit ? "rgba(201,168,76,0.06)" : "#1A1A1A",
                  borderColor: msg.isRateLimit ? "rgba(201,168,76,0.2)" : "#2A2A2A",
                }}
              >
                {msg.isLoading ? (
                  <div className="flex items-center gap-1.5">
                    <span
                      className="w-1.5 h-1.5 rounded-full animate-bounce"
                      style={{ backgroundColor: "#555555" }}
                    />
                    <span
                      className="w-1.5 h-1.5 rounded-full animate-bounce"
                      style={{ backgroundColor: "#555555", animationDelay: "0.15s" }}
                    />
                    <span
                      className="w-1.5 h-1.5 rounded-full animate-bounce"
                      style={{ backgroundColor: "#555555", animationDelay: "0.3s" }}
                    />
                    <span className="text-xs ml-1" style={{ color: "#888888" }}>
                      Procesando...
                    </span>
                  </div>
                ) : msg.isRateLimit ? (
                  <p className="text-sm" style={{ color: "#C9A84C" }}>
                    {msg.bot_message}
                  </p>
                ) : (
                  <>
                    <div className="text-sm leading-relaxed" style={{ color: "#F5F5F5" }}>
                      {msg.bot_message}
                    </div>

                    {msg.confidence > 0 && (
                      <div
                        className="text-xs font-medium"
                        style={{ color: getConfidenceColor(msg.confidence) }}
                      >
                        Confidence: {(msg.confidence * 100).toFixed(0)}%
                      </div>
                    )}

                    {msg.sources.length > 0 && (
                      <div className="border-t pt-3" style={{ borderColor: "#2A2A2A" }}>
                        <p
                          className="text-xs font-semibold mb-2 uppercase tracking-wider"
                          style={{ color: "#888888" }}
                        >
                          Fuentes
                        </p>
                        <div className="space-y-1.5">
                          {msg.sources.map((source, idx) => (
                            <div
                              key={idx}
                              className="text-xs rounded-lg px-3 py-2 border flex items-start gap-2"
                              style={{
                                backgroundColor: "#111111",
                                borderColor: "#2A2A2A",
                              }}
                            >
                              <span style={{ color: "#C9A84C" }}>
                                {source.type === "FAQ" ? "?" : "↗"}
                              </span>
                              <div>
                                <p className="font-medium" style={{ color: "#F5F5F5" }}>
                                  {source.name || source.title}
                                </p>
                                <p style={{ color: "#555555" }}>Score: {source.score}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
        ))}

        {error && (
          <div className="flex justify-center">
            <div
              className="px-4 py-3 rounded-lg border text-sm"
              style={{
                backgroundColor: "rgba(229,62,62,0.08)",
                borderColor: "rgba(229,62,62,0.3)",
                color: "#E53E3E",
              }}
            >
              {error}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div
        className="border-t px-6 py-4 shrink-0"
        style={{ borderColor: "#2A2A2A", backgroundColor: "#111111" }}
      >
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Escribe tu pregunta..."
            disabled={loading}
            className="input flex-1"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="btn btn-primary gap-2"
          >
            <Send size={14} strokeWidth={2} />
            {loading ? "..." : "Enviar"}
          </button>
        </form>
      </div>
    </div>
  );
}
