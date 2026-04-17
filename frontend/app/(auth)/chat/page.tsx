"use client";

import { apiFetch } from "@/lib/api";
import { ChatMessageResponse } from "@/lib/types";
import Link from "next/link";
import { FormEvent, useEffect, useRef, useState } from "react";

interface LocalMessage {
  id: string;
  user_message: string;
  bot_message: string;
  created_at: string;
  isLoading?: boolean;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<LocalMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    
    const userMessage = input.trim();
    if (!userMessage) return;

    setError(null);
    setInput("");
    setLoading(true);

    // Optimistically add user message
    const tempId = `temp_${Date.now()}`;
    setMessages((prev) => [
      ...prev,
      {
        id: tempId,
        user_message: userMessage,
        bot_message: "",
        created_at: new Date().toISOString(),
        isLoading: true,
      },
    ]);

    try {
      const response: ChatMessageResponse = await apiFetch("/chat/messages", {
        method: "POST",
        body: JSON.stringify({ message: userMessage }),
      });

      // Replace temp message with actual response
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === tempId
            ? {
                ...response,
                isLoading: false,
              }
            : msg
        )
      );
    } catch (err: any) {
      setError(err.message || "Failed to send message");
      // Remove the failed message
      setMessages((prev) => prev.filter((msg) => msg.id !== tempId));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="sticky top-0 z-10 border-b border-slate-200 bg-white shadow-sm">
        <div className="mx-auto flex max-w-2xl items-center justify-between px-6 py-4">
          <div>
            <Link
              href="/dashboard"
              className="text-sm text-indigo-600 hover:text-indigo-700 font-medium transition-colors"
            >
              ← Back to Dashboard
            </Link>
            <h1 className="mt-3 text-3xl font-bold text-slate-900">
              Chat Assistant
            </h1>
            <p className="mt-1 text-sm text-slate-600">
              Ask questions about your operational knowledge base
            </p>
          </div>
        </div>
      </header>

      <main className="flex-1 mx-auto w-full max-w-2xl px-6 py-6 flex flex-col">
        {/* Messages container */}
        <div className="flex-1 overflow-y-auto mb-6 space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 text-center">
              <div className="w-16 h-16 mb-6 rounded-2xl bg-indigo-100 flex items-center justify-center text-2xl">
                💬
              </div>
              <h2 className="text-2xl font-bold text-slate-900 mb-3">
                Start a conversation
              </h2>
              <p className="text-slate-600 max-w-sm leading-relaxed">
                Ask OperaBot questions about your operational knowledge base. 
                I'll search through your FAQ and provide helpful answers.
              </p>
            </div>
          ) : (
            <>
              {messages.map((msg) => (
                <div key={msg.id} className="space-y-3">
                  {/* User message */}
                  <div className="flex justify-end">
                    <div className="chat-bubble-user">
                      <p className="break-words whitespace-pre-wrap text-sm">{msg.user_message}</p>
                    </div>
                  </div>

                  {/* Bot message */}
                  {msg.isLoading ? (
                    <div className="flex justify-start">
                      <div className="chat-bubble bg-slate-100 border border-slate-200">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="flex justify-start">
                      <div className="chat-bubble-bot">
                        <p className="break-words whitespace-pre-wrap text-sm">{msg.bot_message}</p>
                      </div>
                    </div>
                  )}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Error message */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 font-medium">
            ⚠️ {error}
          </div>
        )}

        {/* Input form */}
        <form onSubmit={handleSubmit} className="border-t border-slate-200 bg-white pt-4 pb-2 rounded-t-lg">
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
              placeholder="Ask something..."
              className="input flex-1"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="btn btn-primary"
            >
              {loading ? (
                <>
                  <svg
                    className="w-4 h-4 animate-spin"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Sending...
                </>
              ) : (
                "Send"
              )}
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}
