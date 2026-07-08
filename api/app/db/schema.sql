CREATE DATABASE IF NOT EXISTS sig_barbershop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE sig_barbershop;
CREATE TABLE PESSOA (
    id_pessoa       INT          NOT NULL AUTO_INCREMENT,
    nome            VARCHAR(100) NOT NULL,
    cpf             VARCHAR(14)  UNIQUE,
    email           VARCHAR(100) UNIQUE,
    data_nascimento DATE,
    admin           TINYINT      NOT NULL DEFAULT 0,
    PRIMARY KEY (id_pessoa)
);
CREATE TABLE TELEFONE (
    PESSOA_id_pessoa INT         NOT NULL,
    telefone         VARCHAR(20) NOT NULL,
    PRIMARY KEY (PESSOA_id_pessoa, telefone),
    CONSTRAINT FK_TELEFONE_PESSOA
        FOREIGN KEY (PESSOA_id_pessoa) REFERENCES PESSOA (id_pessoa)
        ON DELETE CASCADE
);
CREATE TABLE CLIENTE (
    PESSOA_id_pessoa INT NOT NULL PRIMARY KEY,
    preferencias     TEXT,
    observacoes      TEXT,
    CONSTRAINT FK_CLIENTE_PESSOA
        FOREIGN KEY (PESSOA_id_pessoa) REFERENCES PESSOA (id_pessoa)
        ON DELETE CASCADE
);
CREATE TABLE CAIXA (
    PESSOA_id_pessoa INT NOT NULL PRIMARY KEY,
    CONSTRAINT FK_CAIXA_PESSOA
        FOREIGN KEY (PESSOA_id_pessoa) REFERENCES PESSOA (id_pessoa)
        ON DELETE CASCADE
);
CREATE TABLE BARBEIRO (
    PESSOA_id_pessoa     INT NOT NULL PRIMARY KEY,
    apelido              VARCHAR(60),
    comissao_percentual  DECIMAL(5,2),
    CONSTRAINT FK_BARBEIRO_PESSOA
        FOREIGN KEY (PESSOA_id_pessoa) REFERENCES PESSOA (id_pessoa)
        ON DELETE CASCADE
);

CREATE TABLE DISPONIBILIDADE (
    id_disponibilidade       INT NOT NULL AUTO_INCREMENT,
    BARBEIRO_PESSOA_id_pessoa INT NOT NULL,
    dia_semana               ENUM('SEGUNDA','TERCA','QUARTA','QUINTA','SEXTA','SABADO','DOMINGO') NOT NULL,
    hora_inicio              TIME NOT NULL,
    hora_fim                 TIME NOT NULL,
    ativo                    TINYINT NOT NULL DEFAULT 1,
    PRIMARY KEY (id_disponibilidade),
    KEY FK_DISPONIBILIDADE_BARBEIRO (BARBEIRO_PESSOA_id_pessoa),
    CONSTRAINT FK_DISPONIBILIDADE_BARBEIRO
        FOREIGN KEY (BARBEIRO_PESSOA_id_pessoa) REFERENCES BARBEIRO (PESSOA_id_pessoa)
        ON DELETE CASCADE
);

CREATE TABLE SERVICO (
    id_servico INT         NOT NULL AUTO_INCREMENT,
    nome       VARCHAR(80) NOT NULL,
    ativo      TINYINT     NOT NULL DEFAULT 1,
    PRIMARY KEY (id_servico)
);

CREATE TABLE HISTORICO_SERVICO (
    id_historico       INT           NOT NULL AUTO_INCREMENT,
    SERVICO_id_servico INT           NOT NULL,
    preco              DECIMAL(10,2) NOT NULL,
    duracao_em_minutos INT           NOT NULL,
    pontos_gerados     INT           NOT NULL DEFAULT 0,
    data_inicio        DATE          NOT NULL,
    data_fim           DATE,
    ativo              TINYINT       NOT NULL DEFAULT 1,
    PRIMARY KEY (id_historico),
    KEY FK_HISTORICO_SERVICO_SERVICO (SERVICO_id_servico),
    CONSTRAINT FK_HISTORICO_SERVICO_SERVICO
        FOREIGN KEY (SERVICO_id_servico) REFERENCES SERVICO (id_servico)
);

CREATE TABLE ATENDIMENTO (
    id_atendimento          INT           NOT NULL AUTO_INCREMENT,
    CLIENTE_PESSOA_id_pessoa INT          NOT NULL,
    BARBEIRO_PESSOA_id_pessoa INT         NOT NULL,
    data_hora_inicio        DATETIME      NOT NULL,
    data_hora_fim           DATETIME,
    valor_total             DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    status                  ENUM('AGENDADO','EM_EXECUCAO','CONCLUIDO','CANCELADO') NOT NULL DEFAULT 'AGENDADO',
    observacoes             TEXT,
    PRIMARY KEY (id_atendimento),
    KEY FK_ATENDIMENTO_CLIENTE (CLIENTE_PESSOA_id_pessoa),
    KEY FK_ATENDIMENTO_BARBEIRO (BARBEIRO_PESSOA_id_pessoa),
    CONSTRAINT FK_ATENDIMENTO_CLIENTE
        FOREIGN KEY (CLIENTE_PESSOA_id_pessoa) REFERENCES CLIENTE (PESSOA_id_pessoa),
    CONSTRAINT FK_ATENDIMENTO_BARBEIRO
        FOREIGN KEY (BARBEIRO_PESSOA_id_pessoa) REFERENCES BARBEIRO (PESSOA_id_pessoa)
);

CREATE TABLE ATENDIMENTO_SERVICO (
    ATENDIMENTO_id_atendimento INT           NOT NULL,
    SERVICO_id_servico         INT           NOT NULL,
    preco_cobrado              DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (ATENDIMENTO_id_atendimento, SERVICO_id_servico),
    KEY FK_ATENDIMENTO_SERVICO_SERVICO (SERVICO_id_servico),
    CONSTRAINT FK_ATENDIMENTO_SERVICO_ATENDIMENTO
        FOREIGN KEY (ATENDIMENTO_id_atendimento) REFERENCES ATENDIMENTO (id_atendimento)
        ON DELETE CASCADE,
    CONSTRAINT FK_ATENDIMENTO_SERVICO_SERVICO
        FOREIGN KEY (SERVICO_id_servico) REFERENCES SERVICO (id_servico)
);

CREATE TABLE PRODUTO (
    id_produto INT         NOT NULL AUTO_INCREMENT,
    nome       VARCHAR(80) NOT NULL,
    categoria  VARCHAR(60),
    ativo      TINYINT     NOT NULL DEFAULT 1,
    PRIMARY KEY (id_produto)
);

CREATE TABLE HISTORICO_PRODUTO (
    id_historico      INT           NOT NULL AUTO_INCREMENT,
    PRODUTO_id_produto INT          NOT NULL,
    preco_venda       DECIMAL(10,2) NOT NULL,
    preco_custo       DECIMAL(10,2) NOT NULL,
    pontos_gerados    INT           NOT NULL DEFAULT 0,
    data_inicio       DATE          NOT NULL,
    data_fim          DATE,
    ativo             TINYINT       NOT NULL DEFAULT 1,
    PRIMARY KEY (id_historico),
    KEY FK_HISTORICO_PRODUTO_PRODUTO (PRODUTO_id_produto),
    CONSTRAINT FK_HISTORICO_PRODUTO_PRODUTO
        FOREIGN KEY (PRODUTO_id_produto) REFERENCES PRODUTO (id_produto)
);

CREATE TABLE VENDA (
    id_venda               INT           NOT NULL AUTO_INCREMENT,
    CLIENTE_PESSOA_id_pessoa INT         NOT NULL,
    CAIXA_PESSOA_id_pessoa INT           NOT NULL,
    data_hora              DATETIME      NOT NULL,
    valor_total            DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    status                 ENUM('ABERTA','PAGA','CANCELADA','ESTORNADA') NOT NULL DEFAULT 'ABERTA',
    forma_pagamento        ENUM('DINHEIRO','PIX','CARTAO_CREDITO','CARTAO_DEBITO','OUTRO') NOT NULL,
    desconto               DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    PRIMARY KEY (id_venda),
    KEY FK_VENDA_CLIENTE (CLIENTE_PESSOA_id_pessoa),
    KEY FK_VENDA_CAIXA (CAIXA_PESSOA_id_pessoa),
    CONSTRAINT FK_VENDA_CLIENTE
        FOREIGN KEY (CLIENTE_PESSOA_id_pessoa) REFERENCES CLIENTE (PESSOA_id_pessoa),
    CONSTRAINT FK_VENDA_CAIXA
        FOREIGN KEY (CAIXA_PESSOA_id_pessoa) REFERENCES CAIXA (PESSOA_id_pessoa)
);

CREATE TABLE VENDA_PRODUTO (
    VENDA_id_venda     INT           NOT NULL,
    PRODUTO_id_produto INT           NOT NULL,
    quantidade         INT           NOT NULL,
    preco_unitario     DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    PRIMARY KEY (VENDA_id_venda, PRODUTO_id_produto),
    KEY FK_VENDA_PRODUTO_PRODUTO (PRODUTO_id_produto),
    CONSTRAINT FK_VENDA_PRODUTO_VENDA
        FOREIGN KEY (VENDA_id_venda) REFERENCES VENDA (id_venda)
        ON DELETE CASCADE,
    CONSTRAINT FK_VENDA_PRODUTO_PRODUTO
        FOREIGN KEY (PRODUTO_id_produto) REFERENCES PRODUTO (id_produto)
);

CREATE TABLE FIDELIDADE (
    id_fidelidade     INT     NOT NULL AUTO_INCREMENT,
    PRODUTO_id_produto INT,
    SERVICO_id_servico INT,
    pontos_acumulados INT     NOT NULL DEFAULT 0,
    pontos_uso        INT     NOT NULL DEFAULT 0,
    ativo             TINYINT NOT NULL DEFAULT 1,
    PRIMARY KEY (id_fidelidade),
    KEY FK_FIDELIDADE_PRODUTO (PRODUTO_id_produto),
    KEY FK_FIDELIDADE_SERVICO (SERVICO_id_servico),
    CONSTRAINT FK_FIDELIDADE_PRODUTO
        FOREIGN KEY (PRODUTO_id_produto) REFERENCES PRODUTO (id_produto),
    CONSTRAINT FK_FIDELIDADE_SERVICO
        FOREIGN KEY (SERVICO_id_servico) REFERENCES SERVICO (id_servico)
);

CREATE TABLE HISTORICO_PONTOS (
    id_movimentacao         INT      NOT NULL AUTO_INCREMENT,
    CLIENTE_PESSOA_id_pessoa INT     NOT NULL,
    VENDA_id_venda          INT      NOT NULL,
    FIDELIDADE_id_fidelidade INT     NOT NULL,
    pontos                  INT      NOT NULL,
    tipo_movimentacao       ENUM('ACUMULA','USA') NOT NULL,
    data_movimentacao       DATETIME NOT NULL,
    PRIMARY KEY (id_movimentacao),
    KEY FK_HISTORICO_PONTOS_CLIENTE (CLIENTE_PESSOA_id_pessoa),
    KEY FK_HISTORICO_PONTOS_VENDA (VENDA_id_venda),
    KEY FK_HISTORICO_PONTOS_FIDELIDADE (FIDELIDADE_id_fidelidade),
    CONSTRAINT FK_HISTORICO_PONTOS_CLIENTE
        FOREIGN KEY (CLIENTE_PESSOA_id_pessoa) REFERENCES CLIENTE (PESSOA_id_pessoa),
    CONSTRAINT FK_HISTORICO_PONTOS_VENDA
        FOREIGN KEY (VENDA_id_venda) REFERENCES VENDA (id_venda),
    CONSTRAINT FK_HISTORICO_PONTOS_FIDELIDADE
        FOREIGN KEY (FIDELIDADE_id_fidelidade) REFERENCES FIDELIDADE (id_fidelidade)
);
