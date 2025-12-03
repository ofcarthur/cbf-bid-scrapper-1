#!/usr/bin/env python3
"""
DEBUG: Análise detalhada de captchas para diagnóstico do modelo ML

Este script testa 3 atletas específicos e salva:
- Imagens dos captchas (base64 decodificado)
- Códigos gerados pelo modelo ML
- Logs detalhados do processo

Para diagnosticar problemas de acurácia do modelo.
"""

import sys
import os
import json
import base64
import time
from datetime import datetime

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapper.scrapper import buscar_historico_atleta

def salvar_captcha_debug(captcha_base64, codigo_gerado, codigo_atleta, tentativa):
    """Salva imagem do captcha para debug"""
    try:
        # Criar diretório se não existir
        debug_dir = "debug_captchas"
        os.makedirs(debug_dir, exist_ok=True)
        
        # Nome do arquivo com timestamp
        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"{debug_dir}/captcha_atleta_{codigo_atleta}_tent_{tentativa}_{timestamp}_{codigo_gerado}.png"
        
        # Decodificar base64 e salvar
        if captcha_base64.startswith('data:image'):
            # Remove header se presente
            captcha_data = captcha_base64.split(',')[1]
        else:
            captcha_data = captcha_base64
            
        with open(filename, 'wb') as f:
            f.write(base64.b64decode(captcha_data))
            
        print(f"🖼️  Captcha salvo: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Erro ao salvar captcha: {e}")
        return None

def log_debug(message):
    """Log com timestamp detalhado"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] DEBUG: {message}")

def main():
    # Teste com apenas 3 atletas para debug
    atletas_teste = ["729084", "729085", "729086"]
    
    print("="*100)
    print("🔍 DEBUG: ANÁLISE DETALHADA DE CAPTCHAS")
    print("="*100)
    print(f"🧪 Testando {len(atletas_teste)} atletas: {', '.join(atletas_teste)}")
    print("🎯 Objetivo: Diagnosticar problemas de acurácia do modelo ML")
    print("📁 Captchas serão salvos em: ./debug_captchas/")
    print("-"*100)
    
    for i, codigo_atleta in enumerate(atletas_teste):
        print(f"\n{'='*80}")
        print(f"🔬 ATLETA {i+1}/{len(atletas_teste)}: {codigo_atleta}")
        print(f"{'='*80}")
        
        log_debug(f"Iniciando análise do atleta {codigo_atleta}")
        
        # Vamos interceptar o processo de busca para capturar os captchas
        # Para isso, vamos usar a função interna modificada
        try:
            resultado = debug_buscar_com_captcha_save(codigo_atleta)
            
            if resultado['sucesso']:
                print(f"✅ SUCESSO: {resultado['dados']['nome']} - {resultado['dados']['clube']}")
                log_debug(f"Atleta {codigo_atleta} processado com sucesso")
            else:
                print(f"❌ FALHA: {resultado['erro']}")
                log_debug(f"Falha no atleta {codigo_atleta}: {resultado['erro']}")
                
        except Exception as e:
            print(f"❌ ERRO GERAL: {e}")
            log_debug(f"Erro geral no atleta {codigo_atleta}: {e}")
        
        # Pausa entre atletas
        if i < len(atletas_teste) - 1:
            print(f"\n⏱️  Aguardando 5 segundos antes do próximo atleta...")
            time.sleep(5)
    
    print(f"\n{'='*100}")
    print("🎯 DEBUG CONCLUÍDO!")
    print("📁 Verifique as imagens salvas em ./debug_captchas/")
    print("🔍 Compare os códigos gerados com as imagens para avaliar a acurácia")
    print("="*100)

def debug_buscar_com_captcha_save(codigo_atleta):
    """Versão modificada da busca que salva captchas para debug"""
    import requests
    import random
    from bs4 import BeautifulSoup
    
    try:
        # Import das funções de captcha
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from captcha_ml.captcha_solver import CaptchaSolver
        solver = CaptchaSolver()
        captcha_ml_disponivel = solver.is_loaded
    except:
        captcha_ml_disponivel = False
    
    if not captcha_ml_disponivel:
        return {"sucesso": False, "erro": "Sistema ML não disponível"}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    
    session = requests.Session()
    session.headers.update({'User-Agent': headers['User-Agent']})
    
    # Acessar página do atleta
    log_debug(f"Acessando página do atleta {codigo_atleta}")
    response_atleta = session.get(f'https://bid.cbf.com.br/atleta-competicoes/{codigo_atleta}', 
                                  headers=headers, timeout=10)
    
    if response_atleta.status_code != 200:
        return {"sucesso": False, "erro": f"Erro ao acessar página: {response_atleta.status_code}"}
    
    # Extrair CSRF token
    soup = BeautifulSoup(response_atleta.text, 'html.parser')
    csrf_meta = soup.find('meta', {'name': 'csrf-token'})
    if csrf_meta:
        csrf_token = csrf_meta.get('content')
        headers['X-CSRF-TOKEN'] = csrf_token
        log_debug(f"CSRF token obtido: {csrf_token[:20]}...")
    
    # Loop de tentativas com debug
    for tentativa in range(1, 3):  # 3 tentativas
        log_debug(f"Tentativa {tentativa}/15 para atleta {codigo_atleta}")
        
        # Obter captcha
        captcha_response = session.get('https://bid.cbf.com.br/get-captcha-base64', 
                                     headers=headers, timeout=10)
        
        if captcha_response.status_code != 200:
            continue
            
        # Extrair base64 do captcha
        content_type = captcha_response.headers.get('content-type', '').lower()
        if 'json' in content_type:
            captcha_data = captcha_response.json()
            captcha_base64 = captcha_data.get('image', '')
        else:
            captcha_base64 = captcha_response.text.strip()
        
        if not captcha_base64:
            continue
            
        # Resolver captcha com ML
        log_debug(f"Resolvendo captcha com ML - tentativa {tentativa}")
        codigo_captcha = solver.solve_captcha_from_base64(captcha_base64)
        
        if not codigo_captcha:
            log_debug(f"Falha na resolução ML - tentativa {tentativa}")
            continue
            
        log_debug(f"Captcha resolvido: '{codigo_captcha}' - tentativa {tentativa}")
        
        # Salvar captcha para debug
        salvar_captcha_debug(captcha_base64, codigo_captcha, codigo_atleta, tentativa)
        
        # Enviar requisição
        dados = {
            'codigo_atleta': str(codigo_atleta),
            'captcha': codigo_captcha
        }
        
        log_debug(f"Enviando requisição com captcha '{codigo_captcha}'")
        response = session.post('https://bid.cbf.com.br/atleta-historico-json', 
                               data=dados, headers=headers, timeout=10)
        
        if response.status_code != 200:
            log_debug(f"Erro HTTP {response.status_code} - tentativa {tentativa}")
            continue
            
        try:
            response_json = response.json()
        except:
            log_debug(f"Erro ao parsear JSON - tentativa {tentativa}")
            continue
        
        # Verificar se captcha foi aceito
        if (isinstance(response_json, dict) and 
            response_json.get('status') == False and 
            'messages' in response_json and
            any('captcha' in msg.lower() and 'invalido' in msg.lower() for msg in response_json['messages'])):
            
            log_debug(f"Captcha '{codigo_captcha}' rejeitado pelo servidor - tentativa {tentativa}")
            time.sleep(2)  # Pausa antes da próxima tentativa
            continue
        
        # Sucesso!
        if isinstance(response_json, dict) and response_json.get('codigo_atleta'):
            log_debug(f"Sucesso! Dados obtidos para atleta {codigo_atleta}")
            return {"sucesso": True, "dados": response_json}
    
    return {"sucesso": False, "erro": "Falhou após 3 tentativas - captchas sempre rejeitados"}

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
