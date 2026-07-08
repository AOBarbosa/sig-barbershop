describe("Agendamento público", () => {
  beforeEach(() => {
    cy.fixture("agendamento-publico").as("dados");
    cy.clearCookie("access_token");
  });

  function interceptCatalogo(dados: any) {
    cy.intercept("GET", "**/pessoas", dados.pessoas).as("listarPessoas");
    cy.intercept("GET", "**/barbeiros", dados.barbeiros).as("listarBarbeiros");
    cy.intercept(
      "GET",
      "**/barbeiros/2/disponibilidades",
      dados.disponibilidades
    ).as("listarDisponibilidades");
    cy.intercept(
      "GET",
      "**/barbeiros/2/horarios-ocupados*",
      dados.horariosOcupados
    ).as("listarOcupados");
  }

  it("permite visualizar horários sem login e exige autenticação só na confirmação", function () {
    interceptCatalogo(this.dados);
    cy.intercept("GET", "**/auth/me", {
      statusCode: 401,
      body: { detail: "Nao autenticado" }
    }).as("usuarioAnonimo");

    cy.visit("/");
    cy.contains("Agendar horário").should("be.visible");
    cy.contains("Joao Barbeiro").click();
    cy.wait(["@listarDisponibilidades", "@listarOcupados"]);

    cy.contains("13/07/2026 08:00").click();
    cy.contains("13/07/2026 08:30").should("not.exist");
    cy.contains("Revisar agendamento").should("be.visible");
    cy.contains("Confirmar agendamento").click();

    cy.location("pathname").should("eq", "/login");
    cy.location("search").should("contain", "next=");
    cy.location("search").then((search) => {
      expect(decodeURIComponent(search)).to.contain("barbeiro=2");
    });
  });

  it("cria conta de cliente e volta para a revisão sem confirmar automaticamente", function () {
    interceptCatalogo(this.dados);
    cy.intercept("POST", "**/auth/registrar-cliente", {
      statusCode: 201,
      body: {
        id_pessoa: 5,
        nome: "Cliente Novo",
        email: "novo@example.com",
        role: "cliente"
      }
    }).as("registrarCliente");
    cy.intercept("GET", "**/auth/me", {
      statusCode: 200,
      body: {
        id_pessoa: 5,
        nome: "Cliente Novo",
        email: "novo@example.com",
        role: "cliente"
      }
    }).as("usuarioAtual");

    cy.visit("/login?next=/?barbeiro=2%26horario=2026-07-13T08:00");
    cy.get("button").contains("Criar conta").last().click();
    cy.get("input[name='nome']").type("Cliente Novo");
    cy.get("input[name='cpf']").type("11122233344");
    cy.get("input[name='email']").type("novo@example.com");
    cy.get("input[name='senha']").type("senha123");
    cy.contains("button", "Criar conta").click();

    cy.wait("@registrarCliente").its("request.body").should("deep.include", {
      nome: "Cliente Novo",
      cpf: "11122233344",
      email: "novo@example.com",
      senha: "senha123"
    });
    cy.location("pathname").should("eq", "/");
    cy.contains("Revisar agendamento").should("be.visible");
    cy.contains("Agendamento confirmado").should("not.exist");
  });

  it("confirma o atendimento quando o cliente autenticado clica na revisão", function () {
    cy.loginAsCliente();
    interceptCatalogo(this.dados);
    cy.intercept("POST", "**/atendimentos", {
      statusCode: 201,
      body: {
        id_atendimento: 22,
        CLIENTE_PESSOA_id_pessoa: 1,
        BARBEIRO_PESSOA_id_pessoa: 2,
        data_hora_inicio: "2026-07-13T08:00:00",
        data_hora_fim: null,
        valor_total: "0.00",
        status: "AGENDADO",
        observacoes: "Agendamento público"
      }
    }).as("criarAtendimento");

    cy.visit("/?barbeiro=2&horario=2026-07-13T08:00");
    cy.wait("@usuarioAtualCliente");
    cy.contains("Revisar agendamento").should("be.visible");
    cy.contains("Confirmar agendamento").click();

    cy.wait("@criarAtendimento").its("request.body").should("deep.include", {
      CLIENTE_PESSOA_id_pessoa: 1,
      BARBEIRO_PESSOA_id_pessoa: 2,
      data_hora_inicio: "2026-07-13T08:00",
      status: "AGENDADO",
      observacoes: "Agendamento público"
    });
    cy.contains("Agendamento confirmado").should("be.visible");
  });
});
