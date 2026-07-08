"use client";

import { createContext, useContext, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  getCurrentUser,
  login,
  logout as logoutRequest
} from "@/services/authService";
import type { LoginPayload, UsuarioAtual } from "@/types/auth";

const authQueryKey = ["auth", "me"];

interface AuthContextValue {
  isLoading: boolean;
  login: (payload: LoginPayload) => Promise<UsuarioAtual>;
  loginError: Error | null;
  logout: () => Promise<void>;
  user: UsuarioAtual | null;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const userQuery = useQuery({
    queryKey: authQueryKey,
    queryFn: getCurrentUser,
    retry: false
  });
  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: (user) => {
      queryClient.setQueryData(authQueryKey, user);
    }
  });
  const logoutMutation = useMutation({
    mutationFn: logoutRequest,
    onSuccess: () => {
      queryClient.setQueryData(authQueryKey, null);
      void queryClient.invalidateQueries({ queryKey: authQueryKey });
    }
  });

  return (
    <AuthContext.Provider
      value={{
        isLoading: userQuery.isLoading,
        login: loginMutation.mutateAsync,
        loginError: loginMutation.error,
        logout: logoutMutation.mutateAsync,
        user: userQuery.data ?? null
      }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth deve ser usado dentro de AuthProvider");
  }

  return context;
}
