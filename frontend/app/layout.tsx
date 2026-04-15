import type { Metadata } from "next";
import { AuthProvider } from "@/components/Auth/AuthProvider";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "OperaBot - Operational Knowledge Assistant",
  description:
    "AI-powered assistant for operational knowledge in manufacturing and logistics",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-white text-gray-900">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
