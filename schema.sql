-- ====================================================================
-- ESQUEMA DE BANCO DE DADOS POSTGRESQL (SUPABASE)
-- PROJETO: GESTÃO DE MANUTENÇÃO SEINFRA / UFG
-- OBJETIVO: SUPORTAR 156K REGISTROS E CONSULTAS ANALÍTICAS DE MILISSEGUNDOS
-- ====================================================================

-- 1. TABELA PRINCIPAL DE CHAMADOS (HISTÓRICO REAL DO CSV)
CREATE TABLE IF NOT EXISTS public.chamados (
    id BIGSERIAL PRIMARY KEY,
    requisicao TEXT,
    divisao TEXT NOT NULL,
    codigo_unidade_requisitante TEXT,
    unidade_requisitante TEXT,
    local TEXT,
    oficina TEXT NOT NULL,
    servico TEXT,
    status TEXT NOT NULL,
    data_abertura TIMESTAMPTZ NOT NULL,
    data_finalizacao TIMESTAMPTZ,
    vinculo TEXT,
    profissional TEXT,
    quantidade_horas NUMERIC(10, 2) DEFAULT 0,
    descricao TEXT,
    observacoes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. ÍNDICES DE PERFORMANCE ESTRATÉGICOS (MANDATÓRIOS PARA PESQUISAS E AGREGADOS)
CREATE INDEX IF NOT EXISTS idx_chamados_oficina ON public.chamados(oficina);
CREATE INDEX IF NOT EXISTS idx_chamados_status ON public.chamados(status);
CREATE INDEX IF NOT EXISTS idx_chamados_divisao ON public.chamados(divisao);
CREATE INDEX IF NOT EXISTS idx_chamados_data_abertura ON public.chamados(data_abertura);
CREATE INDEX IF NOT EXISTS idx_chamados_profissional ON public.chamados(profissional);
CREATE INDEX IF NOT EXISTS idx_chamados_unidade ON public.chamados(unidade_requisitante);
CREATE INDEX IF NOT EXISTS idx_chamados_oficina_ano ON public.chamados(oficina, EXTRACT(YEAR FROM (data_abertura AT TIME ZONE 'UTC')));

-- ====================================================================
-- VIEWS DE AGREGAÇÃO ANALÍTICA PARA CARREGAMENTO ULTRA RÁPIDO DO FRONTEND
-- ====================================================================

-- VIEW 1: KPI CARD GLOBAS (Visão Geral - Topbar e cards principais)
CREATE OR REPLACE VIEW public.view_kpis_globais AS
WITH stats AS (
    SELECT 
        COUNT(id) AS total_requisicoes,
        SUM(quantidade_horas) AS total_horas,
        COUNT(CASE WHEN status = 'FINALIZADA' THEN 1 END) AS total_finalizadas,
        COUNT(CASE WHEN status != 'FINALIZADA' THEN 1 END) AS total_abertas
    FROM public.chamados
),
mediana AS (
    -- Cálculo exato da mediana de SLA (em dias) para chamados finalizados
    SELECT COALESCE(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (data_finalizacao - data_abertura)) / 86400), 0)::NUMERIC(10,1) AS mediana_sla
    FROM public.chamados
    WHERE status = 'FINALIZADA' AND data_finalizacao IS NOT NULL
)
SELECT 
    s.total_requisicoes,
    s.total_horas::NUMERIC(15,2) AS total_horas,
    s.total_finalizadas,
    s.total_abertas,
    m.mediana_sla,
    (CASE WHEN s.total_requisicoes > 0 THEN (s.total_horas / s.total_requisicoes) ELSE 0 END)::NUMERIC(10,2) AS media_horas_req
FROM stats s, mediana m;


-- VIEW 2: TENDÊNCIA ANUAL E MENSAL (Volume de Requisições e Horas)
CREATE OR REPLACE VIEW public.view_mensal_req_horas AS
SELECT 
    EXTRACT(YEAR FROM data_abertura)::INTEGER AS ano,
    EXTRACT(MONTH FROM data_abertura)::INTEGER AS mes,
    COUNT(id) AS total_requisicoes,
    SUM(quantidade_horas)::NUMERIC(15,2) AS total_horas
FROM public.chamados
GROUP BY EXTRACT(YEAR FROM data_abertura)::INTEGER, EXTRACT(MONTH FROM data_abertura)::INTEGER
ORDER BY ano, mes;


-- VIEW 3: DISTRIBUIÇÃO E DETALHAMENTO POR STATUS
CREATE OR REPLACE VIEW public.view_status_distribuicao AS
SELECT 
    status,
    COUNT(id) AS total_requisicoes,
    SUM(quantidade_horas)::NUMERIC(15,2) AS total_horas
FROM public.chamados
GROUP BY status
ORDER BY total_requisicoes DESC;


-- VIEW 4: HORAS E REQUISIÇÕES POR OFICINA (Para o Top 10 Oficinas)
CREATE OR REPLACE VIEW public.view_horas_oficina AS
SELECT 
    oficina,
    COUNT(id) AS total_requisicoes,
    SUM(quantidade_horas)::NUMERIC(15,2) AS total_horas
FROM public.chamados
GROUP BY oficina
ORDER BY total_horas DESC;


-- VIEW 5: TOP 10 UNIDADES REQUISITANTES (Por volume de requisições abertas)
CREATE OR REPLACE VIEW public.view_unidades_solicitantes AS
SELECT 
    unidade_requisitante,
    COUNT(id) AS total_requisicoes
FROM public.chamados
GROUP BY unidade_requisitante
ORDER BY total_requisicoes DESC;


-- VIEW 6: HISTÓRICO YOY POR DIVISÃO E ANO
CREATE OR REPLACE VIEW public.view_yoy_divisao AS
SELECT 
    EXTRACT(YEAR FROM data_abertura)::INTEGER AS ano,
    divisao,
    COUNT(id) AS total_requisicoes,
    SUM(quantidade_horas)::NUMERIC(15,2) AS total_horas
FROM public.chamados
GROUP BY EXTRACT(YEAR FROM data_abertura)::INTEGER, divisao
ORDER BY ano, divisao;


-- VIEW 7: PERFORMANCE GERAL DOS PROFISSIONAIS (Mestre acumulado)
CREATE OR REPLACE VIEW public.view_profissionais_performance AS
SELECT 
    profissional AS n,
    oficina AS ofic,
    vinculo,
    COUNT(id) AS req,
    SUM(quantidade_horas)::NUMERIC(15,2) AS horas,
    (CASE WHEN COUNT(id) > 0 THEN (SUM(quantidade_horas) / COUNT(id)) ELSE 0 END)::NUMERIC(10,1) AS media,
    COALESCE(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (data_finalizacao - data_abertura)) / 86400), 999)::INTEGER AS sla
FROM public.chamados
WHERE profissional IS NOT NULL AND profissional != ''
GROUP BY profissional, oficina, vinculo
ORDER BY req DESC;


-- VIEW 8: PERFORMANCE ANUAL DOS PROFISSIONAIS
CREATE OR REPLACE VIEW public.view_profissionais_performance_anual AS
SELECT 
    EXTRACT(YEAR FROM data_abertura)::INTEGER AS ano,
    profissional AS n,
    oficina AS ofic,
    vinculo,
    COUNT(id) AS req,
    SUM(quantidade_horas)::NUMERIC(15,2) AS horas,
    (CASE WHEN COUNT(id) > 0 THEN (SUM(quantidade_horas) / COUNT(id)) ELSE 0 END)::NUMERIC(10,1) AS media,
    COALESCE(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (data_finalizacao - data_abertura)) / 86400), 999)::INTEGER AS sla
FROM public.chamados
WHERE profissional IS NOT NULL AND profissional != ''
GROUP BY EXTRACT(YEAR FROM data_abertura)::INTEGER, profissional, oficina, vinculo
ORDER BY ano, req DESC;


-- VIEW 9: SAZONALIDADE DETALHADA POR OFICINA, ANO E MÊS (Para Heatmaps)
CREATE OR REPLACE VIEW public.view_sazonalidade_oficina AS
SELECT 
    EXTRACT(YEAR FROM data_abertura)::INTEGER AS ano,
    EXTRACT(MONTH FROM data_abertura)::INTEGER AS mes,
    oficina,
    COUNT(id) AS total_requisicoes,
    SUM(quantidade_horas)::NUMERIC(15,2) AS total_horas,
    COUNT(CASE WHEN status = 'FINALIZADA' THEN 1 END) AS total_finalizadas
FROM public.chamados
GROUP BY EXTRACT(YEAR FROM data_abertura)::INTEGER, EXTRACT(MONTH FROM data_abertura)::INTEGER, oficina
ORDER BY ano, mes, oficina;


-- VIEW 10: EFICIÊNCIA OPERACIONAL E GARGALOS POR OFICINA E ANO (Matriz de Dispersão Scatter)
CREATE OR REPLACE VIEW public.view_eficiencia_oficinas AS
SELECT 
    EXTRACT(YEAR FROM data_abertura)::INTEGER AS ano,
    oficina,
    divisao,
    COUNT(id) AS total_requisicoes,
    COALESCE(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (data_finalizacao - data_abertura)) / 86400), 0)::INTEGER AS sla,
    (CASE WHEN COUNT(id) > 0 THEN (SUM(quantidade_horas) / COUNT(id)) ELSE 0 END)::NUMERIC(10,1) AS horas
FROM public.chamados
GROUP BY EXTRACT(YEAR FROM data_abertura)::INTEGER, oficina, divisao
ORDER BY ano, total_requisicoes DESC;


-- POLÍTICAS DE ROW LEVEL SECURITY (RLS) PARA LEITURA PÚBLICA / ESCRITA SEGURA
ALTER TABLE public.chamados ENABLE ROW LEVEL SECURITY;

-- Limpar políticas antigas se existirem
DROP POLICY IF EXISTS "Permitir leitura pública de chamados" ON public.chamados;
DROP POLICY IF EXISTS "Permitir tudo apenas para service_role" ON public.chamados;

-- Política 1: Leitura livre (SELECT) para usuários anônimos (Dashboard Público)
CREATE POLICY "Permitir leitura pública de chamados" 
ON public.chamados 
FOR SELECT 
TO anon, authenticated 
USING (true);

-- Política 2: Inserção livre (INSERT) e Modificação (ALL) reservada para chave de serviço privada (ETL script)
CREATE POLICY "Permitir tudo apenas para service_role" 
ON public.chamados 
FOR ALL 
TO service_role 
USING (true) 
WITH CHECK (true);
