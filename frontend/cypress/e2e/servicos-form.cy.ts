describe("Módulo Serviços - formulário", () => {
  beforeEach(() => {
    cy.fixture("servicos").as("servicos");
  });

  it("valida e cria um serviço", () => {
    cy.intercept("GET", "**/servicos", {
      statusCode: 200,
      body: []
    }).as("listarDepoisDeCriar");
    cy.intercept("POST", "**/servicos", {
      statusCode: 201,
      body: {
        id_servico: 3,
        nome: "Sobrancelha",
        descricao: "Design simples",
        preco: "20.00",
        duracao_minutos: 20,
        ativo: true
      }
    }).as("criarServico");

    cy.visit("/servicos/novo");
    cy.contains("Salvar serviço").click();
    cy.contains("Nome é obrigatório").should("be.visible");
    cy.contains("Preço deve ser maior que zero").should("be.visible");

    cy.get("input[name='nome']").type("Sobrancelha");
    cy.get("textarea[name='descricao']").type("Design simples");
    cy.get("input[name='preco']").clear().type("20");
    cy.get("input[name='duracao_minutos']").clear().type("20");
    cy.contains("R$ 20,00").should("be.visible");
    cy.contains("Serviço ativo").click();
    cy.contains("Salvar serviço").click();

    cy.wait("@criarServico")
      .its("request.body")
      .should("deep.include", {
        nome: "Sobrancelha",
        descricao: "Design simples",
        preco: 20,
        duracao_minutos: 20,
        ativo: false
      });
    cy.location("pathname").should("eq", "/servicos");
    cy.location("search").should("eq", "?salvo=1");
    cy.wait("@listarDepoisDeCriar");
    cy.contains("Serviço salvo com sucesso").should("be.visible");
  });

  it("edita um serviço existente", function () {
    cy.intercept("GET", "**/servicos", {
      statusCode: 200,
      body: this.servicos
    }).as("listarDepoisDeEditar");
    cy.intercept("GET", "**/servicos/1", {
      statusCode: 200,
      body: this.servicos[0]
    }).as("buscarServico");
    cy.intercept("PUT", "**/servicos/1", {
      statusCode: 200,
      body: {
        ...this.servicos[0],
        nome: "Corte premium",
        preco: "55.00"
      }
    }).as("atualizarServico");

    cy.visit("/servicos/1/editar");
    cy.wait("@buscarServico");

    cy.get("input[name='nome']").clear().type("Corte premium");
    cy.get("input[name='preco']").clear().type("55");
    cy.contains("Salvar serviço").click();

    cy.wait("@atualizarServico")
      .its("request.body")
      .should("deep.include", {
        nome: "Corte premium",
        preco: 55
      });
    cy.location("pathname").should("eq", "/servicos");
    cy.location("search").should("eq", "?salvo=1");
    cy.wait("@listarDepoisDeEditar");
  });
});
