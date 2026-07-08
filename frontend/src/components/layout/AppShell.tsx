"use client";

import {
  CalendarClock,
  Home,
  LogOut,
  Menu,
  Package,
  Scissors,
  ShoppingCart,
  Star,
  UserCog,
  Users
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetTitle,
  SheetTrigger
} from "@/components/ui/sheet";
import { useAuth } from "@/hooks/useAuth";
import { cn } from "@/lib/utils";

const navigationGroups = [
  {
    label: "Visão geral",
    items: [{ href: "/app", label: "Início", icon: Home }]
  },
  {
    label: "Operação",
    items: [
      { href: "/servicos", label: "Serviços", icon: Scissors },
      { href: "/atendimentos", label: "Atendimentos", icon: CalendarClock },
      { href: "/clientes", label: "Clientes", icon: Users },
      { href: "/barbeiros", label: "Barbeiros", icon: UserCog }
    ]
  },
  {
    label: "Comercial",
    items: [
      { href: "/produtos", label: "Produtos", icon: Package },
      { href: "/vendas", label: "Vendas", icon: ShoppingCart },
      { href: "/fidelidade", label: "Fidelidade", icon: Star }
    ]
  }
];

function getCurrentRoute(pathname: string) {
  const items = navigationGroups.flatMap((group) => group.items);

  return (
    items.find((item) =>
      item.href === "/"
        ? pathname === item.href
        : pathname.startsWith(item.href)
    ) ?? items[0]
  );
}

function SidebarContent({ pathname }: { pathname: string }) {
  return (
    <div className="bg-sidebar text-sidebar-foreground flex h-full flex-col">
      <div className="flex h-16 flex-col justify-center border-b px-4">
        <p className="text-base font-semibold tracking-tight">SIG Barbershop</p>
        <p className="text-muted-foreground text-xs">Gestão operacional</p>
      </div>
      <nav className="flex flex-1 flex-col gap-4 p-3">
        {navigationGroups.map((group) => (
          <div key={group.label} className="space-y-1">
            <p className="text-muted-foreground px-3 text-xs font-medium">
              {group.label}
            </p>
            {group.items.map((item) => {
              const Icon = item.icon;
              const active =
                item.href === "/"
                  ? pathname === item.href
                  : pathname.startsWith(item.href);

              return (
                <Button
                  key={item.href}
                  asChild
                  variant={active ? "secondary" : "ghost"}
                  className={cn(
                    "h-9 justify-start gap-2 px-3",
                    active && "bg-sidebar-accent text-sidebar-accent-foreground"
                  )}>
                  <Link href={item.href}>
                    <Icon className="size-4" />
                    {item.label}
                  </Link>
                </Button>
              );
            })}
          </div>
        ))}
      </nav>
      <div className="border-t p-3">
        <div className="bg-muted/60 rounded-lg p-3">
          <p className="text-sm font-medium">Equipe da barbearia</p>
          <p className="text-muted-foreground text-xs">Ambiente acadêmico</p>
        </div>
      </div>
    </div>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { logout, user } = useAuth();
  const currentRoute = getCurrentRoute(pathname);

  if (pathname === "/" || pathname.startsWith("/login")) {
    return <>{children}</>;
  }

  async function handleLogout() {
    await logout();
    router.push("/login");
  }

  return (
    <div className="bg-background min-h-screen">
      <aside className="bg-sidebar fixed inset-y-0 left-0 hidden w-64 border-r lg:block">
        <SidebarContent pathname={pathname} />
      </aside>
      <div className="flex min-h-screen flex-col lg:pl-64">
        <header className="bg-background/95 sticky top-0 z-20 border-b backdrop-blur">
          <div className="mx-auto flex h-16 w-full max-w-7xl items-center gap-3 px-4 lg:px-8">
            <Sheet>
              <SheetTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="lg:hidden"
                  aria-label="Abrir menu">
                  <Menu className="size-5" />
                </Button>
              </SheetTrigger>
              <SheetContent
                side="left"
                className="w-72 p-0"
                data-testid="mobile-sidebar">
                <SheetTitle className="sr-only">Menu principal</SheetTitle>
                <SidebarContent pathname={pathname} />
              </SheetContent>
            </Sheet>
            <div className="min-w-0">
              <p className="truncate text-sm font-medium">
                {currentRoute.label}
              </p>
              <p className="text-muted-foreground text-xs">
                Controle de serviços, atendimentos e vendas
              </p>
            </div>
            <div className="ml-auto flex min-w-0 items-center gap-2">
              {user ? (
                <div className="hidden min-w-0 text-right sm:block">
                  <p className="truncate text-sm font-medium">{user.nome}</p>
                  <p className="text-muted-foreground text-xs">{user.role}</p>
                </div>
              ) : null}
              {user ? (
                <Button variant="outline" size="sm" onClick={handleLogout}>
                  <LogOut className="size-4" />
                  Sair
                </Button>
              ) : (
                <Button asChild variant="outline" size="sm">
                  <Link href={`/login?next=${encodeURIComponent(pathname)}`}>
                    Entrar
                  </Link>
                </Button>
              )}
            </div>
          </div>
        </header>
        <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6 lg:px-8">
          {children}
        </main>
      </div>
    </div>
  );
}
