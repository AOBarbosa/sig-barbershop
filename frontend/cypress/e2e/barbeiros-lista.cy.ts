describe("Módulo Barbeiros - listagem", () => {
  beforeEach(() => {
    cy.fixture("barbeiros").as("barbeirosFixture");
  });

  it("lista barbeiros com dados de pessoa e comissão", function () {
    cy.viewport(1280, 720);
    cy.intercept(
      {
        method: "GET",
        pathname: "/barbeiros",
        headers: { accept: "application/json, text/plain, */*" }
      },
      { statusCode: 200, body: this.barbeirosFixture.barbeiros }
    ).as("listarBarbeiros");
    cy.intercept(
      {
        method: "GET",
        pathname: "/pessoas",
        headers: { accept: "application/json, text/plain, */*" }
      },
      { statusCode: 200, body: this.barbeirosFixture.pessoas }
    ).as("listarPessoas");

    cy.visit("/barbeiros");
    cy.wait(["@listarBarbeiros", "@listarPessoas"]);

    cy.contains("Barbeiros").should("be.visible");
    cy.contains("Pedro Barreto").should("be.visible");
    cy.contains("Pedro").should("be.visible");
    cy.contains("40.00%").should("be.visible");
    cy.contains("Rafael Torres").should("be.visible");
    cy.contains("Diego Almeida").should("be.visible");
    cy.contains("Total de barbeiros").should("be.visible");
    cy.contains("Barbeiros cadastrados").should("be.visible");
    cy.contains("Apelidos").should("be.visible");
    cy.contains("Novo barbeiro").should(
      "have.attr",
      "href",
      "/barbeiros/novo"
    );
  });

  it("filtra barbeiros por busca", function () {
    cy.intercept(
      {
        method: "GET",
        pathname: "/barbeiros",
        headers: { accept: "application/json, text/plain, */*" }
      },
      { statusCode: 200, body: this.barbeirosFixture.barbeiros }
    ).as("listarBarbeiros");
    cy.intercept(
      {
        method: "GET",
        pathname: "/pessoas",
        headers: { accept: "application/json, text/plain, */*" }
      },
      { statusCode: 200, body: this.barbeirosFixture.pessoas }
    ).as("listarPessoas");

    cy.visit("/barbeiros");
    cy.wait(["@listarBarbeiros", "@listarPessoas"]);

    cy.get("input[placeholder='Buscar barbeiro']").type("pedro");
    cy.contains("Pedro Barreto").should("be.visible");
    cy.contains("Rafael Torres").should("not.exist");
  });

  it("mostra estado vazio filtrado e ação de editar", function () {
    cy.intercept(
      {
        method: "GET",
        pathname: "/barbeiros",
        headers: { accept: "application/json, text/plain, */*" }
      },
      { statusCode: 200, body: this.barbeirosFixture.barbeiros }
    ).as("listarBarbeiros");
    cy.intercept(
      {
        method: "GET",
        pathname: "/pessoas",
        headers: { accept: "application/json, text/plain, */*" }
      },
      { statusCode: 200, body: this.barbeirosFixture.pessoas }
    ).as("listarPessoas");

    cy.visit("/barbeiros");
    cy.wait(["@listarBarbeiros", "@listarPessoas"]);

    cy.get("button[aria-label='Abrir ações do barbeiro Pedro Barreto']")
      .filter(":visible")
      .first()
      .click();
    cy.contains("Editar").should("have.attr", "href", "/barbeiros/10/editar");

    cy.visit("/barbeiros");
    cy.wait(["@listarBarbeiros", "@listarPessoas"]);

    cy.get("input[placeholder='Buscar barbeiro']").type("não existe");
    cy.contains("Nenhum barbeiro encontrado").should("be.visible");
    cy.contains("Cadastrar barbeiro").should(
      "have.attr",
      "href",
      "/barbeiros/novo"
    );
  });

  it("mostra erro quando a API retorna uma lista inválida", () => {
    cy.intercept(
      {
        method: "GET",
        pathname: "/barbeiros",
        headers: { accept: "application/json, text/plain, */*" }
      },
      { statusCode: 200, body: { detail: "erro" } }
    ).as("listarBarbeirosInvalido");
    cy.intercept(
      {
        method: "GET",
        pathname: "/pessoas",
        headers: { accept: "application/json, text/plain, */*" }
      },
      { statusCode: 200, body: [] }
    ).as("listarPessoasVazia");

    cy.visit("/barbeiros");

    cy.contains("Resposta inválida ao listar barbeiros").should("be.visible");
  });

  it("mantém a listagem responsiva no mobile", function () {
    cy.viewport("iphone-x");
    cy.intercept(
      {
        method: "GET",
        pathname: "/barbeiros",
        headers: { accept: "application/json, text/plain, */*" }
      },
      { statusCode: 200, body: this.barbeirosFixture.barbeiros }
    ).as("listarBarbeiros");
    cy.intercept(
      {
        method: "GET",
        pathname: "/pessoas",
        headers: { accept: "application/json, text/plain, */*" }
      },
      { statusCode: 200, body: this.barbeirosFixture.pessoas }
    ).as("listarPessoas");

    cy.visit("/barbeiros");
    cy.wait(["@listarBarbeiros", "@listarPessoas"]);

    cy.get("main").contains("Barbeiros").should("be.visible");
    cy.get("[data-testid='barbeiros-mobile-list']")
      .contains("Pedro Barreto")
      .should("be.visible");
  });
});
