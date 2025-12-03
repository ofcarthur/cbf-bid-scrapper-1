#!/usr/bin/env python3
"""
EXTRATOR DE LABELS A PARTIR DOS NOMES DOS ARQUIVOS

Os arquivos de captcha têm nomes como:
- abgj_captcha_20251127_155441_286824.png (label: abgj)
- aczs_captcha_20251127_160616_487256.png (label: aczs)

Este script extrai os labels dos nomes dos arquivos e cria o dataset corretamente.
"""

import os
import numpy as np
import cv2
from datetime import datetime

def extract_label_from_filename(filename):
    """Extrai o label do nome do arquivo"""
    # Formato: {label}_captcha_{timestamp}_{id}.png
    if '_captcha_' in filename:
        return filename.split('_captcha_')[0]
    return None

def load_and_preprocess_image(image_path):
    """Carrega e preprocessa imagem para o formato esperado pelo modelo"""
    try:
        # Carregar imagem
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            print(f"❌ Erro ao carregar imagem: {image_path}")
            return None
        
        # Normalizar para 0-1
        img = img.astype(np.float32) / 255.0
        
        # Redimensionar para (50, 180) - height x width
        img = cv2.resize(img, (180, 50))
        
        return img
        
    except Exception as e:
        print(f"❌ Erro ao processar {image_path}: {e}")
        return None

def main():
    print("="*80)
    print("📂 EXTRATOR DE LABELS DOS NOMES DOS ARQUIVOS")
    print("="*80)
    
    input_dir = "captcha_ml/data/raw"
    output_dir = "captcha_ml/data/processed"
    
    if not os.path.exists(input_dir):
        print(f"❌ Diretório {input_dir} não encontrado!")
        return 1
    
    # Criar diretório de saída
    os.makedirs(output_dir, exist_ok=True)
    
    # Listar todas as imagens PNG
    image_files = [f for f in os.listdir(input_dir) if f.endswith('.png')]
    
    if not image_files:
        print(f"❌ Nenhuma imagem PNG encontrada em {input_dir}")
        return 1
    
    print(f"🔍 Encontradas {len(image_files)} imagens")
    
    # Processar imagens
    dataset = []
    successful = 0
    failed = 0
    
    for i, filename in enumerate(image_files, 1):
        print(f"[{i:4d}/{len(image_files):4d}] Processando: {filename}")
        
        # Extrair label do nome do arquivo
        label = extract_label_from_filename(filename)
        if not label:
            print(f"  ❌ Não foi possível extrair label do nome do arquivo")
            failed += 1
            continue
        
        # Validar label
        if len(label) != 4 or not label.isalnum():
            print(f"  ❌ Label inválido: '{label}' (deve ter 4 caracteres alfanuméricos)")
            failed += 1
            continue
        
        # Carregar e preprocessar imagem
        image_path = os.path.join(input_dir, filename)
        img_array = load_and_preprocess_image(image_path)
        
        if img_array is None:
            failed += 1
            continue
        
        print(f"  ✅ Label extraído: '{label}'")
        
        # Adicionar ao dataset
        dataset.append({
            'image': img_array,
            'label': label.lower(),  # Garantir minúsculas
            'source_file': filename
        })
        successful += 1
    
    print(f"\n📊 Processamento concluído:")
    print(f"  ✅ Sucessos: {successful}")
    print(f"  ❌ Falhas: {failed}")
    print(f"  📈 Taxa de sucesso: {successful/(successful+failed)*100:.1f}%")
    
    if successful == 0:
        print("❌ Nenhuma imagem foi processada com sucesso!")
        return 1
    
    # Salvar dataset
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"extracted_labels_data_{timestamp}.npy")
    
    # Salvar como numpy array
    np.save(output_file, np.array(dataset, dtype=object))
    
    print(f"\n💾 Dataset salvo em: {output_file}")
    print(f"📝 {successful} samples com labels extraídos dos nomes dos arquivos")
    
    # Estatísticas dos labels
    all_labels = [item['label'] for item in dataset]
    unique_labels = set(all_labels)
    print(f"\n📈 Estatísticas dos labels:")
    print(f"  🔤 Labels únicos: {len(unique_labels)}")
    print(f"  📊 Total de samples: {len(all_labels)}")
    
    # Mostrar alguns exemplos
    print(f"\n🔍 Primeiros 10 labels extraídos:")
    for i, item in enumerate(dataset[:10]):
        print(f"  {item['source_file']} → '{item['label']}'")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
