describe("Módulo Barbeiros - formulário", () => {
  beforeEach(() => {
    cy.fixture("barbeiros").as("barbeirosFixture");
  });

  it("valida e cria um barbeiro", () => {
    cy.intercept("GET", "**/barbeiros", { statusCode: 200, body: [] }).as(
      "listarBarbeirosDepois"
    );
    cy.intercept("GET", "**/pessoas", { statusCode: 200, body: [] }).as(
      "listarPessoasDepois"
    );
    cy.intercept("POST", "**/barbeiros/completo", {
      statusCode: 201,
      body: {
        barbeiro: {
          PESSOA_id_pessoa: 20,
          apelido: "Lucas",
          comissao_percentual: "40.00"
        },
        pessoa: {
          id_pessoa: 20,
          nome: "Lucas Fernandes",
          cpf: "88899900011",
          email: "lucas@barbearia.com",
          data_nascimento: "1993-09-14",
          admin: false
        }
      }
    }).as("criarBarbeiroCompleto");
    cy.intercept("POST", "**/disponibilidades", {
      statusCode: 201,
      body: {
        id_disponibilidade: 9,
        BARBEIRO_PESSOA_id_pessoa: 20,
        dia_semana: "SEGUNDA",
        hora_inicio: "08:00:00",
        hora_fim: "18:00:00",
        ativo: true
      }
    }).as("criarDisponibilidade");

    cy.visit("/barbeiros/novo");
    cy.contains("Salvar barbeiro").click();
    cy.contains("Nome é obrigatório").should("be.visible");
    cy.contains("CPF deve conter 11 dígitos").should("be.visible");

    cy.get("input[name='nome']").type("Lucas Fernandes");
    cy.get("input[name='cpf']").type("88899900011");
    cy.get("input[name='email']").type("lucas@barbearia.com");
    cy.get("input[name='data_nascimento']").type("1993-09-14");
    cy.get("input[name='apelido']").type("Lucas");
    cy.get("input[name='comissao_percentual']").clear().type("40");
    cy.get("select[name='dia_semana']").select("Segunda");
    cy.get("input[name='hora_inicio']").type("08:00");
    cy.get("input[name='hora_fim']").type("18:00");
    cy.contains("Salvar barbeiro").click();

    cy.wait("@criarBarbeiroCompleto")
      .its("request.body")
      .should("deep.include", {
        nome: "Lucas Fernandes",
        cpf: "88899900011",
        email: "lucas@barbearia.com",
        data_nascimento: "1993-09-14",
        apelido: "Lucas",
        comissao_percentual: 40
      });
    cy.wait("@criarDisponibilidade")
      .its("request.body")
      .should("deep.include", {
        BARBEIRO_PESSOA_id_pessoa: 20,
        dia_semana: "SEGUNDA",
        hora_inicio: "08:00",
        hora_fim: "18:00"
      });

    cy.location("pathname").should("eq", "/barbeiros");
    cy.location("search").should("eq", "?salvo=1");
    cy.contains("Barbeiro salvo com sucesso").should("be.visible");
  });

  it("edita um barbeiro existente", function () {
    cy.intercept("GET", "**/barbeiros/10", {
      statusCode: 200,
      body: this.barbeirosFixture.barbeiros[0]
    }).as("buscarBarbeiro");
    cy.intercept("GET", "**/pessoas/10", {
      statusCode: 200,
      body: this.barbeirosFixture.pessoas[0]
    }).as("buscarPessoa");
    cy.intercept("GET", "**/barbeiros/10/disponibilidades", {
      statusCode: 200,
      body: [
        {
          id_disponibilidade: 1,
          BARBEIRO_PESSOA_id_pessoa: 10,
          dia_semana: "SEGUNDA",
          hora_inicio: "08:00:00",
          hora_fim: "18:00:00",
          ativo: true
        }
      ]
    }).as("listarDisponibilidades");
    cy.intercept("GET", "**/barbeiros", {
      statusCode: 200,
      body: this.barbeirosFixture.barbeiros
    }).as("listarBarbeirosDepois");
    cy.intercept("GET", "**/pessoas", {
      statusCode: 200,
      body: this.barbeirosFixture.pessoas
    }).as("listarPessoasDepois");
    cy.intercept("PUT", "**/barbeiros/10/completo", {
      statusCode: 200,
      body: {
        barbeiro: {
          ...this.barbeirosFixture.barbeiros[0],
          apelido: "Pedrao",
          comissao_percentual: "45.00"
        },
        pessoa: this.barbeirosFixture.pessoas[0]
      }
    }).as("atualizarBarbeiroCompleto");
    cy.intercept("PUT", "**/disponibilidades/1", {
      statusCode: 200,
      body: {
        id_disponibilidade: 1,
        BARBEIRO_PESSOA_id_pessoa: 10,
        dia_semana: "SEGUNDA",
        hora_inicio: "08:00:00",
        hora_fim: "18:00:00",
        ativo: true
      }
    }).as("atualizarDisponibilidade");

    cy.visit("/barbeiros/10/editar");
    cy.wait(["@buscarBarbeiro", "@buscarPessoa", "@listarDisponibilidades"]);

    cy.get("input[name='apelido']").should("have.value", "Pedro");
    cy.get("input[name='apelido']").clear().type("Pedrao");
    cy.get("input[name='comissao_percentual']").clear().type("45");
    cy.contains("Salvar barbeiro").click();

    cy.wait("@atualizarBarbeiroCompleto")
      .its("request.body")
      .should("deep.include", {
        nome: "Pedro Barreto",
        cpf: "55566677788",
        email: "pedro@barbearia.com",
        data_nascimento: "1988-11-03",
        apelido: "Pedrao",
        comissao_percentual: 45
      });
    cy.wait("@atualizarDisponibilidade");

    cy.location("pathname").should("eq", "/barbeiros");
    cy.location("search").should("eq", "?salvo=1");
  });

  it("exibe erro do backend ao tentar criar com CPF duplicado", () => {
    cy.intercept("POST", "**/barbeiros/completo", {
      statusCode: 409,
      body: { detail: "CPF ja cadastrado" }
    }).as("criarBarbeiroConflito");

    cy.visit("/barbeiros/novo");
    cy.get("input[name='nome']").type("Novo Barbeiro");
    cy.get("input[name='cpf']").type("55566677788");
    cy.get("select[name='dia_semana']").select("Segunda");
    cy.get("input[name='hora_inicio']").type("08:00");
    cy.get("input[name='hora_fim']").type("18:00");
    cy.contains("Salvar barbeiro").click();

    cy.wait("@criarBarbeiroConflito");
    cy.contains("CPF ja cadastrado").should("be.visible");
  });
});
