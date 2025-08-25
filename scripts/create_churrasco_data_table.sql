-- Create confra_config table to replace JSON functionality
CREATE TABLE IF NOT EXISTS u629942907_glpi.confra_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_type ENUM('item', 'pessoas_extras') NOT NULL,
    colaborador_id INT,
    nome_colaborador VARCHAR(255),
    item VARCHAR(255),
    quantidade DECIMAL(10,2),
    unidade VARCHAR(50),
    observacoes TEXT,
    extra_pessoas INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_config_type (config_type),
    INDEX idx_colaborador_id (colaborador_id)
);
