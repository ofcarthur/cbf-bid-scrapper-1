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
    # 1. LÓGICA DE RETOMADA (CHECKPOINT)
    if os.path.exists(OUTPUT_CSV):
        log(f"🔄 Checkpoint encontrado! Retomando de: {OUTPUT_CSV}")
        df = pd.read_csv(OUTPUT_CSV)
    elif os.path.exists(INPUT_CSV):
        log(f"📂 Iniciando do zero. Carregando arquivo original: {INPUT_CSV}")
        df = pd.read_csv(INPUT_CSV)
    else:
        log(f"❌ Nenhum arquivo encontrado (nem {INPUT_CSV}, nem {OUTPUT_CSV})")
        return
    
    total_linhas = len(df)
    
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

    # Estatísticas iniciais
    ja_processados = df[df['scrapper_status'].isin(['sucesso', 'erro', 'ignorado'])].shape[0]
    sucessos_anteriores = df[df['scrapper_status'] == 'sucesso'].shape[0]
    
    log(f"📊 Total de linhas no arquivo: {total_linhas}")
    log(f"✅ Já finalizados (Sucesso/Erro/Ignorado): {ja_processados}")
    log(f"🏆 Sucessos até agora: {sucessos_anteriores}")
    log(f"⏳ Restantes para processar: {total_linhas - ja_processados}")
    
    # 4. Loop de Processamento
    processados_sessao = 0
    sucessos_sessao = 0
    ignorados_sessao = 0
    erros_sessao = 0
    
    print("="*60)
    print("🚀 INICIANDO PROCESSAMENTO EM MASSA")
    print("="*60)

    # Iterar sobre o dataframe
    for index, row in df.iterrows():
        # Validar ID básico
        raw_id = row[COLUNA_ID]
        if pd.isna(raw_id) or str(raw_id).strip() == '' or str(raw_id).lower() == 'nan':
            continue

        # Formatar ID corretamente
        id_atleta = str(raw_id).replace('.0', '').strip()
        
        # --- VERIFICAÇÃO DE CHECKPOINT CORRIGIDA ---
        # Se o status NÃO for nulo, significa que já processamos (seja sucesso, erro ou ignorado)
        status_atual = str(row.get('scrapper_status', ''))
        
        # Pula se já foi processado (Sucesso, Erro ou Ignorado)
        if status_atual in ['sucesso', 'erro', 'ignorado']:
            continue
        # -------------------------------------------

        # --- REGRA DE NEGÓCIO: IGNORAR ID COMEÇANDO COM 5 ---
        if id_atleta.startswith('5'):
            df.at[index, 'scrapper_status'] = 'ignorado'
            df.at[index, 'scrapper_msg'] = 'ID começa com 5'
            ignorados_sessao += 1
            # Não fazemos log aqui para não poluir o terminal, apenas conta
            continue
        # ----------------------------------------------------

        log(f"🔄 Processando atleta ID: {id_atleta} (Linha {index})")
        
        try:
            # Chama o scrapper (15 tentativas para garantir)
            dados = buscar_historico_atleta(id_atleta, auto_solve=True, max_retries=15)
            
            # Sucesso
            df.at[index, 'scrapper_status'] = 'sucesso'
            df.at[index, 'scrapper_data'] = json.dumps(dados, ensure_ascii=False)
            df.at[index, 'scrapper_msg'] = "OK"
            
            sucessos_sessao += 1
            log(f"✅ Sucesso para {id_atleta}")
            
        except Exception as e:
            # Erro
            error_msg = str(e)
            df.at[index, 'scrapper_status'] = 'erro'
            df.at[index, 'scrapper_msg'] = error_msg
            erros_sessao += 1
            log(f"❌ Erro para {id_atleta}: {error_msg}")
        
        processados_sessao += 1
        
        # 5. Checkpoint (Salvar periodicamente)
        # Salvamos também se tiver muitos ignorados acumulados para não perder essa marcação
        if (processados_sessao + ignorados_sessao) % SAVE_INTERVAL == 0:
            log(f"💾 Salvando checkpoint em {OUTPUT_CSV}...")
            df.to_csv(OUTPUT_CSV, index=False)
        
        # Delay aleatório se processou algo (não aplicar delay em ignorados)
        sleep_time = random.uniform(2, 5)
        time.sleep(sleep_time)

    # 6. Salvamento Final
    log("💾 Salvando arquivo final...")
    df.to_csv(OUTPUT_CSV, index=False)
    
    print("="*60)
    print(f"🏁 CONCLUÍDO!")
    print(f"Processados nesta sessão: {processados_sessao}")
    print(f"Sucessos nesta sessão: {sucessos_sessao}")
    print(f"Erros nesta sessão: {erros_sessao}")
    print(f"Ignorados (ID começa com 5): {ignorados_sessao}")
    print(f"Arquivo salvo: {OUTPUT_CSV}")
    print("="*60)

if __name__ == "__main__":
    run_production_scraping()