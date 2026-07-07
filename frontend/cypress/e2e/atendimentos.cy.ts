describe("Módulo Atendimentos", () => {
  beforeEach(() => {
    cy.fixture("atendimentos").as("dados");
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
    cy.intercept(apiRoute("/barbeiros"), dados.barbeiros).as("listarBarbeiros");
    cy.intercept(apiRoute("/servicos"), dados.servicos).as("listarServicos");
    cy.intercept(
      apiRoute("/barbeiros/2/disponibilidades"),
      dados.disponibilidades
    ).as("listarDisponibilidades");
  }

  it("lista atendimentos com nomes, status colorido e valor do backend", function () {
    interceptBase(this.dados);
    cy.intercept(apiRoute("/atendimentos"), this.dados.atendimentos).as(
      "listarAtendimentos"
    );

    cy.visit("/atendimentos");
    cy.wait("@listarAtendimentos");

    cy.get("main").contains("Atendimentos").should("be.visible");
    cy.contains("Maria Silva").should("be.visible");
    cy.contains("João Barbeiro").should("be.visible");
    cy.contains("Agendado").should("be.visible");
    cy.contains("R$ 80,00").should("be.visible");
    cy.contains("Novo atendimento").should(
      "have.attr",
      "href",
      "/atendimentos/novo"
    );
  });

  it("cria atendimento com cliente, barbeiro disponível, data e serviços", function () {
    interceptBase(this.dados);
    cy.intercept(apiRoute("/atendimentos"), []).as("listarDepoisDeCriar");
    cy.intercept("POST", "**/atendimentos", {
      statusCode: 201,
      body: {
        id_atendimento: 11,
        CLIENTE_id_cliente: 1,
        BARBEIRO_id_barbeiro: 2,
        data_hora: "2026-07-06T14:30:00",
        status: "agendado",
        valor_total: "0.00",
        observacao: "Cliente quer corte e barba"
      }
    }).as("criarAtendimento");
    cy.intercept("POST", "**/atendimentos/11/servicos", {
      statusCode: 201,
      body: this.dados.atendimentoServicos[0]
    }).as("vincularServico");

    cy.visit("/atendimentos/novo");
    cy.contains("Salvar atendimento").click();
    cy.contains("Cliente é obrigatório").should("be.visible");

    cy.get("select[name='CLIENTE_id_cliente']").select("Maria Silva");
    cy.get("select[name='BARBEIRO_id_barbeiro']").select("João Barbeiro");
    cy.wait("@listarDisponibilidades");
    cy.get("input[name='data_hora']").type("2026-07-06T14:30");
    cy.contains("Corte masculino").click();
    cy.get("textarea[name='observacao']").type("Cliente quer corte e barba");
    cy.contains("Salvar atendimento").click();

    cy.wait("@criarAtendimento")
      .its("request.body")
      .should("deep.include", {
        CLIENTE_id_cliente: 1,
        BARBEIRO_id_barbeiro: 2,
        data_hora: "2026-07-06T14:30:00",
        status: "agendado",
        observacao: "Cliente quer corte e barba"
      });
    cy.wait("@vincularServico")
      .its("request.body")
      .should("deep.equal", { SERVICO_id_servico: 1 });
    cy.location("pathname").should("eq", "/atendimentos");
    cy.location("search").should("eq", "?salvo=1");
    cy.wait("@listarDepoisDeCriar");
  });

  it("mostra detalhes, serviços vinculados e muda status sem calcular valor", function () {
    interceptBase(this.dados);
    cy.intercept(apiRoute("/atendimentos/10"), this.dados.atendimentos[0]).as(
      "buscarAtendimento"
    );
    cy.intercept(
      apiRoute("/atendimentos/10/servicos"),
      this.dados.atendimentoServicos
    ).as("listarServicosAtendimento");
    cy.intercept("PATCH", "**/atendimentos/10/status", {
      statusCode: 200,
      body: {
        ...this.dados.atendimentos[0],
        status: "em_andamento",
        valor_total: "80.00"
      }
    }).as("iniciarAtendimento");

    cy.visit("/atendimentos/10");
    cy.wait(["@buscarAtendimento", "@listarServicosAtendimento"]);

    cy.contains("Maria Silva").should("be.visible");
    cy.contains("Corte masculino").should("be.visible");
    cy.contains("Barba completa").should("be.visible");
    cy.contains("Total calculado pelo backend").should("be.visible");
    cy.contains("R$ 80,00").should("be.visible");
    cy.contains("Iniciar").click();
    cy.wait("@iniciarAtendimento")
      .its("request.body")
      .should("deep.equal", { status: "em_andamento" });
    cy.contains("Em andamento").should("be.visible");
  });
});
