describe("Módulo Fidelidade", () => {
  beforeEach(() => {
    cy.fixture("fidelidade").as("dados");
  });

  function apiRoute(pathname: string) {
    return {
      method: "GET",
      pathname,
      headers: {
        accept: "application/json, text/plain, */*"
      }
    };
  }

  function interceptBase(dados: any) {
    cy.intercept(apiRoute("/servicos"), dados.servicos).as("listarServicos");
    cy.intercept(apiRoute("/produtos"), dados.produtos).as("listarProdutos");
  }

  it("lista regras mostrando origem (serviço ou produto) e pontos", function () {
    interceptBase(this.dados);
    cy.intercept(apiRoute("/fidelidades"), this.dados.fidelidades).as(
      "listarFidelidades"
    );

    cy.visit("/fidelidade");
    cy.wait(["@listarFidelidades", "@listarServicos", "@listarProdutos"]);

    cy.get("main").contains("Fidelidade").should("be.visible");
    cy.contains("Corte masculino").should("be.visible");
    cy.contains("Pomada modeladora").should("be.visible");
    cy.contains("10 pts").should("be.visible");
    cy.contains("Nova regra").should("have.attr", "href", "/fidelidade/nova");
  });

  it("cria regra de fidelidade vinculada a um serviço", function () {
    interceptBase(this.dados);
    cy.intercept(apiRoute("/fidelidades"), []).as("listarDepoisDeCriar");
    cy.intercept("POST", "**/fidelidades", {
      statusCode: 201,
      body: {
        id_fidelidade: 3,
        SERVICO_id_servico: 1,
        PRODUTO_id_produto: null,
        pontos: 10,
        ativo: true
      }
    }).as("criarFidelidade");

    cy.visit("/fidelidade/nova");
    cy.wait(["@listarServicos", "@listarProdutos"]);

    cy.get("select#servico").select("Corte masculino");
    cy.get("input[name='pontos']").clear().type("10");
    cy.contains("Salvar regra").click();

    cy.wait("@criarFidelidade").its("request.body").should("deep.equal", {
      SERVICO_id_servico: 1,
      PRODUTO_id_produto: null,
      pontos: 10,
      ativo: true
    });
    cy.location("pathname").should("eq", "/fidelidade");
    cy.location("search").should("eq", "?salvo=1");
    cy.wait("@listarDepoisDeCriar");
  });

  it("cria regra de fidelidade vinculada a um produto", function () {
    interceptBase(this.dados);
    cy.intercept(apiRoute("/fidelidades"), []).as("listarDepoisDeCriar");
    cy.intercept("POST", "**/fidelidades", {
      statusCode: 201,
      body: {
        id_fidelidade: 4,
        SERVICO_id_servico: null,
        PRODUTO_id_produto: 1,
        pontos: 5,
        ativo: true
      }
    }).as("criarFidelidade");

    cy.visit("/fidelidade/nova");
    cy.wait(["@listarServicos", "@listarProdutos"]);

    cy.contains("label", "Produto").click();
    cy.get("select#produto").select("Pomada modeladora");
    cy.get("input[name='pontos']").clear().type("5");
    cy.contains("Salvar regra").click();

    cy.wait("@criarFidelidade").its("request.body").should("deep.equal", {
      SERVICO_id_servico: null,
      PRODUTO_id_produto: 1,
      pontos: 5,
      ativo: true
    });
    cy.location("pathname").should("eq", "/fidelidade");
    cy.location("search").should("eq", "?salvo=1");
    cy.wait("@listarDepoisDeCriar");
  });

  it("impede regra sem escolha e regra com serviço e produto ao mesmo tempo", function () {
    interceptBase(this.dados);

    cy.visit("/fidelidade/nova");
    cy.wait(["@listarServicos", "@listarProdutos"]);

    cy.contains("Salvar regra").click();
    cy.contains("Selecione um serviço ou um produto").should("be.visible");

    cy.get("select#servico").select("Corte masculino");
    cy.contains("label", "Produto").click();
    cy.get("select#produto").select("Pomada modeladora");
    cy.get("input[name='pontos']").clear().type("10");
    cy.contains("Salvar regra").click();

    cy.contains(
      "Selecione apenas um: serviço ou produto, nunca os dois"
    ).should("be.visible");
  });
});
