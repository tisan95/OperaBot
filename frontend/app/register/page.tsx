import Link from "next/link";
import RegisterForm from "@/components/Auth/RegisterForm";

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4" style={{ backgroundColor: "#0A0A0A" }}>
      <div className="w-full max-w-md">
        <div className="card card-padding">
          <div className="mb-8 text-center">
            <h1 className="text-3xl font-bold tracking-tight" style={{ color: "#C9A84C" }}>
              OperaBot
            </h1>
            <p className="text-sm mt-2" style={{ color: "#888888" }}>
              Create your account
            </p>
          </div>

          <RegisterForm />

          <p className="text-center text-sm mt-6" style={{ color: "#888888" }}>
            Already have an account?{" "}
            <Link href="/" className="font-medium" style={{ color: "#C9A84C" }}>
              Login
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
