import pandas as pd
import sys
import os
import time
import random
import json
from datetime import datetime

# Adicionar o diretório atual ao path para importar o scrapper
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Tentar importar o scrapper
try:
    from scrapper.scrapper import buscar_historico_atleta
except ImportError:
    print("❌ Erro: Não foi possível importar 'scrapper.scrapper'.")
    print("Verifique se você está executando o script da raiz do projeto.")
    sys.exit(1)

# --- CONFIGURAÇÕES ---
INPUT_CSV = "s_cadastro_jogadores_rows.csv"
OUTPUT_CSV = "jogadores_historico_completo.csv"
COLUNA_ID = "registro_canonico_bid"
SAVE_INTERVAL = 10  # Salvar o CSV a cada X atletas processados

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")

def run_production_scraping():
    # 1. LÓGICA DE CARREGAMENTO
    if os.path.exists(OUTPUT_CSV):
        log(f"🔄 Carregando arquivo de checkpoint: {OUTPUT_CSV}")
        df = pd.read_csv(OUTPUT_CSV)
    elif os.path.exists(INPUT_CSV):
        log(f"📂 Iniciando do zero. Carregando arquivo original: {INPUT_CSV}")
        df = pd.read_csv(INPUT_CSV)
    else:
        log(f"❌ Nenhum arquivo encontrado (nem {INPUT_CSV}, nem {OUTPUT_CSV})")
        return
    
    # 2. Validação inicial da coluna
    if COLUNA_ID not in df.columns:
        log(f"❌ Coluna '{COLUNA_ID}' não encontrada no CSV.")
        return
    
    # 3. Preparar colunas de saída se não existirem
    if 'scrapper_status' not in df.columns:
        df['scrapper_status'] = None 
    if 'scrapper_data' not in df.columns:
        df['scrapper_data'] = None   
    if 'scrapper_msg' not in df.columns:
        df['scrapper_msg'] = None    

    print("="*80)
    print("🔍 ANALISANDO RANGE DE REGISTROS")
    print("="*80)
    
    # 4. ANÁLISE DO RANGE - Identificar registros válidos
    registros_validos = []
    
    for index, row in df.iterrows():
        raw_id = row[COLUNA_ID]
        if pd.isna(raw_id) or str(raw_id).strip() == '' or str(raw_id).lower() == 'nan':
            continue
            
        # Formatar ID corretamente
        id_atleta = str(raw_id).replace('.0', '').strip()
        
        # Ignorar IDs começando com 5
        if id_atleta.startswith('5'):
            continue
            
        # Verificar se é número válido
        try:
            id_numero = int(id_atleta)
            registros_validos.append(id_numero)
        except ValueError:
            continue
    
    if not registros_validos:
        log("❌ Nenhum registro válido encontrado!")
        return
    
    # 5. DETERMINAR RANGE - ABORDAGEM INTELIGENTE
    primeiro_registro = min(registros_validos)
    ultimo_registro = max(registros_validos)
    
    log(f"📊 PRIMEIRO REGISTRO ENCONTRADO: {primeiro_registro}")
    log(f"📊 ÚLTIMO REGISTRO ENCONTRADO: {ultimo_registro}")
    
    # Análise de distribuição para definir ranges inteligentes
    distribuicao = {
        'baixos (1-1000)': len([r for r in registros_validos if 1 <= r <= 1000]),
        'medios (500000-600000)': len([r for r in registros_validos if 500000 <= r <= 600000]),
        'altos (600001-1000000)': len([r for r in registros_validos if 600001 <= r <= 1000000])
    }
    
    log("📊 DISTRIBUIÇÃO DOS REGISTROS:")
    for faixa, count in distribuicao.items():
        log(f"   {faixa}: {count:,} registros")
    
    # Definir range inteligente - focar onde há mais concentração
    # Se há muitos registros acima de 500k, vamos focar nessa faixa
    registros_altos = [r for r in registros_validos if r >= 500000]
    
    if len(registros_altos) > len(registros_validos) * 0.8:  # Se 80%+ dos registros são altos
        range_inicio = 526964
        range_fim = ultimo_registro
        log(f"🎯 RANGE OTIMIZADO: {range_inicio:,} até {range_fim:,} (foco em registros altos)")
    else:
        range_inicio = primeiro_registro
        range_fim = ultimo_registro
        log(f"🎯 RANGE COMPLETO: {range_inicio:,} até {range_fim:,}")
    
    # 6. CONTAR REGISTROS NO RANGE OTIMIZADO
    total_range = range_fim - range_inicio + 1
    log(f"📊 TOTAL DE REGISTROS NO RANGE: {total_range:,}")
    
    # 7. IDENTIFICAR REGISTROS EXISTENTES NA FAIXA OTIMIZADA
    registros_existentes_na_faixa = set([r for r in registros_validos if range_inicio <= r <= range_fim])
    log(f"📊 REGISTROS JÁ EXISTENTES NO RANGE: {len(registros_existentes_na_faixa):,}")
    
    # 8. IDENTIFICAR REGISTROS FALTANTES NO RANGE OTIMIZADO
    registros_faltantes = []
    for registro in range(range_inicio, range_fim + 1):
        if registro not in registros_existentes_na_faixa:
            registros_faltantes.append(registro)
    
    log(f"📊 REGISTROS FALTANTES NO RANGE: {len(registros_faltantes):,}")
    
    # 9. ESTATÍSTICAS DETALHADAS
    if 'scrapper_status' in df.columns:
        sucessos_anteriores = len(df[df['scrapper_status'] == 'sucesso'])
        erros_anteriores = len(df[df['scrapper_status'] == 'erro'])
        log(f"✅ SUCESSOS ANTERIORES: {sucessos_anteriores:,}")
        log(f"❌ ERROS ANTERIORES: {erros_anteriores:,}")
    
    print("="*80)
    print("🚀 INICIANDO PROCESSAMENTO DOS REGISTROS FALTANTES")
    print("="*80)
    
    # 10. PROCESSAR REGISTROS FALTANTES
    processados_sessao = 0
    sucessos_sessao = 0
    
    for i, registro in enumerate(registros_faltantes):
        log(f"🔄 Processando registro {registro} ({i+1}/{len(registros_faltantes)})")
        
        try:
            # Chama o scrapper
            dados = buscar_historico_atleta(str(registro), auto_solve=True, max_retries=15)
            
            # Criar nova linha no DataFrame
            nova_linha = {
                COLUNA_ID: registro,
                'scrapper_status': 'sucesso',
                'scrapper_data': json.dumps(dados, ensure_ascii=False),
                'scrapper_msg': 'OK'
            }
            
            # Adicionar outras colunas como vazias se existirem
            for col in df.columns:
                if col not in nova_linha:
                    nova_linha[col] = None
            
            # Adicionar linha ao DataFrame
            new_df = pd.DataFrame([nova_linha])
            df = pd.concat([df, new_df], ignore_index=True)
            
            sucessos_sessao += 1
            log(f"✅ Sucesso para registro {registro}")
            
        except Exception as e:
            # Erro - adicionar linha com erro
            error_msg = str(e)
            nova_linha = {
                COLUNA_ID: registro,
                'scrapper_status': 'erro',
                'scrapper_data': None,
                'scrapper_msg': error_msg
            }
            
            # Adicionar outras colunas como vazias se existirem
            for col in df.columns:
                if col not in nova_linha:
                    nova_linha[col] = None
            
            # Adicionar linha ao DataFrame
            new_df = pd.DataFrame([nova_linha])
            df = pd.concat([df, new_df], ignore_index=True)
            
            log(f"❌ Erro para registro {registro}: {error_msg}")
        
        processados_sessao += 1
        
        # 11. Checkpoint (Salvar periodicamente)
        if processados_sessao % SAVE_INTERVAL == 0:
            log(f"💾 Salvando checkpoint em {OUTPUT_CSV}...")
            df.to_csv(OUTPUT_CSV, index=False)
        
        # Delay aleatório
        sleep_time = random.uniform(2, 5)
        time.sleep(sleep_time)

    # 12. Salvamento Final
    log("💾 Salvando arquivo final...")
    df.to_csv(OUTPUT_CSV, index=False)
    
    print("="*80)
    print(f"🏁 PROCESSAMENTO CONCLUÍDO!")
    print(f"Registros faltantes processados: {processados_sessao}")
    print(f"Sucessos nesta sessão: {sucessos_sessao}")
    print(f"Arquivo salvo: {OUTPUT_CSV}")
    print("="*80)

if __name__ == "__main__":
    run_production_scraping()