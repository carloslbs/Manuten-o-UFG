import os
import sys
import csv
import json
import datetime
import urllib.request
import urllib.error

# Garantir codificação UTF-8 no console Windows
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# ====================================================================
# SCRIPT ETL DE MIGRAÇÃO: CSV PARA SUPABASE (POSTGRESQL)
# PROJETO: GESTÃO DE MANUTENÇÃO SEINFRA / UFG
# ====================================================================

# 1. CARREGADOR TEXTUAL DE ARQUIVO .ENV (LIVRE DE DEPENDÊNCIAS EXTERNAS)
def load_dotenv():
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")

# 2. FUNÇÃO DE HIGIENIZAÇÃO E PARSING DE DATAS (FORMATO BRASILEIRO E ISO)
def parse_date(date_str):
    if not date_str or date_str.strip() == '':
        return None
    
    # Limpa espaçamento excessivo
    clean_str = date_str.replace(',', ' ').replace('  ', ' ').strip()
    
    # Formatos de data suportados pelo histórico
    formats = [
        '%d/%m/%Y %H:%M:%S',
        '%d/%m/%Y %H:%M',
        '%d/%m/%Y',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d'
    ]
    
    for fmt in formats:
        try:
            dt = datetime.datetime.strptime(clean_str, fmt)
            # Formata para string compatível com timestamptz do Postgres (GMT-3 Brasília)
            return dt.strftime('%Y-%m-%d %H:%M:%S-03')
        except ValueError:
            continue
            
    # Fallback caso a hora venha corrompida: tenta isolar apenas a data
    try:
        parts = clean_str.split(' ')
        if len(parts) > 1:
            for fmt in ['%d/%m/%Y', '%Y-%m-%d']:
                try:
                    dt = datetime.datetime.strptime(parts[0], fmt)
                    return dt.strftime('%Y-%m-%d 00:00:00-03')
                except ValueError:
                    continue
    except Exception:
        pass
        
    return None

# 3. FUNÇÃO DE PARSING DE HORAS (TRATAMENTO DE DECIMAIS BRASILEIROS)
def parse_hours(hours_str):
    if not hours_str or hours_str.strip() == '':
        return 0.0
    try:
        clean = hours_str.replace('"', '').replace("'", '').replace(',', '.').strip()
        return float(clean)
    except Exception:
        return 0.0

# 4. TRATAMENTO DE TEXTOS E STRINGS VAZIAS para NULL no banco
def clean_text(text, fallback=None):
    if not text:
        return fallback
    clean = text.strip()
    return clean if clean != '' else fallback

# 5. REPRODUÇÃO DE CANONICALIZAÇÃO DE OFICINAS DO FRONTER
OFFICIAL_OFFICES = {
    "alvenaria", "chaveiro", "controle de acesso", "elétrica", "eletrônica", "elevador", 
    "extintor", "gerador", "hidráulica", "impressão 3d", "impressoras", "informática", 
    "marcenaria", "mecânica", "óptica", "parecer", "pequenas reformas", "pintura/gesso", 
    "reciclagem", "refrigeração", "serralheria", "telecomunicações", "vidraçaria"
}

def get_canonical_oficina(ofic_str):
    if not ofic_str:
        return "Outro"
    
    # Sanitização e remoção de parênteses/ruídos comuns
    clean = ofic_str.strip().replace('"', '').replace("'", "")
    clean_lower = clean.lower()
    
    # Checar exato
    if clean_lower in OFFICIAL_OFFICES:
        # Encontra o nome capitalizado correto
        for official in OFFICIAL_OFFICES:
            if official == clean_lower:
                # Retorna com a grafia correta
                words = official.split(' ')
                return ' '.join(w.capitalize() if w not in ['de', 'do', 'da'] else w for w in words)
    
    # Tratamentos especiais de abreviações e erros comuns
    if "eletri" in clean_lower:
        return "Elétrica"
    if "refrig" in clean_lower:
        return "Refrigeração"
    if "hidrau" in clean_lower or "encanador" in clean_lower:
        return "Hidráulica"
    if "pintur" in clean_lower or "gesso" in clean_lower:
        return "Pintura/Gesso"
    if "marcen" in clean_lower or "carpint" in clean_lower:
        return "Marcenaria"
    if "serralh" in clean_lower:
        return "Serralheria"
    if "telecom" in clean_lower:
        return "Telecomunicações"
    if "chave" in clean_lower:
        return "Chaveiro"
    if "alven" in clean_lower or "pedreir" in clean_lower:
        return "Alvenaria"
    
    return "Outro"

# ====================================================================
# EXECUÇÃO PRINCIPAL DO PIPELINE ETL
# ====================================================================
def main():
    print("🚀 Iniciando Pipeline ETL de Migração de Dados SEINFRA...")
    load_dotenv()
    
    supabase_url = os.environ.get("SUPABASE_URL")
    service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    # Validação de credenciais obrigatórias
    if not supabase_url or not service_role_key:
        print("\n❌ ERRO: Credenciais do Supabase não configuradas no arquivo .env!")
        print("Por favor, crie um arquivo chamado '.env' no diretório raiz do projeto com o seguinte conteúdo:")
        print("----------------------------------------------------------------")
        print("SUPABASE_URL=https://seu-projeto.supabase.co")
        print("SUPABASE_SERVICE_ROLE_KEY=sua-chave-service-role-privada-super-secreta")
        print("----------------------------------------------------------------")
        print("⚠️ Nota: Use a 'service_role key' (nunca a 'anon key') para o script de migração ter permissão de escrita.")
        sys.exit(1)
        
    # Identificar caminho do CSV
    csv_filename = "Manutenção_19_05_2026.csv"
    if len(sys.argv) > 1:
        csv_filename = sys.argv[1]
        
    if not os.path.exists(csv_filename):
        # Tenta buscar arquivos alternativos na pasta
        alt_csv = "relatorio_de_horas_de_requisicoes_de_manutencao___seinfra_2026-05-04T08_56_53.503371475-03_00_maio_1.csv"
        if os.path.exists(alt_csv):
            print(f"⚠️ CSV padrão não encontrado. Utilizando arquivo alternativo detectado: '{alt_csv}'")
            csv_filename = alt_csv
        else:
            print(f"\n❌ ERRO: Arquivo CSV '{csv_filename}' não encontrado!")
            print("Coloque o arquivo CSV no diretório do projeto ou passe o caminho como argumento:")
            print("Exemplo: python migrate_csv.py /caminho/do/seu/arquivo.csv")
            sys.exit(1)
            
    print(f"📂 Arquivo CSV selecionado: '{csv_filename}' ({os.path.getsize(csv_filename) / (1024*1024):.2f} MB)")
    
    # 1. DETECTAR ENCODING (UTF-8 vs ISO-8859-1/Latin1)
    encoding = 'utf-8'
    try:
        with open(csv_filename, 'r', encoding='utf-8') as f:
            f.readline() # tenta ler a primeira linha
    except UnicodeDecodeError:
        encoding = 'latin1'
        print("ℹ️ Codificação UTF-8 falhou. Utilizando codificação ISO-8859-1 (Latin1) para ler acentuações brasileiras.")
        
    # 2. ANÁLISE INICIAL E DELIMITADOR
    delim = ';'
    with open(csv_filename, 'r', encoding=encoding) as f:
        first_line = f.readline()
        semic_count = first_line.count(';')
        comma_count = first_line.count(',')
        delim = ';' if semic_count > comma_count else ','
        print(f"ℹ️ Delimitador dominante detectado: '{delim}'")
        
    # 3. LEITURA E PARSING DOS REGISTROS
    rows_to_insert = []
    allowed_statuses = {"FINALIZADA", "ENVIADA", "AGUARDANDO VISITA", "EM ROTA VISITA", "AGUARDANDO PEDIDO MATERIAL", "PEDIDO MATERIAL REALIZADO", "SERVIÇO AVALIADO", "AGUARDANDO AVALIAÇÃO REQUISITANTE"}
    
    print("⏳ Lendo e higienizando registros do CSV... Por favor, aguarde.")
    
    with open(csv_filename, 'r', encoding=encoding) as f:
        reader = csv.reader(f, delimiter=delim)
        try:
            headers = next(reader)
        except StopIteration:
            print("❌ ERRO: O arquivo CSV está completamente vazio.")
            sys.exit(1)
            
        # Mapear posições de colunas (case-insensitive)
        headers_lower = [h.lower().strip() for h in headers]
        
        required_cols = {
            'requisicao': 'requisição',
            'divisao': 'divisão',
            'codigo_unidade': 'código unidade requisitante',
            'unidade': 'unidade requisitante',
            'local': 'local',
            'oficina': 'oficina',
            'servico': 'serviço',
            'status': 'status',
            'abertura': 'data de abertura',
            'finalizacao': 'data de finalização',
            'vinculo': 'vínculo',
            'profissional': 'profissional',
            'horas': 'quantidade de horas',
            'descricao': 'descricao',
            'observacoes': 'observacoes'
        }
        
        idx = {}
        for key, expected in required_cols.items():
            if expected in headers_lower:
                idx[key] = headers_lower.index(expected)
            else:
                # Tenta match parcial inteligente
                matched = False
                for i, h in enumerate(headers_lower):
                    if key == 'descricao' and h in ['descrição', 'descricao']:
                        idx[key] = i
                        matched = True
                        break
                    elif key == 'observacoes' and h in ['observações', 'observacoes']:
                        idx[key] = i
                        matched = True
                        break
                    elif key == 'finalizacao' and 'finalização' in h:
                        idx[key] = i
                        matched = True
                        break
                if not matched:
                    # Mapeia como opcional ou exibe aviso
                    idx[key] = -1
                    if key in ['requisicao', 'divisao', 'oficina', 'status', 'abertura']:
                        print(f"❌ ERRO: Coluna mandatória '{expected}' não foi encontrada no CSV!")
                        sys.exit(1)
                        
        line_count = 0
        skipped_status_count = 0
        
        for row in reader:
            if not row or len(row) < 3:
                continue
                
            line_count += 1
            
            # Validação do Status
            status_val = row[idx['status']].strip() if idx['status'] < len(row) else ''
            if status_val not in allowed_statuses:
                skipped_status_count += 1
                continue
                
            # Mapeamento e higienização exata dos campos
            # Fallback para "Outro" ou nulo caso campos obrigatórios estejam vazios
            divisao = clean_text(row[idx['divisao']], "Outro") if idx['divisao'] < len(row) else "Outro"
            oficina = get_canonical_oficina(row[idx['oficina']]) if idx['oficina'] < len(row) else "Outro"
            
            # Limpeza de datas
            dt_abertura = parse_date(row[idx['abertura']]) if idx['abertura'] < len(row) else None
            dt_finalizacao = parse_date(row[idx['finalizacao']]) if idx['finalizacao'] < len(row) else None
            
            # Ignora registros sem data de abertura válida (inconsistência grave)
            if not dt_abertura:
                continue
                
            # Mapeia cargo se estiver acoplado no nome do profissional ou nulo
            prof_nome = clean_text(row[idx['profissional']]) if idx['profissional'] < len(row) else None
            
            chamado = {
                "requisicao": clean_text(row[idx['requisicao']]) if idx['requisicao'] < len(row) else None,
                "divisao": divisao,
                "codigo_unidade_requisitante": clean_text(row[idx['codigo_unidade']]) if idx['codigo_unidade'] < len(row) else None,
                "unidade_requisitante": clean_text(row[idx['unidade']]) if idx['unidade'] < len(row) else None,
                "local": clean_text(row[idx['local']]) if idx['local'] < len(row) else None,
                "oficina": oficina,
                "servico": clean_text(row[idx['servico']]) if idx['servico'] < len(row) else None,
                "status": status_val,
                "data_abertura": dt_abertura,
                "data_finalizacao": dt_finalizacao,
                "vinculo": clean_text(row[idx['vinculo']]) if idx['vinculo'] < len(row) else None,
                "profissional": prof_nome,
                "quantidade_horas": parse_hours(row[idx['horas']]) if idx['horas'] < len(row) else 0.0,
                "descricao": clean_text(row[idx['descricao']]) if idx['descricao'] < len(row) else None,
                "observacoes": clean_text(row[idx['observacoes']]) if idx['observacoes'] < len(row) else None
            }
            
            rows_to_insert.append(chamado)
            
    total_valid = len(rows_to_insert)
    print(f"✅ Leitura concluída. Total de linhas processadas: {line_count}")
    print(f"ℹ️ Linhas descartadas por status inválido: {skipped_status_count}")
    print(f"📈 Total de registros prontos para migração: {total_valid}")
    
    # 4. ENVIO DOS REGISTROS EM CHUNKS (LOTEAMENTO DE SEGURANÇA E PERFORMANCE)
    CHUNK_SIZE = 2000
    total_chunks = (total_valid + CHUNK_SIZE - 1) // CHUNK_SIZE
    
    endpoint_url = f"{supabase_url.rstrip('/')}/rest/v1/chamados"
    
    print(f"\n⚡ Iniciando upload em massa para o Supabase ({total_chunks} lotes de {CHUNK_SIZE} registros)...")
    
    # Loop de upload por lotes
    for i in range(total_chunks):
        start_idx = i * CHUNK_SIZE
        end_idx = min(start_idx + CHUNK_SIZE, total_valid)
        chunk = rows_to_insert[start_idx:end_idx]
        
        # Prepara requisição POST HTTP REST
        data_json = json.dumps(chunk).encode('utf-8')
        
        req = urllib.request.Request(
            endpoint_url,
            data=data_json,
            headers={
                "apikey": service_role_key,
                "Authorization": f"Bearer {service_role_key}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal" # Economia radical de tráfego e latência
            },
            method="POST"
        )
        
        # Envia lote
        retry = 3
        while retry > 0:
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    # Sucesso (normalmente 201 Created)
                    percent = (end_idx / total_valid) * 100
                    print(f" Lote {i+1}/{total_chunks} enviado com sucesso! {end_idx}/{total_valid} registros ({percent:.1f}%)")
                    break
            except urllib.error.HTTPError as e:
                err_msg = e.read().decode('utf-8')
                print(f"⚠️ Erro no lote {i+1} (Tentativa {4-retry}/3): Código {e.code} - {e.reason}")
                print(f" Detalhe: {err_msg[:300]}")
                retry -= 1
                if retry == 0:
                    print("❌ ERRO GRAVE: Falhas repetidas ao enviar o lote. Interrompendo migração.")
                    sys.exit(1)
            except Exception as e:
                print(f"⚠️ Erro de conexão no lote {i+1} (Tentativa {4-retry}/3): {str(e)}")
                retry -= 1
                if retry == 0:
                    print("❌ ERRO GRAVE: Falhas de rede repetidas. Interrompendo migração.")
                    sys.exit(1)
                    
    print("\n🎉 Todos os registros foram migrados com sucesso para a tabela 'chamados' do Supabase!")
    
    # 5. ATUALIZAR VIEWS MATERIALIZADAS DO BANCO DE DADOS (VIA RPC)
    print("⏳ Atualizando e otimizando as views consolidadas no banco de dados...")
    rpc_url = f"{supabase_url.rstrip('/')}/rest/v1/rpc/refresh_materialized_views"
    req_rpc = urllib.request.Request(
        rpc_url,
        data=b'{}', # Corpo vazio exigido pelo PostgREST
        headers={
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req_rpc, timeout=15) as r:
            print("✅ Views consolidadas e materializadas recalculadas com absoluto sucesso!")
    except Exception as e:
        # A RPC pode não existir no banco ainda se o DDL não rodou, reporta apenas aviso
        print(f"⚠️ Aviso: Não foi possível atualizar as views via RPC: {str(e)}")
        print("Certifique-se de executar o arquivo 'schema.sql' no SQL Editor do seu Supabase para as views e relatórios funcionarem.")
        
    print("\n🌟 OPERAÇÃO DE INGESTÃO CONCLUÍDA COM SUCESSO! 🌟")

if __name__ == '__main__':
    main()
