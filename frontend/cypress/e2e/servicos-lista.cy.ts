describe("Módulo Serviços - listagem", () => {
  beforeEach(() => {
    cy.fixture("servicos").as("servicos");
  });

  it("lista serviços por nome e navega pelo shell", function () {
    cy.viewport(1280, 720);
    cy.intercept(
      {
        method: "GET",
        pathname: "/servicos",
        headers: {
          accept: "application/json, text/plain, */*"
        }
      },
      {
        statusCode: 200,
        body: this.servicos
      }
    ).as("listarServicos");

    cy.visit("/servicos");
    cy.wait("@listarServicos");

    cy.contains("SIG Barbershop").should("be.visible");
    cy.contains("Serviços").should("be.visible");
    cy.contains("Corte masculino").should("be.visible");
    cy.contains("Barba completa").should("be.visible");
    cy.contains("Total de serviços").should("be.visible");
    cy.contains("3").should("be.visible");
    cy.contains("Serviços ativos").should("be.visible");
    cy.contains("Ativos").should("be.visible");
    cy.contains("Novo serviço").should("have.attr", "href", "/servicos/novo");
  });

  it("filtra serviços por busca e status", function () {
    cy.intercept(
      {
        method: "GET",
        pathname: "/servicos",
        headers: {
          accept: "application/json, text/plain, */*"
        }
      },
      {
        statusCode: 200,
        body: this.servicos
      }
    ).as("listarServicos");

    cy.visit("/servicos");
    cy.wait("@listarServicos");

    cy.get("input[placeholder='Buscar serviço']").type("barba");
    cy.contains("Barba completa").should("be.visible");
    cy.contains("Corte masculino").should("not.exist");

    cy.get("input[placeholder='Buscar serviço']").clear();
    cy.contains("Inativos").click();
    cy.contains("Coloracao").should("be.visible");
    cy.contains("Barba completa").should("not.exist");
  });

  it("mostra estado vazio filtrado e expõe ação de editar", function () {
    cy.intercept(
      {
        method: "GET",
        pathname: "/servicos",
        headers: {
          accept: "application/json, text/plain, */*"
        }
      },
      {
        statusCode: 200,
        body: this.servicos
      }
    ).as("listarServicos");

    cy.visit("/servicos");
    cy.wait("@listarServicos");

    cy.get("button[aria-label='Abrir ações do serviço Corte masculino']")
      .filter(":visible")
      .first()
      .click();
    cy.contains("Editar").should("have.attr", "href", "/servicos/1/editar");

    cy.visit("/servicos");
    cy.wait("@listarServicos");

    cy.get("input[placeholder='Buscar serviço']")
      .type("não existe")
      .should("have.value", "não existe");
    cy.contains("Nenhum serviço encontrado").should("be.visible");
    cy.contains("Cadastrar serviço").should("have.attr", "href", "/servicos/novo");
  });

  it("mostra erro quando a API retorna uma lista inválida", () => {
    cy.intercept(
      {
        method: "GET",
        pathname: "/servicos",
        headers: {
          accept: "application/json, text/plain, */*"
        }
      },
      {
        statusCode: 200,
        body: { detail: "rota incorreta" }
      }
    ).as("listarServicosFormatoInvalido");

    cy.visit("/servicos");
    cy.wait("@listarServicosFormatoInvalido");

    cy.contains("Resposta inválida ao listar serviços").should("be.visible");
    cy.contains("Runtime TypeError").should("not.exist");
  });

  it("mantém a listagem e o menu principal responsivos no mobile", function () {
    cy.viewport("iphone-x");
    cy.intercept(
      {
        method: "GET",
        pathname: "/servicos",
        headers: {
          accept: "application/json, text/plain, */*"
        }
      },
      {
        statusCode: 200,
        body: this.servicos
      }
    ).as("listarServicos");

    cy.visit("/servicos");
    cy.wait("@listarServicos");

    cy.get("main").contains("Serviços").should("be.visible");
    cy.get("button[aria-label='Abrir menu']").click();
    cy.get("[data-testid='mobile-sidebar']").within(() => {
      cy.contains("SIG Barbershop").should("be.visible");
      cy.contains("Atendimentos").should("be.visible");
    });
    cy.get("input[placeholder='Buscar serviço']").should("be.visible");
    cy.get("[data-testid='servicos-mobile-list']")
      .contains("Corte masculino")
      .should("be.visible");
  });
});
