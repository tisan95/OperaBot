import { type LucideIcon } from "lucide-react";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export default function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="w-14 h-14 rounded-full flex items-center justify-center border bg-card border-border mb-4">
        <Icon size={22} strokeWidth={1.5} className="text-muted" />
      </div>
      <p className="text-sm font-semibold text-text-primary mb-1">{title}</p>
      {description && (
        <p className="text-xs text-muted max-w-xs leading-relaxed">{description}</p>
      )}
      {action && (
        <button onClick={action.onClick} className="btn btn-secondary btn-sm mt-4">
          {action.label}
        </button>
      )}
    </div>
  );
}
