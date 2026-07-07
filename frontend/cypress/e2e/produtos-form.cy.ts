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
        descricao: "Brilho intenso",
        preco: "20.00",
        estoque: 15,
        ativo: true
      }
    }).as("criarProduto");

    cy.visit("/produtos/novo");
    cy.contains("Salvar produto").click();
    cy.contains("Nome é obrigatório").should("be.visible");
    cy.contains("Preço deve ser maior que zero").should("be.visible");

    cy.get("input[name='nome']").type("Cera modeladora");
    cy.get("textarea[name='descricao']").type("Brilho intenso");
    cy.get("input[name='preco']").clear().type("20");
    cy.get("input[name='estoque']").clear().type("15");
    cy.contains("R$ 20,00").should("be.visible");
    cy.contains("Produto ativo").click();
    cy.contains("Salvar produto").click();

    cy.wait("@criarProduto").its("request.body").should("deep.include", {
      nome: "Cera modeladora",
      descricao: "Brilho intenso",
      preco: 20,
      estoque: 15,
      ativo: false
    });
    cy.location("pathname").should("eq", "/produtos");
    cy.location("search").should("eq", "?salvo=1");
    cy.wait("@listarDepoisDeCriar");
    cy.contains("Produto salvo com sucesso").should("be.visible");
  });

  it("edita um produto existente", function () {
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
        preco: "55.00"
      }
    }).as("atualizarProduto");

    cy.visit("/produtos/1/editar");
    cy.wait("@buscarProduto");

    cy.get("input[name='nome']").clear().type("Pomada premium");
    cy.get("input[name='preco']").clear().type("55");
    cy.contains("Salvar produto").click();

    cy.wait("@atualizarProduto").its("request.body").should("deep.include", {
      nome: "Pomada premium",
      preco: 55
    });
    cy.location("pathname").should("eq", "/produtos");
    cy.location("search").should("eq", "?salvo=1");
    cy.wait("@listarDepoisDeEditar");
  });
});
