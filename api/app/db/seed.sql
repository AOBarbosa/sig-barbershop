USE sig_barbershop;

-- -----------------------------------------------------
-- PESSOA
-- -----------------------------------------------------
INSERT INTO PESSOA (nome, cpf, email, data_nascimento) VALUES
('Carlos Mendes',   '11122233344', 'carlos@email.com',   '1990-03-15'),
('Ana Lima',        '22233344455', 'ana@email.com',       '1985-07-22'),
('Pedro Souza',     '33344455566', 'pedro@email.com',     '1992-11-08'),
('Juliana Costa',   '44455566677', 'juliana@email.com',   '1988-05-30'),
('Roberto Alves',   '55566677788', 'roberto@email.com',   '1995-01-17'),
('Fernanda Nunes',  '66677788899', 'fernanda@email.com',  '1993-09-04'),
('Marcos Oliveira', '77788899900', 'marcos@email.com',    '1980-12-25'),
('Beatriz Santos',  '88899900011', 'beatriz@email.com',   '1997-06-14');

-- -----------------------------------------------------
-- TELEFONE
-- -----------------------------------------------------
INSERT INTO TELEFONE (PESSOA_id_pessoa, numero) VALUES
(1, '84991110001'),
(2, '84991110002'),
(3, '84991110003'),
(4, '84991110004'),
(5, '84991110005'),
(6, '84991110006'),
(7, '84991110007'),
(8, '84991110008');

-- -----------------------------------------------------
-- CLIENTE (pessoas 1, 2, 3, 4)
-- -----------------------------------------------------
INSERT INTO CLIENTE (PESSOA_id_pessoa) VALUES (1), (2), (3), (4);

-- -----------------------------------------------------
-- CAIXA (pessoa 5)
-- -----------------------------------------------------
INSERT INTO CAIXA (PESSOA_id_pessoa) VALUES (5);

-- -----------------------------------------------------
-- BARBEIRO (pessoas 6, 7, 8)
-- -----------------------------------------------------
INSERT INTO BARBEIRO (PESSOA_id_pessoa, especialidade, ativo) VALUES
(6, 'Corte degradê',      TRUE),
(7, 'Barba e bigode',     TRUE),
(8, 'Corte infantil',     TRUE);

-- -----------------------------------------------------
-- DISPONIBILIDADE
-- -----------------------------------------------------
INSERT INTO DISPONIBILIDADE (BARBEIRO_id_barbeiro, dia_semana, hora_inicio, hora_fim) VALUES
(1, 'segunda', '08:00', '18:00'),
(1, 'terca',   '08:00', '18:00'),
(1, 'quarta',  '08:00', '18:00'),
(1, 'quinta',  '08:00', '18:00'),
(1, 'sexta',   '08:00', '18:00'),
(2, 'segunda', '09:00', '17:00'),
(2, 'quarta',  '09:00', '17:00'),
(2, 'sexta',   '09:00', '17:00'),
(2, 'sabado',  '09:00', '14:00'),
(3, 'terca',   '10:00', '19:00'),
(3, 'quinta',  '10:00', '19:00'),
(3, 'sabado',  '08:00', '16:00');

-- -----------------------------------------------------
-- SERVICO
-- -----------------------------------------------------
INSERT INTO SERVICO (nome, descricao, preco, duracao_minutos, ativo) VALUES
('Corte simples',   'Corte de cabelo simples',           25.00, 30, TRUE),
('Corte degradê',   'Corte com técnica degradê',         40.00, 45, TRUE),
('Barba',           'Aparar e modelar barba',            20.00, 20, TRUE),
('Corte + Barba',   'Combo corte e barba',               55.00, 60, TRUE),
('Hidratação',      'Hidratação capilar',                35.00, 40, TRUE),
('Corte infantil',  'Corte para crianças até 12 anos',   20.00, 25, TRUE);

-- -----------------------------------------------------
-- HISTORICO_SERVICO
-- -----------------------------------------------------
INSERT INTO HISTORICO_SERVICO (SERVICO_id_servico, preco_anterior, preco_novo, ativo, alterado_em) VALUES
(1, 20.00, 25.00, TRUE, '2025-01-10 10:00:00'),
(2, 35.00, 40.00, TRUE, '2025-01-10 10:00:00'),
(4, 45.00, 55.00, TRUE, '2025-03-01 09:00:00');

-- -----------------------------------------------------
-- PRODUTO
-- -----------------------------------------------------
INSERT INTO PRODUTO (nome, descricao, preco, estoque, ativo) VALUES
('Pomada modeladora', 'Pomada para modelagem de cabelo', 35.00, 20, TRUE),
('Shampoo masculino', 'Shampoo para cabelos masculinos', 25.00, 15, TRUE),
('Óleo para barba',   'Óleo hidratante para barba',      30.00, 12, TRUE),
('Cera capilar',      'Cera de fixação forte',           28.00, 18, TRUE);

-- -----------------------------------------------------
-- HISTORICO_PRODUTO
-- -----------------------------------------------------
INSERT INTO HISTORICO_PRODUTO (PRODUTO_id_produto, preco_anterior, preco_novo, estoque_anterior, estoque_novo, ativo, alterado_em) VALUES
(1, 30.00, 35.00, 25, 20, TRUE, '2025-02-15 11:00:00'),
(3, 25.00, 30.00, 10, 12, TRUE, '2025-04-01 14:00:00');

-- -----------------------------------------------------
-- ATENDIMENTO
-- -----------------------------------------------------
INSERT INTO ATENDIMENTO (CLIENTE_id_cliente, BARBEIRO_id_barbeiro, data_hora, status, valor_total) VALUES
(1, 1, '2026-06-10 09:00:00', 'concluido',    40.00),
(2, 2, '2026-06-10 10:00:00', 'concluido',    55.00),
(3, 3, '2026-06-11 14:00:00', 'concluido',    20.00),
(4, 1, '2026-06-15 08:00:00', 'cancelado',     0.00),
(1, 2, '2026-07-05 09:00:00', 'agendado',      0.00);

-- -----------------------------------------------------
-- ATENDIMENTO_SERVICO
-- -----------------------------------------------------
INSERT INTO ATENDIMENTO_SERVICO (ATENDIMENTO_id_atendimento, SERVICO_id_servico, preco_cobrado) VALUES
(1, 2, 40.00),
(2, 4, 55.00),
(3, 3, 20.00);

-- -----------------------------------------------------
-- VENDA
-- -----------------------------------------------------
INSERT INTO VENDA (CLIENTE_id_cliente, CAIXA_id_caixa, valor_total, status, forma_pagamento) VALUES
(1, 1, 35.00, 'concluida', 'pix'),
(2, 1, 55.00, 'concluida', 'cartao_credito'),
(3, 1, 28.00, 'concluida', 'dinheiro'),
(4, 1,  0.00, 'pendente',   NULL);

-- -----------------------------------------------------
-- VENDA_PRODUTO
-- -----------------------------------------------------
INSERT INTO VENDA_PRODUTO (VENDA_id_venda, PRODUTO_id_produto, quantidade, preco_unitario) VALUES
(1, 1, 1, 35.00),
(2, 2, 1, 25.00),
(2, 3, 1, 30.00),
(3, 4, 1, 28.00);

-- -----------------------------------------------------
-- FIDELIDADE
-- -----------------------------------------------------
INSERT INTO FIDELIDADE (SERVICO_id_servico, PRODUTO_id_produto, pontos, ativo) VALUES
(1, NULL, 10, TRUE),
(2, NULL, 15, TRUE),
(3, NULL,  8, TRUE),
(4, NULL, 20, TRUE),
(NULL, 1,  5, TRUE),
(NULL, 2,  3, TRUE),
(NULL, 3,  4, TRUE);

-- -----------------------------------------------------
-- HISTORICO_PONTOS
-- -----------------------------------------------------
INSERT INTO HISTORICO_PONTOS (CLIENTE_id_cliente, pontos, tipo_movimentacao, descricao) VALUES
(1, 15, 'acumulo', 'Corte degradê - atendimento #1'),
(2, 20, 'acumulo', 'Corte + Barba - atendimento #2'),
(3,  8, 'acumulo', 'Barba - atendimento #3'),
(1,  5, 'acumulo', 'Compra pomada modeladora - venda #1'),
(2, 10, 'resgate', 'Resgate de pontos por desconto');
