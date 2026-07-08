"use client";

import { QueryClientProvider } from "@tanstack/react-query";

import { AuthProvider } from "@/hooks/useAuth";
import { queryClient } from "@/lib/queryClient";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>{children}</AuthProvider>
    </QueryClientProvider>
  );
}
