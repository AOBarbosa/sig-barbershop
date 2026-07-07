import type React from "react";

export function AtendimentoFieldError({
  children,
  message
}: {
  children: React.ReactNode;
  message?: string;
}) {
  return (
    <div className="flex flex-col gap-2">
      {children}
      {message ? <p className="text-destructive text-sm">{message}</p> : null}
    </div>
  );
}
