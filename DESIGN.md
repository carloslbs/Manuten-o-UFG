# Guia de Design e Identidade Visual: Manutenção SEINFRA

Este documento define os padrões visuais e componentes de UI para o Dashboard de Manutenção da UFG.

## 1. Conceito Visual
O dashboard utiliza uma estética **Premium Minimalista**, focada na clareza dos dados e no conforto visual para longas sessões de análise. A interface é baseada em "cards" com sombras suaves e bordas levemente arredondadas, seguindo princípios de design moderno de ferramentas de BI (Business Intelligence).

## 2. Paleta de Cores (Design Tokens)

### 2.1. Cores Base (Light Mode)
- **Background:** `#F4F2ED` (Off-white) - Proporciona um contraste suave, menos cansativo que o branco puro.
- **Surface:** `#FAFAF8` - Cor dos cards e áreas de conteúdo.
- **Surface 2:** `#EFEDE7` - Áreas de hover e seções secundárias.
- **Border:** `#E0DDD5` - Linhas de separação e bordas de cards.
- **Text Primary:** `#1A1916` - Texto principal.
- **Text Secondary:** `#6B6860` - Legendas e textos de apoio.

### 2.2. Cores de Destaque e Semânticas
- **Institucional (Accent):** `#1B4F8A` (Azul SEINFRA) - Usado em botões ativos, barras de progresso e ícones principais.
- **Sucesso (Ok):** `#3A6610` (Verde Oliva Profundo).
- **Alerta (Warn):** `#8A4A10` (Âmbar/Bronze).
- **Erro (Danger):** `#8A1F1F` (Vermelho Escuro).

### 2.3. Categorias de Oficina (Cores de Gráfico)
Para facilitar a identificação rápida:
- **Elétrica:** `--c-elec: #1B4F8A`
- **Refrigeração:** `--c-refrig: #4A2D8A`
- **Alvenaria:** `--c-alv: #8A4A10`
- **Pintura:** `--c-pint: #8A1F1F`
- **Hidráulica:** `--c-hid: #1A7A5E`

## 3. Tipografia
O projeto utiliza a família de fontes **DM Sans** via Google Fonts.

- **Interface (Labels, Menus, Textos):** `DM Sans`, Sans-serif.
  - *Weights:* 300 (Light), 400 (Regular), 500 (Medium), 600 (Semi-bold).
- **Dados Numéricos (KPIs, Tabelas, IDs):** `DM Mono`, Monospace.
  - *Uso:* Garante que os números permaneçam alinhados e legíveis em tabelas comparativas.

## 4. Componentes de UI

### 4.1. KPI Cards
- **Radius:** `10px`.
- **Shadow:** `0 1px 3px rgba(0,0,0,.07), 0 4px 12px rgba(0,0,0,.04)`.
- **Destaque:** Borda superior de 3px com a cor semântica correspondente ao status.

### 4.2. Tabelas (`.tbl`)
- **Estilo:** Bordas apenas horizontais (`#E0DDD5`).
- **Hover:** Mudança sutil de fundo para `var(--surface2)`.
- **Alinhamento:** Números sempre alinhados à direita com fonte mono.

### 4.3. Badges e Pills
- **Radius:** `99px` (Pill shape).
- **Opacidade:** Fundo com 15% da cor original e texto com 100%.

## 5. Modo Escuro (Dark Mode)
O sistema utiliza a classe `.dark` no elemento `body`. 

- **Background:** `#141412`.
- **Surface:** `#1C1C1A`.
- **Text Primary:** `#F5F2EC`.
- **Interação:** As cores semânticas (Ok/Warn/Danger) são ajustadas para tons mais vibrantes/pastéis para garantir contraste (WCAG Compliance).

## 6. Iconografia
- **Sistema:** Emojis Unicode.
- **Racional:** Redução de dependências externas e tempo de carregamento zero.
- **Uso:** Apenas como suporte visual na sidebar e títulos de modais.
