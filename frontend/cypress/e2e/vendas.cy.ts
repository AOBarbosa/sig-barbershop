describe("Módulo Vendas", () => {
  beforeEach(() => {
    cy.fixture("vendas").as("dados");
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
    cy.intercept(apiRoute("/pessoas"), dados.pessoas).as("listarPessoas");
    cy.intercept(apiRoute("/clientes"), dados.clientes).as("listarClientes");
    cy.intercept(apiRoute("/caixas"), dados.caixas).as("listarCaixas");
    cy.intercept(apiRoute("/produtos"), dados.produtos).as("listarProdutos");
  }

  it("lista vendas com cliente, status colorido e valor do backend", function () {
    interceptBase(this.dados);
    cy.intercept(apiRoute("/vendas"), this.dados.vendas).as("listarVendas");

    cy.visit("/vendas");
    cy.wait("@listarVendas");

    cy.get("main").contains("Vendas").should("be.visible");
    cy.contains("Maria Silva").should("be.visible");
    cy.contains("Pendente").should("be.visible");
    cy.contains("R$ 80,00").should("be.visible");
    cy.contains("Nova venda").should("have.attr", "href", "/vendas/novo");
  });

  it("cria venda com cliente, caixa, forma de pagamento e produtos", function () {
    interceptBase(this.dados);
    cy.intercept(apiRoute("/vendas"), []).as("listarDepoisDeCriar");
    cy.intercept("POST", "**/vendas", {
      statusCode: 201,
      body: {
        id_venda: 21,
        CLIENTE_PESSOA_id_pessoa: 1,
        CAIXA_PESSOA_id_pessoa: 5,
        data_hora: "2026-07-06T15:00:00",
        status: "ABERTA",
        valor_total: "0.00",
        forma_pagamento: "PIX",
        desconto: "0.00"
      }
    }).as("criarVenda");
    cy.intercept("POST", "**/vendas/21/produtos", {
      statusCode: 201,
      body: this.dados.vendaProdutos[0]
    }).as("vincularProduto");

    cy.visit("/vendas/novo");
    cy.contains("Salvar venda").click();
    cy.contains("Cliente é obrigatório").should("be.visible");

    cy.get("select[name='CLIENTE_PESSOA_id_pessoa']").select("Maria Silva");
    cy.get("select[name='CAIXA_PESSOA_id_pessoa']").select("Carlos Caixa");
    cy.get("input[name='data_hora']").type("2026-07-06T15:00");
    cy.get("select[name='forma_pagamento']").select("Pix");
    cy.get("input[aria-label='Quantidade de Pomada modeladora']")
      .clear()
      .type("1");
    cy.contains("Salvar venda").click();

    cy.wait("@criarVenda").its("request.body").should("deep.include", {
      CLIENTE_PESSOA_id_pessoa: 1,
      CAIXA_PESSOA_id_pessoa: 5,
      data_hora: "2026-07-06T15:00:00",
      forma_pagamento: "PIX"
    });
    cy.wait("@vincularProduto")
      .its("request.body")
      .should("deep.equal", { PRODUTO_id_produto: 1, quantidade: 1 });
    cy.location("pathname").should("eq", "/vendas");
    cy.location("search").should("eq", "?salvo=1");
    cy.wait("@listarDepoisDeCriar");
  });

  it("mostra detalhes, produtos vinculados e conclui a venda", function () {
    interceptBase(this.dados);
    cy.intercept(apiRoute("/vendas/20"), this.dados.vendas[0]).as(
      "buscarVenda"
    );
    cy.intercept(apiRoute("/vendas/20/produtos"), this.dados.vendaProdutos).as(
      "listarProdutosVenda"
    );
    cy.intercept("PATCH", "**/vendas/20/status", {
      statusCode: 200,
      body: {
        ...this.dados.vendas[0],
        status: "PAGA"
      }
    }).as("concluirVenda");

    cy.visit("/vendas/20");
    cy.wait(["@buscarVenda", "@listarProdutosVenda"]);

    cy.contains("Maria Silva").should("be.visible");
    cy.contains("Caixa de Carlos Caixa").should("be.visible");
    cy.contains("Pomada modeladora").should("be.visible");
    cy.contains("Oleo para barba").should("be.visible");
    cy.contains("Total calculado pelo backend").should("be.visible");
    cy.contains("R$ 80,00").should("be.visible");
    cy.contains("Concluir").click();
    cy.wait("@concluirVenda")
      .its("request.body")
      .should("deep.equal", { status: "PAGA" });
    cy.contains("Concluída").should("be.visible");
  });
});
