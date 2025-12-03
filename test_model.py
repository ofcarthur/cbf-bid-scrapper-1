#!/usr/bin/env python3

import cv2
import numpy as np
from captcha_ml.captcha_model import CaptchaModel
from captcha_ml.image_processor import ImageProcessor
import pickle
import os
import glob

def test_model():
    """Testa o modelo treinado"""
    print('🔄 Iniciando teste do modelo...')
    
    try:
        # Carregar modelo
        model = CaptchaModel()
        processor = ImageProcessor()

        # Carregar mapeamentos
        print('📁 Carregando mapeamentos...')
        with open('captcha_ml/models/mappings.pkl', 'rb') as f:
            mappings = pickle.load(f)

        model.char_to_num = mappings['char_to_num']
        model.num_to_char = mappings['num_to_char']
        model.characters = mappings['characters']
        model.img_width = mappings['img_width']
        model.img_height = mappings['img_height']
        model.max_length = mappings['max_length']

        print(f'Caracteres suportados: {len(model.characters)} - {model.characters}')

        # Recriar modelo e carregar pesos
        print('🧠 Recriando arquitetura...')
        model.create_model(len(model.characters))
        model.compile_model()
        model.model.load_weights('captcha_ml/models/model_weights.h5')
        print('✅ Modelo carregado com sucesso!')

        # Testar com algumas imagens rotuladas
        print('\n🔍 Buscando imagens de teste...')
        img_files = glob.glob('captcha_ml/data/labeled/*.png')[:10]
        print(f'Encontradas {len(img_files)} imagens para teste')

        if not img_files:
            print('❌ Nenhuma imagem encontrada!')
            return

        correct = 0
        total = 0

        print('\n📊 Testando predições...')
        for i, img_file in enumerate(img_files, 1):
            # Extrair label do nome do arquivo
            basename = os.path.basename(img_file)
            true_label = basename[:4]  # Primeiros 4 caracteres do nome
            
            # Carregar e processar imagem
            img = cv2.imread(img_file, cv2.IMREAD_GRAYSCALE)
            if img is None:
                print(f'❌ Erro ao carregar {basename}')
                continue
            
            # Preprocessar para o tamanho correto
            processed_img = processor.preprocess_image(img)
            
            # Fazer predição
            prediction = model.predict(processed_img)
            
            is_correct = prediction == true_label
            if is_correct:
                correct += 1
            total += 1
            
            status = "✅" if is_correct else "❌"
            print(f'{i:2d}. {basename[:25]:<25} | {true_label} → {prediction} {status}')

        accuracy = correct/total*100 if total > 0 else 0
        print(f'\n📊 RESULTADO FINAL')
        print(f'   Acertos: {correct}/{total}')
        print(f'   Acurácia: {accuracy:.1f}%')
        
        if accuracy > 50:
            print('🎉 Modelo está funcionando bem!')
        else:
            print('⚠️  Modelo precisa de mais treinamento')

    except Exception as e:
        print(f'❌ Erro durante o teste: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_model()
