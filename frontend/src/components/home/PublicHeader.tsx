"use client";

import Link from "next/link";
import { LogOut, Repeat2, UserRound } from "lucide-react";
import { useRouter } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";

export function PublicHeader() {
  const router = useRouter();
  const { logout, user } = useAuth();

  async function handleLogout() {
    await logout();
    router.refresh();
  }

  async function handleSwitchAccount() {
    await logout();
    router.push("/login");
  }

  return (
    <header className="absolute inset-x-0 top-0 z-20">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
        <Link href="/" className="text-sm font-semibold text-white">
          O Teu Barbeiro
        </Link>
        {user ? (
          <div className="flex min-w-0 items-center gap-2 text-white">
            <UserRound className="size-4 shrink-0" />
            <div className="hidden min-w-0 text-right sm:block">
              <p className="truncate text-sm font-medium">{user.nome}</p>
              <p className="text-xs text-white/70">{user.role}</p>
            </div>
            <Badge className="bg-white/15 text-white">Logado</Badge>
            <Button
              type="button"
              size="sm"
              variant="secondary"
              onClick={handleSwitchAccount}>
              <Repeat2 className="size-4" />
              Trocar
            </Button>
            <Button
              type="button"
              size="sm"
              variant="outline"
              className="border-white/30 bg-white/10 text-white hover:bg-white/20 hover:text-white"
              onClick={handleLogout}>
              <LogOut className="size-4" />
              Sair
            </Button>
          </div>
        ) : (
          <Button asChild size="sm" variant="secondary">
            <Link href="/login">Entrar</Link>
          </Button>
        )}
      </div>
    </header>
  );
}
