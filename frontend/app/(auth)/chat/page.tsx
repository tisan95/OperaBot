"use client";

import { apiFetch } from "@/lib/api";
import { FormEvent, useEffect, useRef, useState } from "react";

interface Source {
  type: string;
  title: string;
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
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load chat history
  useEffect(() => {
    loadHistory();
  }, []);

  // Auto-scroll to bottom
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

    // Optimistically add user message
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

      // Replace loading message with actual response
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
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to send message"
      );
      // Remove the loading message
      setMessages((prev) => prev.filter((msg) => msg.id !== tempId));
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return "text-green-600";
    if (confidence >= 0.6) return "text-yellow-600";
    return "text-red-600";
  };

  return (
    <div className="flex flex-col h-[calc(100vh-200px)] bg-white border border-slate-200 rounded-lg shadow-sm">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-50 to-blue-50 border-b border-slate-200 px-6 py-4">
        <h1 className="text-2xl font-bold text-slate-900">💬 Chat</h1>
        <p className="text-sm text-slate-600 mt-1">
          Ask questions about your operational knowledge base
        </p>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="text-6xl mb-4">💭</div>
              <h2 className="text-2xl font-bold text-slate-900 mb-2">
                Start a conversation
              </h2>
              <p className="text-slate-600 max-w-md">
                Ask questions about FAQs, documents, or operational procedures.
                The AI will search your knowledge base and provide answers with sources.
              </p>
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={msg.id} className="space-y-3">
            {/* User Message */}
            <div className="flex justify-end">
              <div className="max-w-2xl bg-gradient-to-r from-sky-500 to-blue-600 text-white rounded-lg px-4 py-3 shadow-sm">
                <p className="text-sm">{msg.user_message}</p>
              </div>
            </div>

            {/* Bot Response with Sources */}
            <div className="flex justify-start">
              <div className="max-w-2xl bg-white border border-slate-200 rounded-lg shadow-sm p-4 space-y-3">
                {msg.isLoading ? (
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-100"></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-200"></div>
                    <span className="text-sm text-slate-600 ml-2">Thinking...</span>
                  </div>
                ) : (
                  <>
                    {/* Answer */}
                    <div className="text-sm text-slate-900 leading-relaxed">
                      {msg.bot_message}
                    </div>

                    {/* Confidence Score */}
                    {msg.confidence > 0 && (
                      <div className={`text-xs font-semibold ${getConfidenceColor(msg.confidence)}`}>
                        Confidence: {(msg.confidence * 100).toFixed(0)}%
                      </div>
                    )}

                    {/* Sources */}
                    {msg.sources.length > 0 && (
                      <div className="border-t border-slate-200 pt-3">
                        <p className="text-xs font-semibold text-slate-700 mb-2">
                          📚 Sources:
                        </p>
                        <div className="space-y-2">
                          {msg.sources.map((source, idx) => (
                            <div
                              key={idx}
                              className="text-xs bg-slate-50 border border-slate-200 rounded p-2 flex items-start space-x-2"
                            >
                              <span className="font-semibold text-slate-600 min-w-fit">
                                {source.type === "FAQ" ? "❓" : "📄"}
                              </span>
                              <div>
                                <p className="font-semibold text-slate-700 truncate">
                                  {source.title}
                                </p>
                                <p className="text-slate-500">
                                  Score: {source.score}
                                </p>
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
            <div className="max-w-2xl bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm text-red-700">
              ❌ {error}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-slate-200 bg-white px-6 py-4">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            disabled={loading}
            className="flex-1 px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-slate-100"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-slate-400 font-semibold transition"
          >
            {loading ? "..." : "Send"}
          </button>
        </form>
      </div>
    </div>
  );
}
