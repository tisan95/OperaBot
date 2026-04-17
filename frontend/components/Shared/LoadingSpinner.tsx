"use client";

export default function LoadingSpinner() {
  return (
    <div className="flex justify-center items-center">
      <div className="relative w-12 h-12">
        <div className="absolute inset-0 rounded-full border-4 border-indigo-100"></div>
        <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-indigo-600 border-r-indigo-600 animate-spin"></div>
      </div>
    </div>
  );
}
