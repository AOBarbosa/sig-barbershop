describe("Módulo Clientes - listagem", () => {
  beforeEach(() => {
    cy.fixture("clientes").as("clientesFixture");
  });

  it("lista clientes com dados formatados e navega pelo shell", function () {
    cy.viewport(1280, 720);
    cy.intercept(
      {
        method: "GET",
        pathname: "/clientes",
        headers: { accept: "application/json, text/plain, */*" }
      },
      { statusCode: 200, body: this.clientesFixture.clientes }
    ).as("listarClientes");
    cy.intercept(
      {
        method: "GET",
        pathname: "/pessoas",
        headers: { accept: "application/json, text/plain, */*" }
      },
      { statusCode: 200, body: this.clientesFixture.pessoas }
    ).as("listarPessoas");

    cy.visit("/clientes");
    cy.wait(["@listarClientes", "@listarPessoas"]);

    cy.contains("SIG Barbershop").should("be.visible");
    cy.contains("Clientes").should("be.visible");
    cy.contains("Maria Silva").should("be.visible");
    cy.contains("123.456.789-01").should("be.visible");
    cy.contains("Joao Souza").should("be.visible");
    cy.contains("Ana Costa").should("be.visible");
    cy.contains("Total de clientes").should("be.visible");
    cy.contains("Com email").should("be.visible");
    cy.contains("Novo cliente").should("have.attr", "href", "/clientes/novo");
  });

  it("filtra clientes por nome, CPF e email", function () {
    cy.intercept(
      {
        method: "GET",
        pathname: "/clientes",
        headers: { accept: "application/json, text/plain, */*" }
      },
      { statusCode: 200, body: this.clientesFixture.clientes }
    ).as("listarClientes");
    cy.intercept(
      {
        method: "GET",
        pathname: "/pessoas",
        headers: { accept: "application/json, text/plain, */*" }
      },
      { statusCode: 200, body: this.clientesFixture.pessoas }
    ).as("listarPessoas");

    cy.visit("/clientes");
    cy.wait(["@listarClientes", "@listarPessoas"]);

    cy.get("input[placeholder='Buscar cliente']").type("maria");
    cy.contains("Maria Silva").should("be.visible");
    cy.contains("Joao Souza").should("not.exist");

    cy.get("input[placeholder='Buscar cliente']").clear().type("ana@");
    cy.contains("Ana Costa").should("be.visible");
    cy.contains("Maria Silva").should("not.exist");
  });

  it("mostra estado vazio filtrado e expõe ação de editar", function () {
    cy.intercept(
      {
        method: "GET",
        pathname: "/clientes",
        headers: { accept: "application/json, text/plain, */*" }
      },
      { statusCode: 200, body: this.clientesFixture.clientes }
    ).as("listarClientes");
    cy.intercept(
      {
        method: "GET",
        pathname: "/pessoas",
        headers: { accept: "application/json, text/plain, */*" }
      },
      { statusCode: 200, body: this.clientesFixture.pessoas }
    ).as("listarPessoas");

    cy.visit("/clientes");
    cy.wait(["@listarClientes", "@listarPessoas"]);

    cy.get("button[aria-label='Abrir ações do cliente Maria Silva']")
      .filter(":visible")
      .first()
      .click();
    cy.contains("Editar").should("have.attr", "href", "/clientes/1/editar");

    cy.visit("/clientes");
    cy.wait(["@listarClientes", "@listarPessoas"]);

    cy.get("input[placeholder='Buscar cliente']").type("não existe");
    cy.contains("Nenhum cliente encontrado").should("be.visible");
    cy.contains("Cadastrar cliente").should(
      "have.attr",
      "href",
      "/clientes/novo"
    );
  });

  it("mostra erro quando a API retorna uma lista inválida", () => {
    cy.intercept(
      {
        method: "GET",
        pathname: "/clientes",
        headers: { accept: "application/json, text/plain, */*" }
      },
      { statusCode: 200, body: { detail: "rota incorreta" } }
    ).as("listarClientesFormatoInvalido");
    cy.intercept(
      {
        method: "GET",
        pathname: "/pessoas",
        headers: { accept: "application/json, text/plain, */*" }
      },
      { statusCode: 200, body: [] }
    ).as("listarPessoasVazia");

    cy.visit("/clientes");

    cy.contains("Resposta inválida ao listar clientes").should("be.visible");
    cy.contains("Runtime TypeError").should("not.exist");
  });

  it("mantém a listagem e o menu principal responsivos no mobile", function () {
    cy.viewport("iphone-x");
    cy.intercept(
      {
        method: "GET",
        pathname: "/clientes",
        headers: { accept: "application/json, text/plain, */*" }
      },
      { statusCode: 200, body: this.clientesFixture.clientes }
    ).as("listarClientes");
    cy.intercept(
      {
        method: "GET",
        pathname: "/pessoas",
        headers: { accept: "application/json, text/plain, */*" }
      },
      { statusCode: 200, body: this.clientesFixture.pessoas }
    ).as("listarPessoas");

    cy.visit("/clientes");
    cy.wait(["@listarClientes", "@listarPessoas"]);

    cy.get("main").contains("Clientes").should("be.visible");
    cy.get("button[aria-label='Abrir menu']").click();
    cy.get("[data-testid='mobile-sidebar']").within(() => {
      cy.contains("SIG Barbershop").should("be.visible");
      cy.contains("Clientes").should("be.visible");
    });
    cy.get("input[placeholder='Buscar cliente']").should("be.visible");
    cy.get("[data-testid='clientes-mobile-list']")
      .contains("Maria Silva")
      .should("be.visible");
  });
});
