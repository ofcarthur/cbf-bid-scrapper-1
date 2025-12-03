import numpy as np
import matplotlib.pyplot as plt
import os

# Caminho do arquivo de dados processados
data_path = "captcha_ml/data/processed/processed_data.npy"

if not os.path.exists(data_path):
    print("Erro: Arquivo de dados não encontrado.")
else:
    print("Carregando dados de treino...")
    data = np.load(data_path, allow_pickle=True)
    
    # Pegar 3 amostras aleatórias
    indices = np.random.randint(0, len(data), 3)
    
    plt.figure(figsize=(15, 5))
    
    for i, idx in enumerate(indices):
        item = data[idx]
        img = item['image'] # Imagem crua (0-255)
        label = item['label']
        
        # --- SIMULAÇÃO DO QUE ACONTECE DENTRO DO MODELO ---
        # 1. Transposição (se necessário, baseado no seu código de treino)
        if img.shape[0] < img.shape[1]:
            img = img.T
            
        # 2. Normalização (Rescaling 1./255)
        img_float = img.astype(float) / 255.0
        
        # 3. Inversão (Lambda 1.0 - z)
        # É isso que as camadas Conv2D realmente enxergam
        model_view = 1.0 - img_float
        
        # Plotar
        plt.subplot(1, 3, i+1)
        # Transpomos de volta só para o humano ver de pé
        plt.imshow(model_view.squeeze().T, cmap='gray', vmin=0, vmax=1)
        plt.title(f"Treino: {label}\n(Simulação da Entrada)")
        plt.axis('off')
        
    plt.tight_layout()
    plt.savefig("check_treino.png")
    print("✅ Salvei 'check_treino.png'. Abra para ver o que o modelo aprendeu.")