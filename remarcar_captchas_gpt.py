#!/usr/bin/env python3
"""
Auto-Labeling de Captchas usando ChatGPT Vision API

Este script:
1. Lê todas as imagens de captcha salvas
2. Envia para ChatGPT Vision API para identificar os caracteres
3. Cria um novo dataset com labels corretos
4. Opcionalmente retreina o modelo
"""

import os
import base64
import json
import requests
import numpy as np
from PIL import Image
import cv2
from datetime import datetime
import time

# Configurações da API OpenAI
OPENAI_API_KEY = input("Digite sua chave da API OpenAI: ").strip()
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

def encode_image_base64(image_path):
    """Converte imagem para base64 para envio à API"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def ask_gpt_vision(image_path):
    """Envia imagem para ChatGPT Vision API e obtém os caracteres"""
    
    # Encode da imagem
    base64_image = encode_image_base64(image_path)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    payload = {
        "model": "gpt-4o",  # ou gpt-4-vision-preview
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
        "max_tokens": 10
    }
    
    try:
        response = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        gpt_response = result['choices'][0]['message']['content'].strip().lower()
        
        # Validar resposta (deve ter exatamente 4 caracteres alfanuméricos)
        if len(gpt_response) == 4 and gpt_response.isalnum():
            return gpt_response
        else:
            print(f"⚠️ Resposta inválida do GPT: '{gpt_response}' - deve ter 4 caracteres")
            return None
            
    except Exception as e:
        print(f"❌ Erro na API OpenAI: {e}")
        return None

def load_image_as_array(image_path):
    """Carrega imagem e converte para array NumPy no formato esperado pelo modelo"""
    # Ler imagem em escala de cinza
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    if img is None:
        print(f"❌ Erro ao carregar imagem: {image_path}")
        return None
    
    # Normalizar para 0-255 se necessário
    if img.max() <= 1.0:
        img = (img * 255).astype(np.uint8)
    
    # Verificar dimensões e ajustar se necessário
    # O modelo espera (180, 50) - width x height
    if img.shape != (50, 180):  # OpenCV usa (height, width)
        # Redimensionar mantendo proporção ou não dependendo da necessidade
        img = cv2.resize(img, (180, 50))
    
    return img

def process_captcha_images():
    """Processa todas as imagens de captcha e cria novo dataset"""
    
    captcha_dir = "captcha_ml/data/raw"
    if not os.path.exists(captcha_dir):
        print(f"❌ Diretório {captcha_dir} não encontrado!")
        return None
    
    # Listar todas as imagens PNG
    image_files = [f for f in os.listdir(captcha_dir) if f.endswith('.png')]
    
    if not image_files:
        print(f"❌ Nenhuma imagem PNG encontrada em {captcha_dir}")
        return None
    
    print(f"🔍 Encontradas {len(image_files)} imagens de captcha")
    print(f"💰 Custo estimado: ~${len(image_files) * 0.01:.2f} USD (aprox)")
    
    confirm = input(f"Processar {len(image_files)} imagens com ChatGPT? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Operação cancelada.")
        return None
    
    # Processar imagens
    dataset = []
    successful = 0
    failed = 0
    
    print(f"\n🚀 Iniciando processamento...")
    
    for i, filename in enumerate(image_files, 1):
        image_path = os.path.join(captcha_dir, filename)
        
        print(f"\n[{i:2d}/{len(image_files)}] Processando: {filename}")
        
        # Carregar imagem como array
        img_array = load_image_as_array(image_path)
        if img_array is None:
            failed += 1
            continue
        
        # Obter label do ChatGPT
        print(f"  🧠 Consultando ChatGPT...")
        gpt_label = ask_gpt_vision(image_path)
        
        if gpt_label:
            print(f"  ✅ Label identificado: '{gpt_label}'")
            
            # Adicionar ao dataset
            dataset.append({
                'image': img_array,
                'label': gpt_label,
                'source_file': filename
            })
            successful += 1
        else:
            print(f"  ❌ Falha na identificação")
            failed += 1
        
        # Pausa para não sobrecarregar a API
        if i < len(image_files):
            time.sleep(1)
    
    print(f"\n📊 Processamento concluído:")
    print(f"  ✅ Sucessos: {successful}")
    print(f"  ❌ Falhas: {failed}")
    print(f"  📈 Taxa de sucesso: {successful/(successful+failed)*100:.1f}%")
    
    if successful == 0:
        print("❌ Nenhuma imagem foi processada com sucesso!")
        return None
    
    # Salvar dataset
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"captcha_ml/data/processed/gpt_labeled_data_{timestamp}.npy"
    
    # Criar diretório se não existir
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Salvar como numpy array
    np.save(output_file, np.array(dataset, dtype=object))
    
    print(f"\n💾 Dataset salvo em: {output_file}")
    print(f"📝 {successful} samples com labels do ChatGPT")
    
    return output_file

def merge_datasets(gpt_dataset_path):
    """Combina o novo dataset do GPT com os dados existentes"""
    
    original_path = "captcha_ml/data/processed/processed_data.npy"
    
    # Carregar dataset do GPT
    gpt_data = np.load(gpt_dataset_path, allow_pickle=True)
    print(f"📊 Dataset GPT: {len(gpt_data)} samples")
    
    # Carregar dataset original se existir
    if os.path.exists(original_path):
        original_data = np.load(original_path, allow_pickle=True)
        print(f"📊 Dataset original: {len(original_data)} samples")
        
        # Combinar
        merged_data = np.concatenate([original_data, gpt_data])
        print(f"📊 Dataset combinado: {len(merged_data)} samples")
    else:
        merged_data = gpt_data
        print(f"📊 Usando apenas dataset GPT: {len(merged_data)} samples")
    
    # Salvar dataset combinado
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    merged_path = f"captcha_ml/data/processed/merged_data_{timestamp}.npy"
    np.save(merged_path, merged_data)
    
    print(f"💾 Dataset combinado salvo: {merged_path}")
    return merged_path

def main():
    print("="*80)
    print("🤖 AUTO-LABELING DE CAPTCHAS COM CHATGPT")
    print("="*80)
    
    if not OPENAI_API_KEY:
        print("❌ API Key da OpenAI é obrigatória!")
        return 1
    
    # Processar imagens
    gpt_dataset_path = process_captcha_images()
    
    if not gpt_dataset_path:
        return 1
    
    # Perguntar se quer combinar com dados existentes
    merge = input("\nCombinar com dataset existente? (Y/n): ").strip().lower()
    if merge != 'n':
        final_dataset = merge_datasets(gpt_dataset_path)
    else:
        final_dataset = gpt_dataset_path
    
    # Perguntar se quer retreinar
    retrain = input(f"\nRetreinar modelo com novo dataset? (Y/n): ").strip().lower()
    if retrain != 'n':
        print("\n🚀 Iniciando retreinamento...")
        os.system(f"python3 captcha_pipeline.py train --data_path {final_dataset} --epochs 50")
    
    print("\n✅ Processo concluído!")
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
