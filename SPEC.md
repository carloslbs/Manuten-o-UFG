# Especificação Técnica: Dashboard de Manutenção SEINFRA

## 1. Visão Geral
O **Dashboard de Manutenção SEINFRA** é uma aplicação web single-page (SPA) projetada para monitorar, analisar e otimizar as operações de manutenção predial, de serviços e de equipamentos da UFG. Ele consolida dados históricos (2019-2026) para oferecer insights sobre produtividade, cumprimento de prazos (SLA), sazonalidade de demandas e tendências ano a ano.

---

## 2. Stack Tecnológica
- **Core:** HTML5 semântico, CSS3 (Vanilla com Variáveis CSS).
- **Lógica:** JavaScript (ES6+ Vanilla).
- **Gráficos:** [Chart.js](https://www.chartjs.org/) (v4.4.1 - carregado via CDN UMD).
- **Tipografia:** DM Sans (Interface) e DM Mono (Dados/Números) via Google Fonts.
- **Ícones:** Emojis nativos para máxima performance, compatibilidade e tempo de carregamento zero.

---

## 3. Design System & Identidade Visual
O design segue uma estética *Premium/Minimalista*, focada em legibilidade, contraste harmônico e densidade de informações sem sobrecarga cognitiva.

### 3.1. Paleta de Cores (Design Tokens)

#### Modo Claro (Default)
As variáveis de cor são declaradas no `:root` e proporcionam um visual off-white limpo:
- **Background (`--bg`):** `#F4F2ED` (Off-white quente, confortável para leitura prolongada).
- **Superfície Principal (`--surface`):** `#FAFAF8` (Fundo dos cards e contêineres).
- **Superfície Secundária (`--surface2`):** `#EFEDE7` (Áreas de hover e elementos de suporte).
- **Bordas (`--border` / `--border2`):** `#E0DDD5` / `#D0CCC2`.
- **Textos (`--text` / `--text2` / `--text3`):** `#1A1916` (Principal) / `#6B6860` (Secundário) / `#9B9890` (Suporte).
- **Destaque Principal (`--accent`):** `#1B4F8A` (Azul Institucional / SEINFRA).
- **Destaque Secundário (`--accent2`):** `#1A7A5E` (Verde).
- **Cores Semânticas:**
  - **Status Ok (`--ok`):** `#3A6610` (Verde Oliva Profundo).
  - **Alerta (`--warn`):** `#8A4A10` (Bronze/Âmbar).
  - **Crítico (`--danger`):** `#8A1F1F` (Vermelho Escuro).

#### Modo Escuro (Dark Mode)
Ativado adicionando a classe `.dark` no elemento `body`, invertendo as variáveis para tons de carbono e cinza profundo:
- **Background (`--bg`):** `#141412`.
- **Superfície Principal (`--surface`):** `#1C1C1A`.
- **Superfície Secundária (`--surface2`):** `#252522`.
- **Bordas (`--border` / `--border2`):** `#2E2E2A` / `#3A3A35`.
- **Textos (`--text` / `--text2` / `--text3`):** `#F5F2EC` / `#CCC8C0` / `#9E9A92`.
- **Destaque Principal (`--accent`):** `#4A8FE0` (Azul adaptado para contraste).
- **Destaque Secundário (`--accent2`):** `#3ABB8A` (Verde esmeralda).
- **Cores Semânticas:**
  - **Status Ok (`--ok`):** `#70C030`.
  - **Alerta (`--warn`):** `#D09040`.
  - **Crítico (`--danger`):** `#D05555`.

### 3.2. Layout
- **Sidebar (Navegação):** Menu fixo à esquerda com 220px de largura. Contém o logotipo da instituição, links das seções, chave de configurações (modal) e o período ativo dos dados.
- **Topbar:** Cabeçalho adaptável que muda dinamicamente o título contextual conforme a aba selecionada e apresenta 3 badges globais em tempo real: total de requisições, total de horas e volume de ordens em aberto.
- **Content Area:** Grid e colunas totalmente responsivas via CSS Grid/Flexbox, adaptando-se de forma fluida para 1 coluna em telas menores que 900px, com a ocultação automatizada da sidebar para maximizar o espaço de visualização móvel.

---

## 4. Módulos e Funcionalidades

### 4.1. Visão Geral (Overview)
Apresenta o panorama consolidado do pipeline de manutenções:
- **KPIs Principais (6 Cards):**
  1. Total de Requisições (Volume absoluto).
  2. Total de Horas registradas.
  3. Finalizadas (Volume absoluto e percentual de conversão).
  4. Em aberto (Volume absoluto e percentual pendente).
  5. Mediana SLA (Tempo mediano de encerramento das ordens).
  6. Média de horas por requisição.
- **Gráficos e Tabelas de Distribuição:**
  - **Volume Mensal de Requisições:** Gráfico de linha temporal temporal mostrando a oscilação de volume anual (2019-2026).
  - **Horas por Oficina:** Top 10 especialidades com maior consumo de horas trabalhadas em gráfico de barras horizontais.
  - **Distribuição por Status:** Gráfico de rosca (doughnut) mostrando o percentual de cada status.
  - **Horas por Divisão × Vínculo:** Gráfico de barras agrupadas comparando horas executadas por funcionários Terceirizados vs. Servidores próprios da UFG por Divisão.
  - **Status Detalhado:** Tabela analítica mapeando a quantidade, percentual representativo e soma de horas para cada status ativo.
  - **Top 10 Unidades Requisitantes:** Gráfico de barras horizontais indicando os maiores solicitantes do campus.

### 4.2. Painel de SLA (Service Level Agreement)
Focado no controle de prazos e detecção de gargalos críticos de resolução:
- **Filtros Locais:** Barra dedicada de filtros de refinamento por **Ano**, **Divisão**, **Oficina** e **Status**, além de um botão de reinicialização rápida.
- **Métricas do Painel:**
  - % de requisições finalizadas Fora do SLA (considerando a métrica de 90+ dias).
  - % de requisições finalizadas Dentro de 7 dias.
  - Mediana de resolução em dias com indicação de P75 (Percentil 75).
  - Volume absoluto de ordens em aberto crítico (paradas há mais de 90 dias).
  - Exibição de P90 e P95 para análise estatística de cauda longa.
- **Componentes de Análise:**
  - **Distribuição por faixa de prazo:** Barras comparativas de faixas temporais (0-7d, 8-15d, 16-30d, 31-90d, 90+d) separadas entre Ordens Finalizadas e Ordens Em Aberto.
  - **Alertas Críticos de SLA:** Cards de avisos coloridos sinalizando pontos graves (ex: status "Enviada" inalterado há mais de 6 anos; oficinas de Pintura/Alvenaria com tempos médios altos; taxas excessivas de requisições pendentes por muito tempo).
  - **SLA por Oficina (Top 10):** Tabela mapeando Mediana, Média e classificação qualitativa (Bom, Regular, Crítico).
  - **Evolução Temporal do SLA:** Gráfico de tendência horizontal mostrando a evolução ano a ano do percentual de ordens finalizadas em até 30 dias.
  - **Tempo Médio de Ordens Abertas por Status:** Tabela informando a quantidade e o atraso médio decorrido em dias para cada status de transição.

### 4.3. Ranking de Profissionais
Mapeamento detalhado da produtividade individual de cada técnico da equipe:
- **Filtros Locais:** Busca textual por nome do profissional, filtro por **Ano**, **Oficina**, **Faixa de SLA** (Bom, Regular, Crítico) e ordenação dinâmica por volume de requisições, horas totais, melhor/pior SLA ou média de horas.
- **Métricas de Performance:** Cards dinâmicos apontando quantidade de profissionais filtrados, requisições totais, soma de horas, melhor SLA individual e pior SLA individual com os nomes dos profissionais correspondentes.
- **Interface Visual:**
  - **Top 15 por Requisições:** Lista de profissionais exibindo avatar colorido com base na oficina, barras de progresso, total de horas e badge semântico indicando a mediana de SLA.
  - **Top 15 por Horas:** Ranking dos profissionais ordenados pelo total absoluto de horas de esforço de trabalho.
  - **Tabela Completa de Profissionais:** Visualização tabular de toda a equipe com cabeçalhos ordenáveis ao clique (`#`, Nome, Oficina, Req, Horas, Média h/req, SLA mediana).

### 4.4. Sazonalidade (Heatmaps)
Identificação visual rápida de surtos sazonais de demanda e picos operacionais ao longo dos meses e anos:
- **Filtros Locais:** Filtro por Oficina com atualização reativa de volume.
- **Matrizes Sazonais (Mes x Ano):**
  - **Heatmap de Requisições Abertas:** Grade bidimensional de densidade cromática, onde células com maior volume de requisições ganham coloração azul escura (`#C8DCF0` -> `#0D2E52`).
  - **Heatmap de Horas Registradas:** Grade baseada em cores verdes (`#B8E8D8` -> `#083D28`) destacando períodos de maior esforço de trabalho técnico.
- **KPI Compacto Integrado:** Contador rápido do "Total de Requisições" correspondente ao filtro de oficina ativo no momento da análise.
- **Insights Sazonais Estáticos:** Alertas explicativos que sumarizam os padrões históricos, apontando o pico tradicional nos meses de Setembro e Outubro (retorno do recesso acadêmico) e a baixa em Maio.

### 4.5. Comparativo Ano a Ano (YoY)
Analisa a evolução histórica e estabilização de demandas na instituição (2019-2025):
- **KPIs Históricos:** Crescimento total 2019 vs 2025 (+242%), indicação do pico histórico de ordens no ano de 2023, taxa de queda/estabilização no período 2023→2025 e a dominância da Divisão Predial nos chamados ativos.
- **Gráfico Dinâmico YoY:** Gráfico de linhas reativo que suporta 5 modos alternáveis de visualização por abas:
  1. Requisições por divisão.
  2. Horas por divisão.
  3. Horas consumidas pelas oficinas principais.
  4. Requisições geradas pelas oficinas principais.
  5. Taxa de crescimento YoY % (comparativo de deltas anuais).
- **Tabelas Históricas:** Detalhamento tabular de requisições por divisão por ano, esforço de horas nas 5 maiores oficinas por ano e requisições nas top 5 oficinas por ano.

### 4.6. Eficiência Operacional (Gargalos)
Módulo analítico estratégico focado na identificação visual de gargalos operacionais e burocráticos (administrativos) das oficinas de manutenção:
- **Navegação:** Ícone dedicado `🎯` (Eficiência) na sidebar.
- **Filtros Locais:** Barra dedicada de filtros de refinamento por **Ano** (2019-2026) e **Divisão** (Predial, Serviços, Equipamentos, etc.), com botão de reinicialização rápida (reset).
- **Métricas do Painel (4 Cards de KPI):**
  1. **Oficina Mais Eficiente:** Identifica a oficina com o menor tempo de atendimento (SLA) e esforço equilibrado.
  2. **Gargalo Administrativo Crítico:** Aponta a oficina que se encontra no pior cenário do quadrante de gargalo administrativo (alto SLA e baixo esforço técnico).
  3. **Média de SLA Global:** Exibe o tempo mediano geral de resolução (em dias) para o contexto filtrado.
  4. **Média de Horas Técnicas:** Indica a média de esforço técnico (em horas por requisição) do contexto ativo.
- **Matriz de Dispersão (Scatter Plot):**
  - Gráfico cartesiano de dispersão gerado via Chart.js, cruzando duas métricas fundamentais por oficina:
    - **Eixo X (Tempo Administrativo):** Mediana de SLA (em dias).
    - **Eixo Y (Esforço Técnico):** Média de horas trabalhadas por chamado.
  - Cores dos pontos mapeadas com base no padrão visual consolidado para as oficinas.
  - **Divisão em 4 Quadrantes Analíticos:** Implementada através de um plugin customizado nativo do Chart.js (`quadrantLines`), que desenha linhas tracejadas dinâmicas baseadas na média/mediana global das oficinas ativas, dividindo o gráfico em:
    - **Quadrante 1 (Alto SLA, Baixo Esforço):** *Gargalo Administrativo / Burocrático*. Caracteriza chamados que passam longos períodos parados em trâmites administrativos, filas de espera ou aguardando materiais, apesar de demandarem pouco tempo de execução técnica real.
    - **Quadrante 2 (Alto SLA, Alto Esforço):** *Gargalo Operacional / Alta Complexidade*. Oficinas que demandam muito tempo de execução física e enfrentam atrasos severos de entrega.
    - **Quadrante 3 (Baixo SLA, Alto Esforço):** *Alta Produtividade*. Serviços complexos resolvidos com agilidade pela equipe técnica.
    - **Quadrante 4 (Baixo SLA, Baixo Esforço):** *Eficiência Operacional*. Fluxo ideal onde os chamados possuem rápida tramitação e baixa complexidade técnica.
  - **Suporte ao Dark Mode:** O gráfico e seu plugin customizado adaptam-se dinamicamente às trocas de tema, atualizando as cores das linhas de grade, eixos, rótulos e linhas de divisão dos quadrantes para manter o alto contraste.
- **Painel de Diagnóstico Inteligente:**
  - **Alertas Reativos:** Gera avisos detalhados e contextualizados em tempo real com base no quadrante em que cada oficina se encontra.
  - **Causas Raiz:** Identifica gargalos administrativos causados por atrasos de fluxo de aprovação ou compras de material (com base no alto SLA e baixas horas físicas).
  - **Sugestões de Insumos (Estoque Crítico):** Recomenda materiais específicos para o estoque das oficinas em gargalo burocrático (ex: *Cabos e Disjuntores* para Elétrica; *Tubos e Conexões* para Hidráulica; *Gás Refrigerante e Compressores* para Refrigeração; *Fechaduras e Cilindros* para Chaveiro) para reduzir o tempo de espera por compras descentralizadas.
- **Reatividade e Persistência:**
  - **Dados Estáticos:** Pré-mapeados no objeto global `D.eficiencia_oficinas` para garantir portabilidade completa e histórica (2019-2026).
  - **Dados Dinâmicos (CSV):** O CSV Parser agrupa as linhas processadas em tempo real por ano e oficina, recalculando automaticamente as medianas de SLA e médias de esforço técnico, salvando-as no `localStorage` de forma integrada.

---

## 5. Gestão de Dados (Data Engine)

### 5.1. Estrutura de Dados Estática
Os dados são armazenados no objeto JavaScript global `const D` no `index.html`. Isso garante portabilidade total, permitindo o funcionamento 100% offline da aplicação (relatório autocontido).

### 5.2. Sistema de Importação (CSV Parser)
O dashboard inclui um motor de leitura e reprocessamento de CSV embarcado no navegador:
- **Parser Robusto:** Suporta quebras de linha reais no meio de descrições e comentários longos (células delimitadas por aspas), reconstruindo o arquivo sem quebrar a integridade das linhas.
- **Delimitador Inteligente:** Identifica automaticamente se o arquivo utiliza ponto e vírgula (`;`) ou vírgula (`,`) como separador de colunas através de análise de frequência na primeira linha.
- **Colunas Obrigatórias:**
  `Requisição`, `Status`, `Divisão`, `Oficina`, `Profissional`, `Vínculo`, `Quantidade de Horas`, `Data De Abertura`, `Data de Finalização`, `Unidade Requisitante`.
- **Filtro Estrito de Status:** Apenas linhas que contenham um dos 8 status válidos abaixo são processadas para evitar erros de leitura e desalinhamento de linhas:
  - `FINALIZADA`
  - `ENVIADA`
  - `AGUARDANDO VISITA`
  - `EM ROTA VISITA` (mapeado para a exibição de "EM ROTA DE VISITA")
  - `AGUARDANDO PEDIDO MATERIAL` (mapeado para "AGUARDANDO PEDIDO DE MATERIAL")
  - `PEDIDO MATERIAL REALIZADO` (mapeado para "PEDIDO DE MATERIAL REALIZADO")
  - `SERVIÇO AVALIADO` (mapeado para "SERVIÇO AVALIADO")
  - `AGUARDANDO AVALIAÇÃO REQUISITANTE` (mapeado para "AGUARDANDO REQUISIÇÃO REQUISITANTE")
- **Motor de Datas:** O parser traduz as strings de data nos formatos brasileiros (`DD/MM/AAAA`) ou ISO (`AAAA-MM-DD`) para objetos `Date` nativos, permitindo recalcular com precisão o tempo de atendimento das ordens de serviço.
- **Stable Office (Oficina Estável dos Profissionais):** Lógica que mapeia e fixa a oficina principal de cada técnico baseado no volume dominante de ordens realizadas (ex: garante que Daniel da Costa Braz e Pedro Fernandes pertençam sempre à "Elétrica", mesmo que façam serviços esporádicos para outras áreas), evitando distorções em históricos anuais.
- **Persistência Local (LocalStorage):** Os dados lidos do CSV são automaticamente salvos como string JSON em `'dashboard-csv-data'`, junto com o horário da gravação em `'dashboard-csv-timestamp'`. Durante a inicialização, a função `loadCsvData()` recupera os dados salvos, garantindo a permanência dos relatórios mesmo após o fechamento do navegador. O usuário pode clicar em "Restaurar dados de exemplo" no painel de configurações para retornar aos dados estáticos originais.

---

## 6. Sistema de Filtros e Qualidade de Dados
- **Abordagem Reativa Local:** Filtros globais centralizados foram substituídos por controladores locais específicos em cada aba. Isso confere maior precisão e flexibilidade nas análises contextuais.
- **Higienização de Oficinas (`isValidOficina`):** Para remover dados incorretos e ruídos típicos da base de dados histórica, o motor de qualidade de dados só aceita registros de oficinas presentes na lista oficial de **23 oficinas válidas**:
  > *Alvenaria, Chaveiro, Controle De Acesso, Elétrica, Eletrônica, Elevador, Extintor, Gerador, Hidráulica, Impressão 3d, Impressoras, Informática, Marcenaria, Mecânica, Óptica, Parecer, Pequenas Reformas, Pintura/Gesso, Reciclagem, Refrigeração, Serralheria, Telecomunicações, Vidraçaria.*
  > 
  > Códigos de blocos (ex: `BTO6`), tags residuais entre parênteses (ex: `(Oca)`) ou descrições incorretas na coluna de oficinas do CSV são automaticamente rejeitados ou filtrados pelo método.

---

## 7. Roadmap Sugerido
1. **Integração de Backend:** Substituir o `localStorage` por uma base de dados ativa (como o Supabase), possibilitando que múltiplos gestores alimentem a ferramenta de forma colaborativa em tempo real.
2. **Autenticação de Acesso:** Implementar níveis de permissões de visualização e edição baseados nos cargos dos gestores de manutenção da UFG.
3. **Mecanismo de Relatórios:** Desenvolvimento de uma biblioteca (como `jsPDF`) acoplada para permitir a exportação dos gráficos e tabelas filtradas em formato PDF formatado para impressão.
