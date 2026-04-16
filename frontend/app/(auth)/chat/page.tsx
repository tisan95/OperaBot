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
      <header className="border-b bg-white sticky top-0 z-10">
        <div className="mx-auto flex max-w-2xl items-center justify-between px-6 py-4">
          <div>
            <Link
              href="/dashboard"
              className="text-sm text-sky-600 hover:underline"
            >
              ← Back to dashboard
            </Link>
            <h1 className="mt-2 text-3xl font-semibold text-slate-900">
              Chat with OperaBot
            </h1>
            <p className="mt-1 text-sm text-slate-500">
              Ask questions about your operational knowledge base
            </p>
          </div>
        </div>
      </header>

      <main className="flex-1 mx-auto w-full max-w-2xl px-6 py-6 flex flex-col">
        {/* Messages container */}
        <div className="flex-1 overflow-y-auto mb-6 space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="text-5xl mb-4">💬</div>
              <h2 className="text-xl font-semibold text-slate-900 mb-2">
                Start a conversation
              </h2>
              <p className="text-slate-600 max-w-sm">
                Ask OperaBot any questions about your operational knowledge base.
                I'll search the FAQ and provide helpful answers.
              </p>
            </div>
          ) : (
            <>
              {messages.map((msg) => (
                <div key={msg.id} className="space-y-3">
                  {/* User message */}
                  <div className="flex justify-end">
                    <div className="max-w-xs bg-sky-600 text-white rounded-2xl px-4 py-3 text-sm">
                      <p className="break-words whitespace-pre-wrap">{msg.user_message}</p>
                    </div>
                  </div>

                  {/* Bot message */}
                  {msg.isLoading ? (
                    <div className="flex justify-start">
                      <div className="bg-white border border-slate-200 rounded-2xl px-4 py-3 text-sm">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="flex justify-start">
                      <div className="max-w-xs bg-white border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-900">
                        <p className="break-words whitespace-pre-wrap">{msg.bot_message}</p>
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
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Input form */}
        <form onSubmit={handleSubmit} className="border-t bg-white pt-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
              placeholder="Ask a question..."
              className="flex-1 px-4 py-2 rounded-xl border border-slate-300 shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent text-sm disabled:bg-slate-100 disabled:cursor-not-allowed"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="inline-flex items-center gap-2 px-6 py-2 bg-sky-600 text-white rounded-xl font-medium hover:bg-sky-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition text-sm"
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
