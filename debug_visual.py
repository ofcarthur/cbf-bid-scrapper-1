from captcha_ml.captcha_solver import CaptchaSolver
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import glob
import os

solver = CaptchaSolver()
debug_files = glob.glob("debug_captchas/*.png")

if debug_files:
    # Pega a imagem mais recente
    img_path = max(debug_files, key=os.path.getctime)
    print(f"Analisando: {img_path}")

    original = Image.open(img_path)
    processed_array = solver._preprocess_image(original)
    
    # Pega os dados brutos e transpõe de volta
    visual_data = processed_array[0, :, :, 0].T
    
    # --- CORREÇÃO AQUI: Normalizar para 0..1 antes de inverter ---
    visual_data = visual_data / 255.0 
    
    pred = solver.solve_captcha_from_file(img_path)

    plt.figure(figsize=(10, 4))
    
    plt.subplot(1, 2, 1)
    plt.imshow(original)
    plt.title(f"Original\nPredição: {pred}")
    plt.axis('off')
    
    # Simula a visão da rede (Inverte cores: Fundo Preto, Texto Branco)
    simulated_view = 1.0 - visual_data
    
    plt.subplot(1, 2, 2)
    plt.imshow(simulated_view, cmap='gray', vmin=0, vmax=1)
    plt.title("O que a Rede Vê (Pós-Limpeza)\nTexto deve ser BRANCO, Fundo PRETO")
    plt.axis('off')
    
    plt.tight_layout()
    plt.savefig("diagnostico_final_v2.png")
    print("✅ Novo diagnóstico salvo em 'diagnostico_final_v2.png'")