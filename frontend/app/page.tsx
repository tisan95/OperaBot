import Link from "next/link";
import LoginForm from "@/components/Auth/LoginForm";
import { redirect } from "next/navigation";

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-lg shadow-md p-8">
          <h1 className="text-3xl font-bold text-center text-gray-900 mb-2">
            OperaBot
          </h1>
          <p className="text-center text-gray-600 mb-8">
            Operational Knowledge Assistant
          </p>

          <LoginForm />

          <p className="text-center text-gray-600 mt-6">
            New to OperaBot?{" "}
            <Link href="/register" className="text-blue-600 hover:underline font-medium">
              Create an account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
