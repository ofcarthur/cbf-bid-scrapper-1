import numpy as np
from PIL import Image
import os
import glob
import sys

class ImageProcessor:
    """
    Processador de Imagens Otimizado v2.
    - Suporta múltiplas fontes de dados (Raw + Ouro).
    - Garante consistência exata com o CaptchaSolver (PIL + Padding).
    """
    
    def __init__(self, processed_data_dir="captcha_ml/data/processed"):
        # Define as pastas onde vamos buscar imagens
        # 1. raw: Dados originais rotulados manualmente
        # 2. dataset_ouro: Dados coletados e validados pelo robô em produção
        self.source_dirs = [
            "captcha_ml/data/raw",
            "captcha_ml/data/dataset_ouro"
        ]
        self.processed_data_dir = processed_data_dir
        self.img_width = 180
        self.img_height = 50
        
    def preprocess_image(self, image_path):
        """
        Lê e processa uma imagem.
        IMPORTANTE: Esta lógica deve ser IDÊNTICA à do captcha_solver.py
        para evitar 'Training-Serving Skew'.
        """
        img = Image.open(image_path)
            
        # 1. Tratar Transparência (Igual ao Solver)
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            bg = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P': img = img.convert('RGBA')
            bg.paste(img, mask=img.split()[-1])
            img = bg
            
        # 2. Converter para Cinza
        img = img.convert('L')
        
        # 3. Threshold (Binarização - Texto Branco, Fundo Preto)
        # Transforma tudo < 180 (Texto) em 255 (Branco)
        img = img.point(lambda p: 255 if p < 180 else 0)
        
        # 4. Redimensionar com Padding (Manter proporção)
        target_w, target_h = self.img_width, self.img_height
        
        # Calcula proporção
        ratio = min(target_w / img.width, target_h / img.height)
        new_w = int(img.width * ratio)
        new_h = int(img.height * ratio)
        
        # Resize (Nearest para manter bordas duras)
        img = img.resize((new_w, new_h), Image.Resampling.NEAREST)
        
        # Cola no centro de um fundo preto
        final_img = Image.new('L', (target_w, target_h), 0)
        offset_x = (target_w - new_w) // 2
        offset_y = (target_h - new_h) // 2
        final_img.paste(img, (offset_x, offset_y))
        
        # Retorna array 0-255 (O pipeline de treino fará a normalização final 0-1)
        return np.array(final_img)

    def process_dataset(self):
        """Lê imagens de TODAS as pastas fonte e salva em um único .npy"""
        os.makedirs(self.processed_data_dir, exist_ok=True)
        
        all_images = []
        all_labels = []
        
        print("--- INICIANDO PROCESSAMENTO DE IMAGENS ---")
        [print(f"📁 Fonte configurada: {d}") for d in self.source_dirs]
        print("-" * 40)
        
        total_count = 0
        
        for source_dir in self.source_dirs:
            if not os.path.exists(source_dir):
                print(f"⚠️ Aviso: Pasta não encontrada: {source_dir} (Pulando)")
                continue
                
            # Busca todos os PNGs
            files = glob.glob(os.path.join(source_dir, "*.png"))
            print(f"📂 Processando {len(files)} imagens de: {os.path.basename(source_dir)}")
            
            local_count = 0
            for file_path in files:
                try:
                    filename = os.path.basename(file_path)
                    
                    # Extrair label
                    # Suporta formato simples: 'abcd.png'
                    # Suporta formato ouro: 'abcd_17321234.png'
                    label = filename.split('.')[0].split('_')[0]
                    
                    # Validação básica
                    if len(label) != 4:
                        continue
                    
                    # Processar
                    img_array = self.preprocess_image(file_path)
                    
                    all_images.append(img_array)
                    all_labels.append(label)
                    local_count += 1
                    
                except Exception as e:
                    print(f"❌ Erro em {filename}: {e}")
            
            print(f"   -> {local_count} imagens válidas adicionadas.")
            total_count += local_count

        if total_count == 0:
            print("\n❌ ERRO CRÍTICO: Nenhuma imagem válida encontrada em nenhuma pasta.")
            return
            
        # Salvar o arquivo consolidado
        data = []
        for img, lbl in zip(all_images, all_labels):
            data.append({'image': img, 'label': lbl})
            
        output_path = os.path.join(self.processed_data_dir, "processed_data.npy")
        np.save(output_path, data)
        
        print("\n" + "="*40)
        print(f"✅ PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
        print(f"Total acumulado: {len(data)} amostras")
        print(f"Arquivo salvo: {output_path}")
        print("Agora você pode rodar 'python3 captcha_pipeline.py train'")
        print("="*40)

if __name__ == "__main__":
    # Ajuste de diretório para execução
    if os.path.basename(os.getcwd()) == "captcha_ml":
        os.chdir("..")
        
    processor = ImageProcessor()
    processor.process_dataset()