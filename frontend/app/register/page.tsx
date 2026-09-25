import Link from "next/link";
import RegisterForm from "@/components/Auth/RegisterForm";

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-bg">
      <div className="w-full max-w-md">
        <div className="card card-padding">
          <div className="mb-8 text-center">
            <h1 className="text-3xl font-bold tracking-tight text-gold">
              OperaBot
            </h1>
            <p className="text-sm mt-2 text-text-secondary">
              Crea tu cuenta
            </p>
          </div>

          <RegisterForm />

          <p className="text-center text-sm mt-6 text-text-secondary">
            ¿Ya tienes una cuenta?{" "}
            <Link href="/" className="font-medium text-gold">
              Inicia sesión
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
