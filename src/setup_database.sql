-- Script para configurar as tabelas do sistema de clientes
-- Criação das tabelas principais

-- Tabela para os planos disponíveis
CREATE TABLE IF NOT EXISTS client_planchoice (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    plan_code VARCHAR(2) UNIQUE NOT NULL,
    name VARCHAR(30) UNIQUE NOT NULL,
    cost DECIMAL(4,2) NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_changed DATETIME DEFAULT CURRENT_TIMESTAMP,
    description1 VARCHAR(300) NOT NULL,
    description2 VARCHAR(300) NOT NULL,
    external_plan_id VARCHAR(255) UNIQUE NOT NULL,
    external_api_url VARCHAR(2000) NOT NULL,
    external_style_json VARCHAR(2000) NOT NULL
);

-- Tabela para as assinaturas dos clientes
CREATE TABLE IF NOT EXISTS client_subscription (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cost DECIMAL(4,2) NOT NULL,
    external_subscription_id VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id BIGINT NOT NULL,
    plan_choice_id BIGINT NOT NULL,
    FOREIGN KEY (plan_choice_id) REFERENCES client_planchoice(id),
    FOREIGN KEY (user_id) REFERENCES account_customuser(id)
);

-- Inserir planos padrão
INSERT INTO client_planchoice (
    plan_code, 
    name, 
    cost, 
    is_active, 
    description1, 
    description2, 
    external_plan_id, 
    external_api_url, 
    external_style_json
) VALUES 
('ST', 'Standard', 9.99, TRUE, 
'Access to standard articles and basic features', 
'Perfect for casual readers', 
'P-3RX00000000000000000000000', 
'https://www.paypal.com/sdk/js?client-id=YOUR_CLIENT_ID&vault=true',
'{"layout":"vertical","color":"blue","height":45}'),

('PR', 'Premium', 19.99, TRUE, 
'Access to all articles including premium content', 
'Best for avid readers who want full access', 
'P-4RX00000000000000000000000',
'https://www.paypal.com/sdk/js?client-id=YOUR_CLIENT_ID&vault=true',
'{"layout":"vertical","color":"gold","height":45}'); 