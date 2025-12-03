import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from PIL import Image
import io
import base64
import os
import pickle

class CaptchaSolver:
    """
    Solver Otimizado v3.
    Compatível com o modelo treinado com 3 Pools, Dense 128 e pré-processamento binário.
    """
    
    def __init__(self, model_dir="captcha_ml/models"):
        self.model_dir = model_dir
        self.prediction_model = None
        self.char_to_num = {}
        self.num_to_char = {}
        self.img_width = 180
        self.img_height = 50
        self.max_length = 4
        self.vocab_size = 0
        self.is_loaded = False
        
        try:
            self.load_model()
        except Exception as e:
            print(f"⚠️ Aviso: Modelo não carregado: {e}")

    def load_model(self):
        # 1. Carregar Metadados
        meta_path = os.path.join(self.model_dir, 'meta.pkl')
        if not os.path.exists(meta_path):
            raise FileNotFoundError(f"Meta arquivo não encontrado: {meta_path}")
            
        with open(meta_path, 'rb') as f:
            meta = pickle.load(f)
            self.char_to_num = meta['char_to_num']
            self.num_to_char = meta['num_to_char']
            self.vocab_size = meta['vocab_size']
            # Garante chaves inteiras para decodificação
            self.num_to_char = {int(k): v for k, v in self.num_to_char.items()}
            
        # 2. MÉTODO ALTERNATIVO: Usar diretamente o CaptchaModel
        try:
            from captcha_ml.captcha_model import CaptchaModel
            
            model = CaptchaModel(img_width=180, img_height=50, max_length=4)
            model.char_to_num = self.char_to_num
            model.num_to_char = self.num_to_char
            model.vocab_size = self.vocab_size
            
            # Construir modelo primeiro
            model.create_model()
            
            # Tentar carregar pesos diretamente
            weights_path = os.path.join(self.model_dir, "ctc_model.weights.h5")
            checkpoint_path = os.path.join(self.model_dir, "ctc_model_checkpoint.weights.h5")
            
            if os.path.exists(weights_path):
                model.prediction_model.load_weights(weights_path)
                print("✅ Pesos carregados: ctc_model.weights.h5")
            elif os.path.exists(checkpoint_path):
                model.prediction_model.load_weights(checkpoint_path)
                print("✅ Pesos carregados: ctc_model_checkpoint.weights.h5")
            else:
                raise FileNotFoundError("Nenhum arquivo de pesos encontrado")
            
            self.prediction_model = model.prediction_model
            self.is_loaded = True
            print(f"✅ Modelo carregado via CaptchaModel! Vocabulário: {self.vocab_size} chars.")
            return
            
        except Exception as e:
            print(f"⚠️ Método CaptchaModel falhou: {e}")
            # Continua para método original abaixo
        self._build_model()
        
        # 3. Carregar Pesos
        weights_path = os.path.join(self.model_dir, "ctc_model.weights.h5")
        checkpoint_path = os.path.join(self.model_dir, "ctc_model_checkpoint.weights.h5")
        
        final_path_to_load = None
        
        if os.path.exists(weights_path):
            final_path_to_load = weights_path
        elif os.path.exists(checkpoint_path):
            final_path_to_load = checkpoint_path
            print("⚠️ Usando arquivo de checkpoint.")
        else:
             raise FileNotFoundError(f"Nenhum arquivo de pesos (.weights.h5) encontrado em {self.model_dir}")
            
        self.prediction_model.load_weights(final_path_to_load)
        self.is_loaded = True
        print(f"✅ Modelo carregado! Vocabulário: {self.vocab_size} chars.")

    def _build_model(self):
        """Usar EXATA arquitetura do CaptchaModel treinado"""
        input_img = layers.Input(shape=(self.img_width, self.img_height, 1), name="image")
        
        # Rescaling (0-255 -> 0-1) - igual ao modelo treinado
        x = layers.Rescaling(1./255.)(input_img)

        # CNN - Bloco 1
        x = layers.Conv2D(32, (3, 3), activation="relu", kernel_initializer="he_normal", padding="same")(x)
        x = layers.MaxPooling2D((2, 2), name="pool1")(x)  # 180 -> 90
        
        # CNN - Bloco 2
        x = layers.Conv2D(64, (3, 3), activation="relu", kernel_initializer="he_normal", padding="same")(x)
        x = layers.MaxPooling2D((2, 2), name="pool2")(x)  # 90 -> 45

        # CNN - Bloco 3 (SEM POOLING, igual ao modelo de treino)
        x = layers.Conv2D(128, (3, 3), activation="relu", kernel_initializer="he_normal", padding="same")(x)
        x = layers.Dropout(0.3)(x)

        # Reshape - dimensões corretas do modelo treinado
        new_width = self.img_width // 4  # 45
        new_height_features = (self.img_height // 4) * 128  # 12 * 128 = 1536
        x = layers.Reshape(target_shape=(new_width, new_height_features), name="reshape")(x)
        
        # Dense com dimensões corretas (1536 -> 64)
        x = layers.Dense(64, activation="relu", name="dense1")(x)
        x = layers.Dropout(0.2)(x)

        # RNN - mesma configuração do modelo treinado
        x = layers.Bidirectional(layers.LSTM(128, return_sequences=True, dropout=0.25))(x)
        x = layers.Bidirectional(layers.LSTM(64, return_sequences=True, dropout=0.25))(x)

        x = layers.Dense(self.vocab_size + 1, activation="softmax", name="dense2")(x)

        self.prediction_model = keras.models.Model(inputs=input_img, outputs=x)

    def _preprocess_image(self, pil_image):
        """
        Preprocessamento compatível com modelo treinado (valores 0-255).
        """
        # 1. Tratar Transparência -> Fundo Branco
        if pil_image.mode in ('RGBA', 'LA') or (pil_image.mode == 'P' and 'transparency' in pil_image.info):
            background = Image.new('RGB', pil_image.size, (255, 255, 255))
            if pil_image.mode == 'P': pil_image = pil_image.convert('RGBA')
            background.paste(pil_image, mask=pil_image.split()[-1])
            pil_image = background
        
        # 2. Converter para Cinza
        pil_image = pil_image.convert('L')
        
        # 3. Threshold Agressivo (Texto < 180 vira BRANCO Puro, Fundo vira PRETO)
        threshold = 180 
        pil_image = pil_image.point(lambda p: 255 if p < threshold else 0)
        
        # 4. Resize com Padding (Manter proporção)
        target_w, target_h = self.img_width, self.img_height
        ratio = min(target_w / pil_image.width, target_h / pil_image.height)
        new_w = int(pil_image.width * ratio)
        new_h = int(pil_image.height * ratio)
        
        pil_image = pil_image.resize((new_w, new_h), Image.Resampling.NEAREST)
        
        final_image = Image.new('L', (target_w, target_h), 0) # Fundo Preto
        offset_x = (target_w - new_w) // 2
        offset_y = (target_h - new_h) // 2
        final_image.paste(pil_image, (offset_x, offset_y))
        
        # 5. Converter para array (manter valores 0-255 para o rescaling do modelo)
        img_array = np.array(final_image).astype(np.float32)
            
        # 6. Dims (W, H, C) - transpor para formato correto
        img_array = img_array.T
        img_array = np.expand_dims(img_array, axis=-1)
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array

    def _decode_batch_predictions(self, pred):
        input_len = np.ones(pred.shape[0]) * pred.shape[1]
        results = keras.backend.ctc_decode(pred, input_length=input_len, greedy=True)[0][0]
        output_text = []
        for res in results:
            res_str = ""
            for val in res:
                if val != -1 and val < self.vocab_size:
                    res_str += self.num_to_char[int(val)]
            output_text.append(res_str)
        return output_text

    def solve_captcha_from_base64(self, base64_string):
        if not self.is_loaded: return None
        try:
            if base64_string.startswith('data:image'): base64_string = base64_string.split(',')[1]
            image_data = base64.b64decode(base64_string)
            pil_image = Image.open(io.BytesIO(image_data))
            
            processed_img = self._preprocess_image(pil_image)
            preds = self.prediction_model.predict(processed_img, verbose=0)
            return self._decode_batch_predictions(preds)[0]
        except Exception as e:
            # print(f"Erro ML: {e}")
            return None

    def solve_captcha_from_file(self, image_path):
        if not self.is_loaded: return None
        try:
            pil_image = Image.open(image_path)
            processed_img = self._preprocess_image(pil_image)
            preds = self.prediction_model.predict(processed_img, verbose=0)
            return self._decode_batch_predictions(preds)[0]
        except Exception as e:
            # print(f"Erro ML: {e}")
            return None

def solve_captcha_auto(base64_string, model_dir="captcha_ml/models"):
    if not hasattr(solve_captcha_auto, "solver"):
        solve_captcha_auto.solver = CaptchaSolver(model_dir)
    return solve_captcha_auto.solver.solve_captcha_from_base64(base64_string)

if __name__ == "__main__":
    solver = CaptchaSolver()
    if solver.is_loaded:
        import glob
        debug_imgs = glob.glob("debug_captchas/*.png")
        if debug_imgs:
            print(f"Testando {len(debug_imgs)} imagens...")
            for img in debug_imgs[:5]:
                res = solver.solve_captcha_from_file(img)
                print(f"{os.path.basename(img)} -> {res}")