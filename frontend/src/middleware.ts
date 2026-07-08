import { jwtVerify } from "jose";
import { NextResponse, type NextRequest } from "next/server";

type Role = "admin" | "funcionario" | "cliente";

const COOKIE_NAME = "access_token";
const JWT_SECRET =
  process.env.JWT_SECRET ??
  ["dev", "secret", "troque", "em", "producao", "32", "bytes+"].join("-");

const funcionarioRoutes = [
  "/barbeiros",
  "/clientes",
  "/fidelidade",
  "/produtos",
  "/servicos",
  "/vendas"
];

function isFuncionarioRoute(pathname: string) {
  return funcionarioRoutes.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`)
  );
}

function loginUrl(request: NextRequest) {
  const url = request.nextUrl.clone();
  const next = `${request.nextUrl.pathname}${request.nextUrl.search}`;

  url.pathname = "/login";
  url.search = "";
  url.searchParams.set("next", next);
  return url;
}

async function getRole(token: string): Promise<Role | null> {
  try {
    const secret = new TextEncoder().encode(JWT_SECRET);
    const { payload } = await jwtVerify(token, secret);
    const role = payload.role;

    if (role === "admin" || role === "funcionario" || role === "cliente") {
      return role;
    }
  } catch {
    return null;
  }

  return null;
}

export async function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  const token = request.cookies.get(COOKIE_NAME)?.value;

  if (pathname === "/" || pathname.startsWith("/agendar")) {
    return NextResponse.next();
  }

  if (pathname.startsWith("/login")) {
    if (!token) {
      return NextResponse.next();
    }

    const role = await getRole(token);
    return role
      ? NextResponse.redirect(new URL("/", request.url))
      : NextResponse.next();
  }

  if (!token) {
    return NextResponse.redirect(loginUrl(request));
  }

  const role = await getRole(token);

  if (!role) {
    const response = NextResponse.redirect(loginUrl(request));
    response.cookies.delete(COOKIE_NAME);
    return response;
  }

  if (role === "cliente" && isFuncionarioRoute(pathname)) {
    return NextResponse.redirect(new URL("/atendimentos", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"]
};
