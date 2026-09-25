import Link from "next/link";
import LoginForm from "@/components/Auth/LoginForm";

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-bg">
      <div className="w-full max-w-md">
        <div className="card card-padding">
          <div className="mb-8 text-center">
            <h1 className="text-3xl font-bold tracking-tight text-gold">
              OperaBot
            </h1>
            <p className="text-sm mt-2 text-text-secondary">
              Operational Knowledge Assistant
            </p>
          </div>

          <LoginForm />

          <p className="text-center text-sm mt-6 text-text-secondary">
            New to OperaBot?{" "}
            <Link href="/register" className="font-medium text-gold">
              Create an account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
