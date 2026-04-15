import Link from "next/link";
import RegisterForm from "@/components/Auth/RegisterForm";

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-lg shadow-md p-8">
          <h1 className="text-3xl font-bold text-center text-gray-900 mb-2">
            OperaBot
          </h1>
          <p className="text-center text-gray-600 mb-8">
            Create your account
          </p>

          <RegisterForm />

          <p className="text-center text-gray-600 mt-6">
            Already have an account?{" "}
            <Link href="/" className="text-blue-600 hover:underline font-medium">
              Login
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
