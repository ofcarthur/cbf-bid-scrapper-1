#!/usr/bin/env python3
"""
TESTE SIMPLES CHATGPT - 5 IMAGENS
"""

import os
import base64
import requests
import cv2
import numpy as np
from datetime import datetime
import time

# Configuração OpenAI
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = None

def encode_image_base64(image_path):
    """Codifica imagem em base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def ask_gpt_vision(image_path):
    """Envia imagem para ChatGPT Vision API e obtém os caracteres"""
    
    base64_image = encode_image_base64(image_path)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Esta imagem contém texto que precisa ser transcrito para um exercício de OCR.

Por favor, identifique os caracteres que você consegue ver na imagem. A imagem contém exatamente 4 caracteres alfanuméricos em sequência.

Responda apenas com os 4 caracteres que você consegue ler, da esquerda para a direita. Use letras minúsculas se forem letras.

Exemplo: se você vê "a", "3", "b", "7", responda apenas: a3b7"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }
    
    try:
        response = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            gpt_response = result['choices'][0]['message']['content'].strip().lower()
            
            # Validar resposta
            if len(gpt_response) == 4 and gpt_response.isalnum():
                return gpt_response
            else:
                print(f"⚠️ Resposta inválida do GPT: '{gpt_response}' - deve ter 4 caracteres")
                return None
        else:
            print(f"❌ Erro API OpenAI: {response.status_code}")
            return None
    
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def main():
    global OPENAI_API_KEY
    
    print("="*60)
    print("🤖 TESTE CHATGPT - 5 IMAGENS")
    print("="*60)
    
    # Solicitar API key
    OPENAI_API_KEY = input("Digite sua chave da API OpenAI: ").strip()
    if not OPENAI_API_KEY:
        print("❌ API key é obrigatória")
        return 1
    
    # Listar primeiras 5 imagens
    captcha_dir = "captcha_ml/data/raw"
    image_files = [f for f in os.listdir(captcha_dir) if f.endswith('.png')][:5]
    
    print(f"\n🔍 Testando com {len(image_files)} imagens...")
    
    for i, filename in enumerate(image_files, 1):
        print(f"\n[{i}/5] Processando: {filename}")
        image_path = os.path.join(captcha_dir, filename)
        
        # Tentar com GPT
        print("  🧠 Consultando ChatGPT...")
        gpt_label = ask_gpt_vision(image_path)
        
        if gpt_label:
            print(f"  ✅ GPT identificou: '{gpt_label}'")
            
            # Extrair label real do nome do arquivo
            if '_captcha_' in filename:
                real_label = filename.split('_captcha_')[0]
                if gpt_label == real_label:
                    print(f"  🎯 CORRETO! GPT == Real: '{real_label}'")
                else:
                    print(f"  ❌ DIFERENTE: GPT='{gpt_label}' vs Real='{real_label}'")
            else:
                print(f"  ❓ Sem label real para comparar")
        else:
            print(f"  ❌ GPT falhou")
        
        # Pausa entre requests
        if i < len(image_files):
            time.sleep(2)
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
