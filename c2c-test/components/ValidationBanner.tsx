import { AlertTriangle } from "lucide-react";

type ValidationBannerProps = {
  message: string | null;
};

export function ValidationBanner({ message }: ValidationBannerProps) {
  if (!message) {
    return null;
  }

  return (
    <div className="flex items-start gap-3 rounded-lg border border-rose/35 bg-rose/10 px-4 py-3 text-sm text-rose">
      <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-rose" aria-hidden="true" />
      <p>{message}</p>
    </div>
  );
}
