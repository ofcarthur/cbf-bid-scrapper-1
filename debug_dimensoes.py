#!/usr/bin/env python3
"""
Debug das dimensões das imagens - onde está o problema?
"""

import numpy as np
import os
from PIL import Image

def debug_image_dimensions():
    """Debug completo das dimensões"""
    
    # 1. Carregar uma imagem do dataset
    dataset_path = "captcha_ml/data/processed/extracted_labels_data_20251127_193240.npy"
    if not os.path.exists(dataset_path):
        print("❌ Dataset não encontrado!")
        return
        
    dataset = np.load(dataset_path, allow_pickle=True)
    sample = dataset[0]
    
    print("=== 1. IMAGEM DO DATASET ===")
    print(f"Shape original: {sample['image'].shape}")
    print(f"Label: {sample['label']}")
    
    # 2. Converter para PIL
    image = sample['image']
    
    # Garantir que está no formato correto para PIL
    if image.max() <= 1.0:
        image = (image * 255).astype(np.uint8)
    else:
        image = image.astype(np.uint8)
    
    pil_image = Image.fromarray(image, mode='L')
    print(f"PIL Image size (width, height): {pil_image.size}")
    
    # 3. Verificar o que o CaptchaSolver faz
    from captcha_ml.captcha_solver import CaptchaSolver
    solver = CaptchaSolver()
    
    if not solver.is_loaded:
        print("❌ Modelo não carregado!")
        return
        
    print("\n=== 2. PREPROCESSAMENTO DO SOLVER ===")
    print(f"solver.img_width: {solver.img_width}")  
    print(f"solver.img_height: {solver.img_height}")
    
    # Chamar _preprocess_image
    processed = solver._preprocess_image(pil_image)
    print(f"Shape após preprocessamento: {processed.shape}")
    
    # 4. Verificar dimensões esperadas pelo modelo
    print("\n=== 3. MODELO ===")
    if solver.prediction_model:
        input_shape = solver.prediction_model.input_shape
        print(f"Input shape esperado pelo modelo: {input_shape}")
    
    # 5. Verificar como era no treinamento
    print("\n=== 4. FORMATO NO TREINAMENTO ===")
    print("No captcha_pipeline.py:")
    print("- create_model() usa: input_img = layers.Input(shape=(self.img_width, self.img_height, 1)")
    print("- img_width = 180, img_height = 50")
    print("- Então espera: (None, 180, 50, 1)")
    
    print("\nNo prepare_data():")
    print("- if img.shape[0] < img.shape[1]: img = img.T")
    print("- Isso transpõe se altura < largura")
    
    # 6. Verificar se a imagem do dataset precisa de transposição
    print("\n=== 5. DIAGNÓSTICO ===")
    img_from_dataset = sample['image']
    height, width = img_from_dataset.shape
    print(f"Dataset image: {height}h x {width}w")
    
    if height < width:
        print("⚠️ Altura < Largura - seria transposta no treinamento!")
        transposed = img_from_dataset.T
        print(f"Após transposição: {transposed.shape}")
    else:
        print("✅ Altura >= Largura - não seria transposta no treinamento")

if __name__ == "__main__":
    debug_image_dimensions()
