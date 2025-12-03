#!/usr/bin/env python3
"""
TESTE DIRETO DO MODELO - Validar se o modelo consegue acertar suas próprias imagens de treinamento
"""

import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_model_on_training_data():
    """Testa o modelo nas próprias imagens de treinamento"""
    
    # Carregar solver
    from captcha_ml.captcha_solver import CaptchaSolver
    solver = CaptchaSolver()
    
    if not solver.is_loaded:
        print("❌ Modelo não carregado!")
        return
    
    print(f"✅ Modelo carregado! Vocabulário: {solver.vocab_size} chars.")
    print(f"Caracteres: {''.join(solver.num_to_char[i] for i in range(solver.vocab_size))}")
    
    # Testar com algumas imagens do dataset
    dataset_path = "captcha_ml/data/processed/extracted_labels_data_20251127_193240.npy"
    
    if not os.path.exists(dataset_path):
        print("❌ Dataset não encontrado!")
        return
    
    # Carregar dataset
    dataset = np.load(dataset_path, allow_pickle=True)
    print(f"📊 Dataset carregado: {len(dataset)} samples")
    
    # Testar com 10 amostras aleatórias
    import random
    test_samples = random.sample(list(dataset), 10)
    
    correct = 0
    total = 0
    
    print("\n🔍 TESTANDO 10 AMOSTRAS ALEATÓRIAS:")
    print("="*60)
    
    for i, sample in enumerate(test_samples, 1):
        image = sample['image']
        true_label = sample['label']
        filename = sample['source_file']
        
        # Converter numpy array para PIL Image
        from PIL import Image
        
        # Garantir que a imagem está no formato correto (altura, largura)
        if image.shape != (50, 180):
            import cv2
            image = cv2.resize(image, (180, 50))  # cv2.resize usa (width, height)
        
        # Converter para uint8 se necessário e criar PIL Image
        if image.max() <= 1.0:
            image = (image * 255).astype(np.uint8)
        else:
            image = image.astype(np.uint8)
            
        pil_image = Image.fromarray(image, mode='L')
        
        # Fazer predição usando método interno que aceita PIL Image
        try:
            processed_img = solver._preprocess_image(pil_image)
            preds = solver.prediction_model.predict(processed_img, verbose=0)
            predicted_label = solver._decode_batch_predictions(preds)[0]
            
        except Exception as e:
            print(f"❌ Erro na predição: {e}")
            predicted_label = "ERRO"
        
        # Verificar acerto
        is_correct = predicted_label == true_label
        if is_correct:
            correct += 1
        total += 1
        
        # Mostrar resultado
        status = "✅" if is_correct else "❌"
        print(f"{status} [{i:2d}/10] {filename}")
        print(f"    Real:     '{true_label}'")
        print(f"    Previsto: '{predicted_label}'")
        print()
    
    accuracy = (correct / total) * 100
    print("="*60)
    print(f"📈 RESULTADO FINAL:")
    print(f"   Corretos: {correct}/{total}")
    print(f"   Acurácia: {accuracy:.1f}%")
    
    if accuracy < 50:
        print("❌ MODELO COM PROBLEMAS GRAVES!")
        print("   O modelo não consegue nem acertar seus próprios dados de treinamento.")
        print("   Possíveis causas:")
        print("   1. Problema na arquitetura CRNN+CTC")
        print("   2. Problema no preprocessamento das imagens")
        print("   3. Problema na decodificação CTC")
        print("   4. Dataset corrompido ou labels errados")
    elif accuracy < 80:
        print("⚠️  MODELO PRECISA MELHORAR")
        print("   Acurácia abaixo do esperado para dados de treinamento.")
    else:
        print("✅ MODELO OK nos dados de treinamento!")
        print("   O problema pode estar na diferença entre treinamento e mundo real.")

if __name__ == "__main__":
    test_model_on_training_data()
