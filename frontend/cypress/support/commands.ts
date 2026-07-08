type TestRole = "cliente" | "funcionario";

const testSecret = [
  "dev",
  "secret",
  "troque",
  "em",
  "producao",
  "32",
  "bytes+"
].join("-");

function toBase64Url(value: string | ArrayBuffer) {
  const bytes =
    typeof value === "string"
      ? new TextEncoder().encode(value)
      : new Uint8Array(value);
  const binary = Array.from(bytes, (byte) => String.fromCharCode(byte)).join(
    ""
  );

  return btoa(binary)
    .replaceAll("+", "-")
    .replaceAll("/", "_")
    .replaceAll("=", "");
}

async function createTestToken(role: TestRole) {
  const sub = role === "cliente" ? "1" : "99";
  const header = toBase64Url(JSON.stringify({ alg: "HS256", typ: "JWT" }));
  const payload = toBase64Url(JSON.stringify({ sub, role, exp: 1893456000 }));
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(testSecret),
    { hash: "SHA-256", name: "HMAC" },
    false,
    ["sign"]
  );
  const signature = await crypto.subtle.sign(
    "HMAC",
    key,
    new TextEncoder().encode(`${header}.${payload}`)
  );

  return `${header}.${payload}.${toBase64Url(signature)}`;
}

Cypress.Commands.add("loginAsFuncionario", () => {
  cy.then(() => createTestToken("funcionario")).then((token) => {
    cy.setCookie("access_token", token);
  });
  cy.intercept("GET", "**/auth/me", {
    statusCode: 200,
    body: {
      id_pessoa: 99,
      nome: "Funcionario Teste",
      email: "funcionario@teste.com",
      role: "funcionario"
    }
  }).as("usuarioAtual");
});

Cypress.Commands.add("loginAsCliente", () => {
  cy.then(() => createTestToken("cliente")).then((token) => {
    cy.setCookie("access_token", token);
  });
  cy.intercept("GET", "**/auth/me", {
    statusCode: 200,
    body: {
      id_pessoa: 1,
      nome: "Cliente Teste",
      email: "cliente@teste.com",
      role: "cliente"
    }
  }).as("usuarioAtualCliente");
});

beforeEach(() => {
  if (Cypress.spec.name !== "auth.cy.ts") {
    cy.loginAsFuncionario();
  }
});

declare global {
  namespace Cypress {
    interface Chainable {
      createTestToken(role: TestRole): Chainable<string>;
      loginAsCliente(): Chainable<void>;
      loginAsFuncionario(): Chainable<void>;
    }
  }
}

Cypress.Commands.add("createTestToken", (role: TestRole) => {
  return cy.then(() => createTestToken(role));
});

export {};
