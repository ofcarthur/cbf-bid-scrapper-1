import requests
from bs4 import BeautifulSoup
import re
import os
import sys

# Adicionar diretório raiz para importar captcha_ml
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from captcha_ml.captcha_solver import solve_captcha_auto
    CAPTCHA_SOLVER_AVAILABLE = True
except ImportError:
    CAPTCHA_SOLVER_AVAILABLE = False
    print("⚠️  Solver de captcha ML não disponível. Use captcha_code manual ou treine o modelo primeiro.")

def buscar_dados_bid(uf, data_publicacao, captcha_code=None, auto_solve=True):
    """
    Busca dados do BID da CBF
    
    Args:
        uf: Sigla do estado (ex: 'AL', 'SP')
        data_publicacao: Data no formato 'dd/mm/yyyy' (ex: '13/03/2020')
        captcha_code: Código do captcha (opcional, mas necessário na prática)
        auto_solve: Se True, tenta resolver captcha automaticamente com ML (default: True)
    
    Returns:
        Lista de registros de atletas
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://bid.cbf.com.br',
        'Referer': 'https://bid.cbf.com.br/'
    }
    
    # Criar uma sessão para manter cookies
    session = requests.Session()
    
    # Primeiro, acessar a página principal para obter o CSRF token e cookies
    print("Acessando página principal...")
    response_home = session.get('https://bid.cbf.com.br/', headers=headers, timeout=10)
    
    if response_home.status_code != 200:
        raise Exception(f'Erro ao acessar página principal: {response_home.status_code}')
    
    # Extrair o CSRF token
    soup = BeautifulSoup(response_home.text, 'html.parser')
    csrf_token = None
    csrf_meta = soup.find('meta', {'name': 'csrf-token'})
    if csrf_meta:
        csrf_token = csrf_meta.get('content')
        print(f"CSRF Token obtido: {csrf_token[:20]}...")
        headers['X-CSRF-TOKEN'] = csrf_token
    else:
        print("AVISO: CSRF token não encontrado")
    
    # Obter o captcha
    if captcha_code is None:
        print("\nObtendo captcha...")
        captcha_response = session.get('https://bid.cbf.com.br/get-captcha-base64', headers=headers, timeout=10)
        
        if captcha_response.status_code == 200:
            # Verificar se é JSON ou base64 direto
            content_type = captcha_response.headers.get('content-type', '').lower()
            
            if 'json' in content_type:
                captcha_data = captcha_response.json()
                captcha_base64 = captcha_data.get('image', '')
            else:
                # Resposta é base64 direto
                captcha_base64 = captcha_response.text.strip()
            
            # Tentar resolver automaticamente com ML se disponível
            if auto_solve and CAPTCHA_SOLVER_AVAILABLE and captcha_base64:
                print("🤖 Tentando resolver captcha automaticamente com ML...")
                captcha_code = solve_captcha_auto(captcha_base64)
                
                if captcha_code:
                    print(f"✓ Captcha resolvido automaticamente: '{captcha_code}'")
                else:
                    print("❌ Falha na resolução automática do captcha")
            
            # Se não conseguiu resolver automaticamente, mostrar instruções
            if captcha_code is None:
                print("\n" + "="*60)
                if CAPTCHA_SOLVER_AVAILABLE:
                    print("ATENÇÃO: Resolução automática falhou. Resolução manual necessária.")
                else:
                    print("ATENÇÃO: O site do BID agora requer resolver um CAPTCHA!")
                print("="*60)
                print("\nPara usar este scrapper, você precisa:")
                print("1. Acessar manualmente https://bid.cbf.com.br/")
                print("2. Preencher os filtros (data, UF)")
                print("3. Visualizar e resolver o captcha")
                print("4. Passar o código do captcha como parâmetro")
                print("\nExemplo:")
                print("  registros = buscar_dados_bid('AL', '13/03/2020', captcha_code='ABC123')")
                
                if not CAPTCHA_SOLVER_AVAILABLE:
                    print("\n💡 DICA: Para resolver captchas automaticamente, treine o modelo ML:")
                    print("  python captcha_pipeline.py collect --num 100")
                    print("  python captcha_pipeline.py label")
                    print("  python captcha_pipeline.py process")
                    print("  python captcha_pipeline.py train")
                
                print("="*60)
                
                raise Exception('Captcha necessário. Veja instruções acima.')
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
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code != 200:
        raise Exception(f'Erro na requisição: {response.status_code}')
    
    # Verificar se a resposta é JSON
    try:
        response_json = response.json()
    except Exception as e:
        print(f"Erro ao parsear JSON: {e}")
        print(f"Response text: {response.text[:500]}")
        raise Exception('Resposta inválida da API')
    
    # Verificar se há erros na resposta
    if isinstance(response_json, dict) and response_json.get('status') == False:
        messages = response_json.get('messages', {})
        error_msg = '; '.join([f"{k}: {v}" for k, v in messages.items()])
        raise Exception(f'Erro retornado pela API: {error_msg}')
    
    # Processar os dados
    if not isinstance(response_json, list):
        raise Exception(f'Formato de resposta inesperado: {type(response_json)}')
    
    print(f"\n{len(response_json)} registros encontrados")
    
    # O novo formato retorna JSON direto com os dados dos atletas
    registros = []
    
    for atleta in response_json:
        # Mapear os novos campos para o formato antigo esperado
        registros.append({
            'jogador': atleta.get('nome', ''),
            'operacao': atleta.get('tipocontrato', ''),  # Tipo de contrato (ex: Profissional)
            'publicacao': atleta.get('data_publicacao', ''),
            'clube': atleta.get('clube', ''),
            # Campos adicionais disponíveis no novo formato
            'apelido': atleta.get('apelido', ''),
            'codigo_atleta': atleta.get('codigo_atleta', ''),
            'contrato_numero': atleta.get('contrato_numero', ''),
            'data_inicio': atleta.get('datainicio', ''),
            'data_nascimento': atleta.get('data_nascimento', ''),
            'codigo_clube': atleta.get('codigo_clube', ''),
            'uf': atleta.get('uf', '')
        })
    
    return registros


def buscar_historico_atleta(codigo_atleta, captcha_code=None, auto_solve=True):
    """
    Busca histórico de um atleta específico no BID da CBF
    
    Args:
        codigo_atleta: Código do atleta (ex: '84629')
        captcha_code: Código do captcha (opcional, será resolvido automaticamente se disponível)
        auto_solve: Se True, tenta resolver captcha automaticamente com ML (default: True)
    
    Returns:
        Dict com dados do histórico do atleta
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://bid.cbf.com.br',
        'Referer': f'https://bid.cbf.com.br/atleta-competicoes/{codigo_atleta}',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    
    # Criar uma sessão para manter cookies
    session = requests.Session()
    
    # Primeiro, acessar a página do atleta para obter o CSRF token e cookies
    print(f"Acessando página do atleta {codigo_atleta}...")
    response_atleta = session.get(f'https://bid.cbf.com.br/atleta-competicoes/{codigo_atleta}', 
                                  headers=headers, timeout=10)
    
    if response_atleta.status_code != 200:
        raise Exception(f'Erro ao acessar página do atleta: {response_atleta.status_code}')
    
    # Extrair o CSRF token
    soup = BeautifulSoup(response_atleta.text, 'html.parser')
    csrf_token = None
    csrf_meta = soup.find('meta', {'name': 'csrf-token'})
    if csrf_meta:
        csrf_token = csrf_meta.get('content')
        print(f"CSRF Token obtido: {csrf_token[:20]}...")
        headers['X-CSRF-TOKEN'] = csrf_token
    else:
        print("AVISO: CSRF token não encontrado")
    
    # Obter o captcha se necessário
    if captcha_code is None:
        print("\nObtendo captcha...")
        captcha_response = session.get('https://bid.cbf.com.br/get-captcha-base64', 
                                     headers=headers, timeout=10)
        
        if captcha_response.status_code == 200:
            # Verificar se é JSON ou base64 direto
            content_type = captcha_response.headers.get('content-type', '').lower()
            
            if 'json' in content_type:
                captcha_data = captcha_response.json()
                captcha_base64 = captcha_data.get('image', '')
            else:
                # Resposta é base64 direto
                captcha_base64 = captcha_response.text.strip()
            
            # Tentar resolver automaticamente com ML se disponível
            if auto_solve and CAPTCHA_SOLVER_AVAILABLE and captcha_base64:
                print("🤖 Tentando resolver captcha automaticamente com ML...")
                captcha_code = solve_captcha_auto(captcha_base64)
                
                if captcha_code:
                    print(f"✓ Captcha resolvido automaticamente: '{captcha_code}'")
                else:
                    print("❌ Falha na resolução automática do captcha")
            
            # Se não conseguiu resolver automaticamente, mostrar instruções
            if captcha_code is None:
                print("\n" + "="*60)
                print("ATENÇÃO: Captcha necessário para acessar dados do atleta!")
                print("="*60)
                print("\nPara usar esta função, você precisa:")
                print(f"1. Acessar manualmente https://bid.cbf.com.br/atleta-competicoes/{codigo_atleta}")
                print("2. Resolver o captcha que aparece na página")
                print("3. Passar o código do captcha como parâmetro")
                print("\nExemplo:")
                print(f"  dados = buscar_historico_atleta('{codigo_atleta}', captcha_code='ABC123')")
                
                if not CAPTCHA_SOLVER_AVAILABLE:
                    print("\n💡 DICA: Para resolver captchas automaticamente, treine o modelo ML!")
                
                print("="*60)
                raise Exception('Captcha necessário. Veja instruções acima.')
        else:
            raise Exception(f'Erro ao obter captcha: {captcha_response.status_code}')
    
    # Preparar os dados para a requisição
    dados = {
        'codigo_atleta': str(codigo_atleta),
        'captcha': captcha_code
    }
    
    print(f"\nBuscando histórico do atleta {codigo_atleta}...")
    response = session.post('https://bid.cbf.com.br/atleta-historico-json', 
                           data=dados, 
                           headers=headers, 
                           timeout=10)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code != 200:
        raise Exception(f'Erro na requisição: {response.status_code}')
    
    # Verificar se a resposta é JSON
    try:
        response_json = response.json()
    except Exception as e:
        print(f"Erro ao parsear JSON: {e}")
        print(f"Response text: {response.text[:500]}")
        raise Exception('Resposta inválida da API')
    
    # Verificar se há erros na resposta
    if isinstance(response_json, dict) and 'error' in response_json:
        raise Exception(f'Erro retornado pela API: {response_json["error"]}')
    
    print(f"\n✅ Dados do atleta obtidos com sucesso!")
    
    # Retornar os dados como estão (já no formato correto baseado no seu exemplo)
    return response_json
