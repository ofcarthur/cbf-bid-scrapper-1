import requests
from bs4 import BeautifulSoup
import re
import os
import sys
import time
import random
import base64
from datetime import datetime

# Adicionar diretório raiz para importar captcha_ml
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from captcha_ml.captcha_solver import solve_captcha_auto
    CAPTCHA_SOLVER_AVAILABLE = True
except ImportError:
    CAPTCHA_SOLVER_AVAILABLE = False
    print("⚠️  Solver de captcha ML não disponível. Use captcha_code manual ou treine o modelo primeiro.")

def salvar_dataset_ouro(base64_string, label):
    """
    Salva o captcha resolvido corretamente para re-treinamento futuro (Data Flywheel).
    """
    try:
        # Define o caminho: captcha_ml/data/dataset_ouro
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ouro_dir = os.path.join(root_dir, "captcha_ml", "data", "dataset_ouro")
        os.makedirs(ouro_dir, exist_ok=True)

        # Limpa o base64
        if base64_string.startswith('data:image'):
            base64_string = base64_string.split(',')[1]
        
        # Gera nome único: LABEL_TIMESTAMP.png (Ex: abcd_16999999.png)
        timestamp = int(time.time() * 1000)
        filename = f"{label}_{timestamp}.png"
        filepath = os.path.join(ouro_dir, filename)

        with open(filepath, "wb") as f:
            f.write(base64.b64decode(base64_string))
            
        print(f"⭐ Captcha '{label}' salvo em dataset_ouro/ para o futuro!")
    except Exception as e:
        print(f"⚠️ Erro ao salvar no dataset ouro: {e}")

def buscar_dados_bid(uf, data_publicacao, captcha_code=None, auto_solve=True):
    """
    Busca dados do BID da CBF (Lista geral por Estado/Data)
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://bid.cbf.com.br',
        'Referer': 'https://bid.cbf.com.br/'
    }
    
    session = requests.Session()
    
    print("Acessando página principal...")
    response_home = session.get('https://bid.cbf.com.br/', headers=headers, timeout=10)
    
    if response_home.status_code != 200:
        raise Exception(f'Erro ao acessar página principal: {response_home.status_code}')
    
    soup = BeautifulSoup(response_home.text, 'html.parser')
    csrf_meta = soup.find('meta', {'name': 'csrf-token'})
    if csrf_meta:
        csrf_token = csrf_meta.get('content')
        headers['X-CSRF-TOKEN'] = csrf_token
    
    # Obter o captcha
    captcha_base64_recieved = None 
    
    if captcha_code is None:
        print("\nObtendo captcha...")
        captcha_response = session.get('https://bid.cbf.com.br/get-captcha-base64', headers=headers, timeout=10)
        
        if captcha_response.status_code == 200:
            content_type = captcha_response.headers.get('content-type', '').lower()
            
            if 'json' in content_type:
                captcha_data = captcha_response.json()
                captcha_base64 = captcha_data.get('image', '')
            else:
                captcha_base64 = captcha_response.text.strip()
            
            captcha_base64_recieved = captcha_base64 
            
            if auto_solve and CAPTCHA_SOLVER_AVAILABLE and captcha_base64:
                print("🤖 Tentando resolver captcha automaticamente com ML...")
                captcha_code = solve_captcha_auto(captcha_base64)
                
                if captcha_code:
                    print(f"✓ Captcha resolvido automaticamente: '{captcha_code}'")
                else:
                    print("❌ Falha na resolução automática do captcha")
            
            if captcha_code is None:
                raise Exception('Captcha necessário. Resolução automática falhou.')
        else:
            raise Exception(f'Erro ao obter captcha: {captcha_response.status_code}')
    
    # Preparar os dados para a busca
    dados = {
        'data': data_publicacao,
        'uf': uf,
        'codigo_clube': '',
        'captcha': captcha_code
    }
    
    print(f"\nBuscando dados para UF={uf}, Data={data_publicacao}...")
    response = session.post('https://bid.cbf.com.br/busca-json', 
                           data=dados, 
                           headers=headers, 
                           timeout=10)
    
    if response.status_code != 200:
        raise Exception(f'Erro na requisição: {response.status_code}')
    
    try:
        response_json = response.json()
    except Exception as e:
        raise Exception('Resposta inválida da API')
    
    # Verificar erros
    if isinstance(response_json, dict):
        if response_json.get('status') == False:
            messages = response_json.get('messages', {})
            if isinstance(messages, dict):
                error_msg = '; '.join([f"{k}: {v}" for k, v in messages.items()])
            else:
                error_msg = str(messages)
            raise Exception(f'Erro retornado pela API: {error_msg}')
    
    # Se chegou aqui, deu certo! Salvar dataset ouro
    if captcha_base64_recieved and captcha_code:
        salvar_dataset_ouro(captcha_base64_recieved, captcha_code)

    print(f"\n{len(response_json)} registros encontrados")
    
    registros = []
    for atleta in response_json:
        registros.append({
            'jogador': atleta.get('nome', ''),
            'operacao': atleta.get('tipocontrato', ''),
            'publicacao': atleta.get('data_publicacao', ''),
            'clube': atleta.get('clube', ''),
            'apelido': atleta.get('apelido', ''),
            'codigo_atleta': atleta.get('codigo_atleta', ''),
            'contrato_numero': atleta.get('contrato_numero', ''),
            'data_inicio': atleta.get('datainicio', ''),
            'data_nascimento': atleta.get('data_nascimento', ''),
            'codigo_clube': atleta.get('codigo_clube', ''),
            'uf': atleta.get('uf', '')
        })
    
    return registros


def buscar_historico_atleta(codigo_atleta, captcha_code=None, auto_solve=True, max_retries=15):
    """
    Busca histórico de um atleta específico no BID da CBF.
    Inclui lógica de Dataset Ouro e tratamento inteligente de erro 500.
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Connection': 'keep-alive',
        'Sec-Ch-Ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"macOS"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://bid.cbf.com.br',
        'Referer': f'https://bid.cbf.com.br/atleta-competicoes/{codigo_atleta}',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': headers['User-Agent'],
        'Accept-Language': headers['Accept-Language'],
        'Accept-Encoding': headers['Accept-Encoding'],
        'Sec-Ch-Ua': headers['Sec-Ch-Ua'],
        'Sec-Ch-Ua-Mobile': headers['Sec-Ch-Ua-Mobile'],
        'Sec-Ch-Ua-Platform': headers['Sec-Ch-Ua-Platform']
    })

    print(f"Acessando página do atleta {codigo_atleta}...")
    time.sleep(random.uniform(1, 2))
    response_atleta = session.get(f'https://bid.cbf.com.br/atleta-competicoes/{codigo_atleta}', 
                                  headers=headers, timeout=10)

    if response_atleta.status_code != 200:
        if response_atleta.status_code >= 500:
            raise Exception(f'Erro de Servidor (CBF fora do ar ou atleta sem dados): {response_atleta.status_code}')
        raise Exception(f'Erro ao acessar página do atleta: {response_atleta.status_code}')

    soup = BeautifulSoup(response_atleta.text, 'html.parser')
    csrf_meta = soup.find('meta', {'name': 'csrf-token'})
    if csrf_meta:
        headers['X-CSRF-TOKEN'] = csrf_meta.get('content')
    else:
        print("AVISO: CSRF token não encontrado")

    # Contador de erros 500 consecutivos para este atleta
    consecutive_500_errors = 0

    # Loop de tentativas
    for tentativa in range(max_retries):
        print(f"\n{'='*60}")
        if tentativa == 0:
            print(f"🔍 Tentativa {tentativa + 1}: Buscando dados do atleta...")
        else:
            print(f"🔄 Tentativa {tentativa + 1}/{max_retries}: Tentando novamente...")
        print(f"{'='*60}")
        
        current_captcha = captcha_code
        current_captcha_base64 = None 
        
        if current_captcha is None or tentativa > 0:  
            print("\nObtendo captcha...")
            
            # Delay progressivo se estiver dando erro
            wait_time = random.uniform(1.5, 3.0) + (consecutive_500_errors * 2)
            if tentativa > 0: time.sleep(wait_time)
                
            captcha_response = session.get('https://bid.cbf.com.br/get-captcha-base64', 
                                         headers=headers, timeout=10)
            
            if captcha_response.status_code == 200:
                content_type = captcha_response.headers.get('content-type', '').lower()
                if 'json' in content_type:
                    current_captcha_base64 = captcha_response.json().get('image', '')
                else:
                    current_captcha_base64 = captcha_response.text.strip()

                if auto_solve and CAPTCHA_SOLVER_AVAILABLE and current_captcha_base64:
                    print("🤖 Resolvendo captcha...")
                    current_captcha = solve_captcha_auto(current_captcha_base64)
                    
                    # Filtro de qualidade
                    if not current_captcha or len(current_captcha) != 4:
                        print(f"⚠️ Predição descartada: '{current_captcha}' (tamanho inválido). Solicitando novo...")
                        continue 
                    
                    if current_captcha:
                        print(f"✓ Captcha resolvido: '{current_captcha}'")
                    else:
                        print("❌ Falha na resolução automática")

                if current_captcha is None:
                    print("❌ Não foi possível resolver o captcha.")
                    continue
            else:
                print(f"Erro ao obter captcha (HTTP {captcha_response.status_code})")
                continue

        dados = {
            'codigo_atleta': str(codigo_atleta),
            'captcha': current_captcha
        }

        print(f"\nEnviando requisição (Captcha: {current_captcha})...")
        response = session.post('https://bid.cbf.com.br/atleta-historico-json', 
                               data=dados, headers=headers, timeout=10)

        # TRATAMENTO DE ERROS HTTP
        if response.status_code != 200:
            print(f"Erro na requisição: {response.status_code}")
            
            # Lógica especial para Erro 500 (Internal Server Error)
            if response.status_code >= 500:
                consecutive_500_errors += 1
                print(f"⚠️ Erro interno do servidor CBF ({consecutive_500_errors}x seguidas).")
                
                # Se der erro 500 por 3 vezes seguidas, assumimos que o atleta está quebrado no banco deles
                if consecutive_500_errors >= 3:
                    raise Exception(f"FALHA CRÍTICA: Servidor CBF retornou erro {response.status_code} repetidamente para este atleta.")
            
            continue

        # Se a resposta for 200, reseta o contador de erros 500
        consecutive_500_errors = 0

        try:
            response_json = response.json()
        except Exception as e:
            print(f"Erro ao parsear JSON: {e}")
            continue

        # Verificar erro de captcha
        if (isinstance(response_json, dict) and 
            response_json.get('status') == False and 
            'messages' in response_json and
            any('captcha' in msg.lower() and 'invalido' in msg.lower() for msg in response_json['messages'])):
            
            print(f"❌ Captcha incorreto.")
            continue
        
        # Verificar erro de API
        if isinstance(response_json, dict) and 'error' in response_json:
            print(f"Erro da API: {response_json['error']}")
            continue
        
        # === SUCESSO! ===
        print(f"\n✅ Dados do atleta obtidos com sucesso!")
        
        if current_captcha_base64 and current_captcha:
            salvar_dataset_ouro(current_captcha_base64, current_captcha)
        
        return response_json
    
    print(f"\n❌ Falha após {max_retries} tentativas.")
    raise Exception(f'Não foi possível obter dados após {max_retries} tentativas')