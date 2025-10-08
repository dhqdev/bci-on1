/*
  # Criação de Tabelas do Sistema OXCASH

  1. Tabelas Criadas
    - `boletos`
      - `id` (uuid, primary key)
      - `dia` (text) - '08' ou '16'
      - `nome` (text)
      - `grupo` (text)
      - `cota` (text)
      - `valor` (numeric)
      - `vencimento` (date)
      - `is_completed` (boolean)
      - `protocolo` (text)
      - `documento_url` (text)
      - `created_at` (timestamptz)
      - `updated_at` (timestamptz)

    - `cotas`
      - `id` (uuid, primary key)
      - `dia` (text) - '08' ou '16'
      - `grupo` (text)
      - `cota` (text)
      - `nome` (text)
      - `whatsapp` (text)
      - `created_at` (timestamptz)
      - `updated_at` (timestamptz)

    - `historico_execucoes`
      - `id` (uuid, primary key)
      - `dia` (text)
      - `grupo` (text)
      - `cota` (text)
      - `nome` (text)
      - `valor_lance` (text)
      - `status` (text)
      - `observacao` (text)
      - `protocolo` (text)
      - `documento_url` (text)
      - `docparser_url` (text)
      - `created_at` (timestamptz)

    - `automacao_status`
      - `id` (uuid, primary key)
      - `dia` (text) - '08' ou '16'
      - `is_running` (boolean)
      - `total_tasks` (integer)
      - `completed_tasks` (integer)
      - `failed_tasks` (integer)
      - `current_task` (text)
      - `started_at` (timestamptz)
      - `updated_at` (timestamptz)

  2. Segurança
    - Enable RLS em todas as tabelas
    - Políticas públicas para leitura (demonstração)
    - Políticas autenticadas para escrita
*/

-- Tabela de Boletos
CREATE TABLE IF NOT EXISTS boletos (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  dia text NOT NULL DEFAULT '08',
  nome text NOT NULL,
  grupo text NOT NULL,
  cota text NOT NULL,
  valor numeric DEFAULT 0,
  vencimento date,
  is_completed boolean DEFAULT false,
  protocolo text,
  documento_url text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE boletos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Permitir leitura pública de boletos"
  ON boletos FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Permitir inserção autenticada de boletos"
  ON boletos FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Permitir atualização autenticada de boletos"
  ON boletos FOR UPDATE
  TO authenticated
  USING (true)
  WITH CHECK (true);

-- Tabela de Cotas
CREATE TABLE IF NOT EXISTS cotas (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  dia text NOT NULL DEFAULT '08',
  grupo text NOT NULL,
  cota text NOT NULL,
  nome text NOT NULL,
  whatsapp text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE cotas ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Permitir leitura pública de cotas"
  ON cotas FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Permitir inserção autenticada de cotas"
  ON cotas FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Permitir atualização autenticada de cotas"
  ON cotas FOR UPDATE
  TO authenticated
  USING (true)
  WITH CHECK (true);

-- Tabela de Histórico de Execuções
CREATE TABLE IF NOT EXISTS historico_execucoes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  dia text NOT NULL,
  grupo text NOT NULL,
  cota text NOT NULL,
  nome text NOT NULL,
  valor_lance text DEFAULT 'N/A',
  status text NOT NULL,
  observacao text,
  protocolo text,
  documento_url text,
  docparser_url text,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE historico_execucoes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Permitir leitura pública de histórico"
  ON historico_execucoes FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Permitir inserção autenticada de histórico"
  ON historico_execucoes FOR INSERT
  TO authenticated
  WITH CHECK (true);

-- Tabela de Status de Automação
CREATE TABLE IF NOT EXISTS automacao_status (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  dia text NOT NULL UNIQUE,
  is_running boolean DEFAULT false,
  total_tasks integer DEFAULT 0,
  completed_tasks integer DEFAULT 0,
  failed_tasks integer DEFAULT 0,
  current_task text,
  started_at timestamptz,
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE automacao_status ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Permitir leitura pública de status"
  ON automacao_status FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Permitir inserção autenticada de status"
  ON automacao_status FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Permitir atualização autenticada de status"
  ON automacao_status FOR UPDATE
  TO authenticated
  USING (true)
  WITH CHECK (true);

-- Inserir registros iniciais de status
INSERT INTO automacao_status (dia, is_running) VALUES ('08', false)
ON CONFLICT (dia) DO NOTHING;

INSERT INTO automacao_status (dia, is_running) VALUES ('16', false)
ON CONFLICT (dia) DO NOTHING;

-- Criar índices para performance
CREATE INDEX IF NOT EXISTS idx_boletos_dia ON boletos(dia);
CREATE INDEX IF NOT EXISTS idx_boletos_is_completed ON boletos(is_completed);
CREATE INDEX IF NOT EXISTS idx_cotas_dia ON cotas(dia);
CREATE INDEX IF NOT EXISTS idx_historico_dia ON historico_execucoes(dia);
CREATE INDEX IF NOT EXISTS idx_historico_created_at ON historico_execucoes(created_at DESC);
