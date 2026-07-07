describe("Módulo Clientes - formulário", () => {
  beforeEach(() => {
    cy.fixture("clientes").as("clientesFixture");
  });

  it("valida e cria um cliente", () => {
    cy.intercept("GET", "**/clientes", { statusCode: 200, body: [] }).as(
      "listarClientesDepois"
    );
    cy.intercept("GET", "**/pessoas", { statusCode: 200, body: [] }).as(
      "listarPessoasDepois"
    );
    cy.intercept("POST", "**/clientes/completo", {
      statusCode: 201,
      body: {
        cliente: { id_cliente: 10, PESSOA_id_pessoa: 10 },
        pessoa: {
          id_pessoa: 10,
          nome: "Carlos Mendes",
          cpf: "45678901234",
          email: "carlos@email.com",
          data_nascimento: "1988-04-10",
          created_at: "2026-07-01T10:00:00",
          updated_at: "2026-07-01T10:00:00"
        }
      }
    }).as("criarClienteCompleto");

    cy.visit("/clientes/novo");
    cy.contains("Salvar cliente").click();
    cy.contains("Nome é obrigatório").should("be.visible");
    cy.contains("CPF deve conter 11 dígitos").should("be.visible");

    cy.get("input[name='nome']").type("Carlos Mendes");
    cy.get("input[name='cpf']").type("45678901234");
    cy.get("input[name='email']").type("carlos@email.com");
    cy.get("input[name='data_nascimento']").type("1988-04-10");
    cy.contains("Salvar cliente").click();

    cy.wait("@criarClienteCompleto")
      .its("request.body")
      .should("deep.include", {
        nome: "Carlos Mendes",
        cpf: "45678901234",
        email: "carlos@email.com",
        data_nascimento: "1988-04-10"
      });

    cy.location("pathname").should("eq", "/clientes");
    cy.location("search").should("eq", "?salvo=1");
    cy.contains("Cliente salvo com sucesso").should("be.visible");
  });

  it("rejeita email inválido", () => {
    cy.visit("/clientes/novo");
    cy.get("input[name='nome']").type("Teste");
    cy.get("input[name='cpf']").type("12345678901");
    cy.get("input[name='email']").type("email-invalido");
    cy.contains("Salvar cliente").click();

    cy.contains("Email inválido").should("be.visible");
  });

  it("edita um cliente existente", function () {
    cy.intercept("GET", "**/clientes/1", {
      statusCode: 200,
      body: this.clientesFixture.clientes[0]
    }).as("buscarCliente");
    cy.intercept("GET", "**/pessoas/1", {
      statusCode: 200,
      body: this.clientesFixture.pessoas[0]
    }).as("buscarPessoa");
    cy.intercept("GET", "**/clientes", {
      statusCode: 200,
      body: this.clientesFixture.clientes
    }).as("listarClientesDepois");
    cy.intercept("GET", "**/pessoas", {
      statusCode: 200,
      body: this.clientesFixture.pessoas
    }).as("listarPessoasDepois");
    cy.intercept("PUT", "**/pessoas/1", {
      statusCode: 200,
      body: {
        ...this.clientesFixture.pessoas[0],
        nome: "Maria Silva Santos"
      }
    }).as("atualizarPessoa");

    cy.visit("/clientes/1/editar");
    cy.wait(["@buscarCliente", "@buscarPessoa"]);

    cy.get("input[name='nome']").should("have.value", "Maria Silva");
    cy.get("input[name='nome']").clear().type("Maria Silva Santos");
    cy.contains("Salvar cliente").click();

    cy.wait("@atualizarPessoa")
      .its("request.body")
      .should("deep.include", { nome: "Maria Silva Santos" });

    cy.location("pathname").should("eq", "/clientes");
    cy.location("search").should("eq", "?salvo=1");
  });

  it("exibe erro do backend ao tentar criar com CPF duplicado", () => {
    cy.intercept("POST", "**/clientes/completo", {
      statusCode: 409,
      body: { detail: "CPF ja cadastrado" }
    }).as("criarClienteConflito");

    cy.visit("/clientes/novo");
    cy.get("input[name='nome']").type("Novo Cliente");
    cy.get("input[name='cpf']").type("12345678901");
    cy.contains("Salvar cliente").click();

    cy.wait("@criarClienteConflito");
    cy.contains("CPF ja cadastrado").should("be.visible");
  });
});
