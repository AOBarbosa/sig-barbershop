describe("Autenticação frontend", () => {
  beforeEach(() => {
    cy.clearCookie("access_token");
  });

  it("redireciona rotas protegidas para login quando não há sessão", () => {
    cy.visit("/clientes");

    cy.location("pathname").should("eq", "/login");
    cy.location("search").should("contain", "next=%2Fclientes");
    cy.contains("Entrar no SIG Barbershop").should("be.visible");
  });

  it("realiza login e redireciona para a rota solicitada", () => {
    cy.createTestToken("funcionario").then((funcionarioToken) => {
      cy.intercept("POST", "**/auth/login", {
        statusCode: 200,
        headers: {
          "set-cookie": `access_token=${funcionarioToken}; Path=/; HttpOnly; SameSite=Lax`
        },
        body: {
          id_pessoa: 99,
          nome: "Funcionario Teste",
          email: "funcionario@teste.com",
          role: "funcionario"
        }
      }).as("login");
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

    cy.visit("/login?next=/servicos");
    cy.get("input[name='email']").type("funcionario@teste.com");
    cy.get("input[name='senha']").type("senha123");
    cy.contains("button", "Entrar").click();

    cy.wait("@login").its("request.body").should("deep.equal", {
      email: "funcionario@teste.com",
      senha: "senha123"
    });
    cy.createTestToken("funcionario").then((funcionarioToken) => {
      cy.setCookie("access_token", funcionarioToken);
      cy.visit("/servicos");
      cy.location("pathname").should("eq", "/servicos");
    });
  });

  it("mostra erro de autenticação inválida", () => {
    cy.intercept("POST", "**/auth/login", {
      statusCode: 401,
      body: { detail: "Email ou senha invalidos" }
    }).as("loginInvalido");

    cy.visit("/login");
    cy.get("input[name='email']").type("errado@teste.com");
    cy.get("input[name='senha']").type("senhaerrada");
    cy.contains("button", "Entrar").click();

    cy.wait("@loginInvalido");
    cy.contains("Email ou senha invalidos").should("be.visible");
  });

  it("bloqueia rota de funcionário para usuário cliente", () => {
    cy.loginAsCliente();

    cy.visit("/clientes");

    cy.location("pathname").should("eq", "/atendimentos");
  });

  it("faz logout e volta para login", () => {
    cy.loginAsFuncionario();
    cy.intercept("POST", "**/auth/logout", {
      statusCode: 204,
      headers: {
        "set-cookie": "access_token=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax"
      }
    }).as("logout");

    cy.visit("/app");
    cy.contains("Funcionario Teste").should("be.visible");
    cy.contains("button", "Sair").click();

    cy.wait("@logout");
    cy.clearCookie("access_token");
    cy.visit("/login");
    cy.location("pathname").should("eq", "/login");
  });
});
