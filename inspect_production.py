from captcha_ml.captcha_solver import CaptchaSolver
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import glob
import os

solver = CaptchaSolver()
debug_files = glob.glob("debug_captchas/*.png")

if not debug_files:
    print("Nenhuma imagem em debug_captchas/.")
else:
    # Pega a última imagem salva pelo robô
    img_path = max(debug_files, key=os.path.getctime)
    print(f"Analisando produção: {img_path}")

    # Carrega original
    original = Image.open(img_path)
    
    # --- O QUE ACONTECE NO SOLVER ---
    # Aqui chamamos o preprocessamento que tem o Threshold 160
    processed_array = solver._preprocess_image(original)
    
    # Extrai o array e simula a camada de inversão do modelo
    visual_data = processed_array[0, :, :, 0]
    
    # Normalização já foi feita no preprocess (astype float), mas vamos garantir 0-1 para visualização
    if visual_data.max() > 1.0:
        visual_data = visual_data / 255.0
        
    # Simula a camada Lambda (Inversão) do Keras
    model_input = 1.0 - visual_data
    
    # Plotar
    plt.figure(figsize=(5, 5))
    # Transpomos de volta para visualização humana
    plt.imshow(model_input.T, cmap='gray', vmin=0, vmax=1)
    plt.title(f"Produção: {os.path.basename(img_path)}\n(Com Threshold e Resize)")
    plt.axis('off')
    
    plt.tight_layout()
    plt.savefig("check_producao.png")
    print("✅ Salvei 'check_producao.png'. Abra para ver o que o modelo recebe hoje.")