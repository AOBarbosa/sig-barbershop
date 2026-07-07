describe("Módulo Produtos - listagem", () => {
  beforeEach(() => {
    cy.fixture("produtos").as("produtos");
  });

  it("lista produtos com preço formatado e navega pelo shell", function () {
    cy.viewport(1280, 720);
    cy.intercept(
      {
        method: "GET",
        pathname: "/produtos",
        headers: {
          accept: "application/json, text/plain, */*"
        }
      },
      {
        statusCode: 200,
        body: this.produtos
      }
    ).as("listarProdutos");

    cy.visit("/produtos");
    cy.wait("@listarProdutos");

    cy.contains("SIG Barbershop").should("be.visible");
    cy.contains("Produtos").should("be.visible");
    cy.contains("Pomada modeladora").should("be.visible");
    cy.contains("Fixação forte, acabamento fosco").should("be.visible");
    cy.contains("R$ 45,00").should("be.visible");
    cy.contains("Óleo para barba").should("be.visible");
    cy.contains("Total de produtos").should("be.visible");
    cy.contains("3").should("be.visible");
    cy.contains("Produtos ativos").should("be.visible");
    cy.contains("Valor em estoque").should("be.visible");
    cy.contains("R$ 820,00").should("be.visible");
    cy.contains("Novo produto").should("have.attr", "href", "/produtos/novo");
  });

  it("filtra produtos por busca e status", function () {
    cy.intercept(
      {
        method: "GET",
        pathname: "/produtos",
        headers: {
          accept: "application/json, text/plain, */*"
        }
      },
      {
        statusCode: 200,
        body: this.produtos
      }
    ).as("listarProdutos");

    cy.visit("/produtos");
    cy.wait("@listarProdutos");

    cy.get("input[placeholder='Buscar produto']").type("barba");
    cy.contains("Óleo para barba").should("be.visible");
    cy.contains("Pomada modeladora").should("not.exist");

    cy.get("input[placeholder='Buscar produto']").clear();
    cy.contains("Inativos").click();
    cy.contains("Shampoo antiqueda").should("be.visible");
    cy.contains("Óleo para barba").should("not.exist");
  });

  it("mostra estado vazio filtrado e expõe ação de editar", function () {
    cy.intercept(
      {
        method: "GET",
        pathname: "/produtos",
        headers: {
          accept: "application/json, text/plain, */*"
        }
      },
      {
        statusCode: 200,
        body: this.produtos
      }
    ).as("listarProdutos");

    cy.visit("/produtos");
    cy.wait("@listarProdutos");

    cy.get("button[aria-label='Abrir ações do produto Pomada modeladora']")
      .filter(":visible")
      .first()
      .click();
    cy.contains("Editar").should("have.attr", "href", "/produtos/1/editar");

    cy.visit("/produtos");
    cy.wait("@listarProdutos");

    cy.get("input[placeholder='Buscar produto']")
      .type("não existe")
      .should("have.value", "não existe");
    cy.contains("Nenhum produto encontrado").should("be.visible");
    cy.contains("Cadastrar produto").should(
      "have.attr",
      "href",
      "/produtos/novo"
    );
  });

  it("mostra erro quando a API retorna uma lista inválida", () => {
    cy.intercept(
      {
        method: "GET",
        pathname: "/produtos",
        headers: {
          accept: "application/json, text/plain, */*"
        }
      },
      {
        statusCode: 200,
        body: { detail: "rota incorreta" }
      }
    ).as("listarProdutosFormatoInvalido");

    cy.visit("/produtos");
    cy.wait("@listarProdutosFormatoInvalido");

    cy.contains("Resposta inválida ao listar produtos").should("be.visible");
    cy.contains("Runtime TypeError").should("not.exist");
  });

  it("mantém a listagem e o menu principal responsivos no mobile", function () {
    cy.viewport("iphone-x");
    cy.intercept(
      {
        method: "GET",
        pathname: "/produtos",
        headers: {
          accept: "application/json, text/plain, */*"
        }
      },
      {
        statusCode: 200,
        body: this.produtos
      }
    ).as("listarProdutos");

    cy.visit("/produtos");
    cy.wait("@listarProdutos");

    cy.get("main").contains("Produtos").should("be.visible");
    cy.get("button[aria-label='Abrir menu']").click();
    cy.get("[data-testid='mobile-sidebar']").within(() => {
      cy.contains("SIG Barbershop").should("be.visible");
      cy.contains("Vendas").should("be.visible");
    });
    cy.get("input[placeholder='Buscar produto']").should("be.visible");
    cy.get("[data-testid='produtos-mobile-list']")
      .contains("Pomada modeladora")
      .should("be.visible");
  });
});
