describe("Módulo Produtos - formulário", () => {
  beforeEach(() => {
    cy.fixture("produtos").as("produtos");
  });

  it("valida e cria um produto", () => {
    cy.intercept("GET", "**/produtos", {
      statusCode: 200,
      body: []
    }).as("listarDepoisDeCriar");
    cy.intercept("POST", "**/produtos", {
      statusCode: 201,
      body: {
        id_produto: 3,
        nome: "Cera modeladora",
        categoria: "Finalizador",
        preco_venda: "42.00",
        preco_custo: "24.00",
        pontos_gerados: 4,
        ativo: true
      }
    }).as("criarProduto");

    cy.visit("/produtos/novo");
    cy.contains("Salvar produto").click();
    cy.contains("Nome é obrigatório").should("be.visible");

    cy.get("input[name='nome']").type("Cera modeladora");
    cy.get("input[name='categoria']").type("Finalizador");
    cy.get("input[name='preco_venda']").clear().type("42");
    cy.get("input[name='preco_custo']").clear().type("24");
    cy.get("input[name='pontos_gerados']").clear().type("4");
    cy.contains("Produto ativo").click();
    cy.contains("Salvar produto").click();

    cy.wait("@criarProduto").its("request.body").should("deep.include", {
      nome: "Cera modeladora",
      categoria: "Finalizador",
      preco_venda: 42,
      preco_custo: 24,
      pontos_gerados: 4,
      ativo: false
    });
    cy.location("pathname").should("eq", "/produtos");
    cy.location("search").should("eq", "?salvo=1");
    cy.wait("@listarDepoisDeCriar");
    cy.contains("Produto salvo com sucesso").should("be.visible");
  });

  it("edita um produto existente", function () {
    cy.loginAsAdmin();
    cy.intercept("GET", "**/produtos", {
      statusCode: 200,
      body: this.produtos
    }).as("listarDepoisDeEditar");
    cy.intercept("GET", "**/produtos/1", {
      statusCode: 200,
      body: this.produtos[0]
    }).as("buscarProduto");
    cy.intercept("PUT", "**/produtos/1", {
      statusCode: 200,
      body: {
        ...this.produtos[0],
        nome: "Pomada premium",
        categoria: "Finalizador premium",
        preco_venda: "55.00",
        preco_custo: "30.00",
        pontos_gerados: 7
      }
    }).as("atualizarProduto");

    cy.visit("/produtos/1/editar");
    cy.wait("@buscarProduto");

    cy.get("input[name='nome']").clear().type("Pomada premium");
    cy.get("input[name='categoria']").clear().type("Finalizador premium");
    cy.get("input[name='preco_venda']").clear().type("55");
    cy.get("input[name='preco_custo']").clear().type("30");
    cy.get("input[name='pontos_gerados']").clear().type("7");
    cy.contains("Salvar produto").click();

    cy.wait("@atualizarProduto").its("request.body").should("deep.include", {
      nome: "Pomada premium",
      categoria: "Finalizador premium",
      preco_venda: 55,
      preco_custo: 30,
      pontos_gerados: 7
    });
    cy.location("pathname").should("eq", "/produtos");
    cy.location("search").should("eq", "?salvo=1");
    cy.wait("@listarDepoisDeEditar");
  });

  it("funcionário edita produto sem sobrescrever o preço de custo oculto", function () {
    cy.loginAsFuncionario();
    cy.intercept("GET", "**/produtos/1", {
      statusCode: 200,
      body: { ...this.produtos[0], preco_custo: null }
    }).as("buscarProduto");
    cy.intercept("GET", "**/produtos", {
      statusCode: 200,
      body: this.produtos
    }).as("listarDepoisDeEditar");
    cy.intercept("PUT", "**/produtos/1", {
      statusCode: 200,
      body: { ...this.produtos[0], nome: "Pomada premium", preco_custo: null }
    }).as("atualizarProduto");

    cy.visit("/produtos/1/editar");
    cy.wait("@buscarProduto");

    cy.get("input[name='preco_custo']").should(
      "have.value",
      "Visível apenas para administradores"
    );
    cy.get("input[name='nome']").clear().type("Pomada premium");
    cy.contains("Salvar produto").click();

    cy.wait("@atualizarProduto")
      .its("request.body")
      .then((body) => {
        expect(body).to.not.have.property("preco_custo");
      });
    cy.location("pathname").should("eq", "/produtos");
  });
});
