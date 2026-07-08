USE sig_barbershop;

INSERT INTO PESSOA (id_pessoa, nome, cpf, email, data_nascimento, admin) VALUES
(1, 'Carlos Mendes', '11122233344', 'carlos@email.com', '1990-03-15', 0),
(2, 'Ana Lima', '22233344455', 'ana@email.com', '1985-07-22', 0),
(3, 'Pedro Souza', '33344455566', 'pedro@email.com', '1992-11-08', 0),
(4, 'Juliana Costa', '44455566677', 'juliana@email.com', '1988-05-30', 0),
(5, 'Roberto Alves', '55566677788', 'roberto@email.com', '1995-01-17', 1),
(6, 'Fernanda Nunes', '66677788899', 'fernanda@email.com', '1993-09-04', 0),
(7, 'Marcos Oliveira', '77788899900', 'marcos@email.com', '1980-12-25', 0),
(8, 'Beatriz Santos', '88899900011', 'beatriz@email.com', '1997-06-14', 0);

INSERT INTO TELEFONE (PESSOA_id_pessoa, telefone) VALUES
(1, '84991110001'),
(2, '84991110002'),
(3, '84991110003'),
(4, '84991110004'),
(5, '84991110005'),
(6, '84991110006'),
(7, '84991110007'),
(8, '84991110008');

INSERT INTO CLIENTE (PESSOA_id_pessoa, preferencias, observacoes) VALUES
(1, 'Corte baixo', 'Cliente mensal'),
(2, 'Barba desenhada', NULL),
(3, 'Corte social', NULL),
(4, NULL, 'Prefere atendimento pela manha');

INSERT INTO CAIXA (PESSOA_id_pessoa) VALUES (5);

INSERT INTO BARBEIRO (PESSOA_id_pessoa, apelido, comissao_percentual) VALUES
(6, 'Nanda', 40.00),
(7, 'Marcos', 45.00),
(8, 'Bia', 35.00);

INSERT INTO DISPONIBILIDADE (
    BARBEIRO_PESSOA_id_pessoa,
    dia_semana,
    hora_inicio,
    hora_fim,
    ativo
) VALUES
(6, 'SEGUNDA', '08:00', '18:00', 1),
(6, 'TERCA', '08:00', '18:00', 1),
(6, 'QUARTA', '08:00', '18:00', 1),
(7, 'SEGUNDA', '09:00', '17:00', 1),
(7, 'SEXTA', '09:00', '17:00', 1),
(8, 'SABADO', '08:00', '16:00', 1);

INSERT INTO SERVICO (id_servico, nome, ativo) VALUES
(1, 'Corte simples', 1),
(2, 'Corte degrade', 1),
(3, 'Barba', 1),
(4, 'Corte + Barba', 1),
(5, 'Hidratacao', 1),
(6, 'Corte infantil', 1);

INSERT INTO HISTORICO_SERVICO (
    SERVICO_id_servico,
    preco,
    duracao_em_minutos,
    pontos_gerados,
    data_inicio,
    data_fim,
    ativo
) VALUES
(1, 25.00, 30, 10, '2026-01-01', NULL, 1),
(2, 40.00, 45, 15, '2026-01-01', NULL, 1),
(3, 20.00, 20, 8, '2026-01-01', NULL, 1),
(4, 55.00, 60, 20, '2026-01-01', NULL, 1),
(5, 35.00, 40, 12, '2026-01-01', NULL, 1),
(6, 20.00, 25, 8, '2026-01-01', NULL, 1);

INSERT INTO PRODUTO (id_produto, nome, categoria, ativo) VALUES
(1, 'Pomada modeladora', 'Finalizador', 1),
(2, 'Shampoo masculino', 'Higiene', 1),
(3, 'Oleo para barba', 'Barba', 1),
(4, 'Cera capilar', 'Finalizador', 1);

INSERT INTO HISTORICO_PRODUTO (
    PRODUTO_id_produto,
    preco_venda,
    preco_custo,
    pontos_gerados,
    data_inicio,
    data_fim,
    ativo
) VALUES
(1, 35.00, 18.00, 5, '2026-01-01', NULL, 1),
(2, 25.00, 12.00, 3, '2026-01-01', NULL, 1),
(3, 30.00, 14.00, 4, '2026-01-01', NULL, 1),
(4, 28.00, 13.00, 4, '2026-01-01', NULL, 1);

INSERT INTO ATENDIMENTO (
    id_atendimento,
    CLIENTE_PESSOA_id_pessoa,
    BARBEIRO_PESSOA_id_pessoa,
    data_hora_inicio,
    data_hora_fim,
    valor_total,
    status,
    observacoes
) VALUES
(1, 1, 6, '2026-06-10 09:00:00', '2026-06-10 09:45:00', 40.00, 'CONCLUIDO', NULL),
(2, 2, 7, '2026-06-10 10:00:00', '2026-06-10 11:00:00', 55.00, 'CONCLUIDO', NULL),
(3, 3, 8, '2026-06-11 14:00:00', '2026-06-11 14:20:00', 20.00, 'CONCLUIDO', NULL),
(4, 4, 6, '2026-06-15 08:00:00', NULL, 0.00, 'CANCELADO', 'Cliente cancelou'),
(5, 1, 7, '2026-07-05 09:00:00', NULL, 0.00, 'AGENDADO', NULL);

INSERT INTO ATENDIMENTO_SERVICO (
    ATENDIMENTO_id_atendimento,
    SERVICO_id_servico,
    preco_cobrado
) VALUES
(1, 2, 40.00),
(2, 4, 55.00),
(3, 3, 20.00);

INSERT INTO VENDA (
    id_venda,
    CLIENTE_PESSOA_id_pessoa,
    CAIXA_PESSOA_id_pessoa,
    data_hora,
    valor_total,
    status,
    forma_pagamento,
    desconto
) VALUES
(1, 1, 5, '2026-06-10 09:50:00', 35.00, 'PAGA', 'PIX', 0.00),
(2, 2, 5, '2026-06-10 11:05:00', 55.00, 'PAGA', 'CARTAO_CREDITO', 0.00),
(3, 3, 5, '2026-06-11 14:30:00', 28.00, 'PAGA', 'DINHEIRO', 0.00),
(4, 4, 5, '2026-07-01 10:00:00', 0.00, 'ABERTA', 'OUTRO', 0.00);

INSERT INTO VENDA_PRODUTO (
    VENDA_id_venda,
    PRODUTO_id_produto,
    quantidade,
    preco_unitario
) VALUES
(1, 1, 1, 35.00),
(2, 2, 1, 25.00),
(2, 3, 1, 30.00),
(3, 4, 1, 28.00);

INSERT INTO FIDELIDADE (
    id_fidelidade,
    PRODUTO_id_produto,
    SERVICO_id_servico,
    pontos_acumulados,
    pontos_uso,
    ativo
) VALUES
(1, NULL, 1, 10, 100, 1),
(2, NULL, 2, 15, 150, 1),
(3, NULL, 3, 8, 80, 1),
(4, NULL, 4, 20, 200, 1),
(5, 1, NULL, 5, 50, 1),
(6, 2, NULL, 3, 30, 1),
(7, 3, NULL, 4, 40, 1);

INSERT INTO HISTORICO_PONTOS (
    CLIENTE_PESSOA_id_pessoa,
    VENDA_id_venda,
    FIDELIDADE_id_fidelidade,
    pontos,
    tipo_movimentacao,
    data_movimentacao
) VALUES
(1, 1, 5, 5, 'ACUMULA', '2026-06-10 09:50:00'),
(2, 2, 6, 3, 'ACUMULA', '2026-06-10 11:05:00'),
(2, 2, 7, 4, 'ACUMULA', '2026-06-10 11:05:00'),
(3, 3, 7, 4, 'ACUMULA', '2026-06-11 14:30:00');
