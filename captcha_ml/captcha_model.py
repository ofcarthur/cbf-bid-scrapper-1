import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import os
from sklearn.model_selection import train_test_split
import pickle
import matplotlib.pyplot as plt

# --- Callback Visual Simples ---
class SimpleMonitor(keras.callbacks.Callback):
    """Callback simplificado para evitar erros de índice"""
    def __init__(self, validation_data, model_obj):
        self.validation_data = validation_data
        self.model_obj = model_obj

    def on_epoch_end(self, epoch, logs=None):
        if epoch % 5 != 0 and epoch != 0: return # Mostra a cada 5 épocas
        
        # Pega apenas 1 batch do dataset de validação para teste
        for batch in self.validation_data.take(1):
            images = batch["image"]
            labels = batch["label"]
            
            preds = self.model_obj.predict_batch(images)
            # Decodifica labels reais (que estão em numeros)
            real_labels_num = labels.numpy()
            
            print(f"\n--- Check Epoca {epoch+1} ---")
            for i in range(min(3, len(preds))): # Mostra 3 exemplos
                # Converte label real numérico para texto
                real_txt = self.model_obj.num_to_label(real_labels_num[i])
                print(f"Real: {real_txt:<5} | Pred: {preds[i]}")
            print("-------------------------")

class CTCLayer(layers.Layer):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.loss_fn = keras.backend.ctc_batch_cost

    def call(self, y_true, y_pred):
        batch_len = tf.cast(tf.shape(y_true)[0], dtype="int64")
        input_length = tf.cast(tf.shape(y_pred)[1], dtype="int64")
        label_length = tf.cast(tf.shape(y_true)[1], dtype="int64")

        input_length = input_length * tf.ones(shape=(batch_len, 1), dtype="int64")
        label_length = label_length * tf.ones(shape=(batch_len, 1), dtype="int64")

        loss = self.loss_fn(y_true, y_pred, input_length, label_length)
        self.add_loss(loss)
        return y_pred

class CaptchaModel:
    def __init__(self, img_width=180, img_height=50, max_length=4):
        self.img_width = img_width
        self.img_height = img_height
        self.max_length = max_length
        self.model = None
        self.prediction_model = None
        self.char_to_num = {}
        self.num_to_char = {}
        self.vocab_size = 0
        self.use_rescaling = True # Flag para controle de normalização
        
    def create_character_mappings(self, labels):
        all_chars = set()
        for label in labels:
            all_chars.update(list(label))
        
        vocab = sorted(list(all_chars))
        print(f"Vocabulário ({len(vocab)} chars): {''.join(vocab)}")
        
        self.char_to_num = {char: idx for idx, char in enumerate(vocab)}
        self.num_to_char = {idx: char for idx, char in enumerate(vocab)}
        self.vocab_size = len(vocab)

    def label_to_num(self, label):
        return [self.char_to_num[char] for char in label]

    def num_to_label(self, num_arr):
        res = ""
        for num in num_arr:
            if num != -1 and num < self.vocab_size:
                res += self.num_to_char[int(num)]
        return res

    def create_model(self):
        input_img = layers.Input(shape=(self.img_width, self.img_height, 1), name="image")
        labels = layers.Input(name="label", shape=(None,), dtype="float32")

        # --- 1. Normalização Inteligente ---
        # Se os dados já forem float (0-1), isso não fará mal se configurado certo.
        # Mas vamos definir isso baseados na análise dos dados em prepare_data.
        if self.use_rescaling:
            x = layers.Rescaling(1.0 / 255)(input_img)
        else:
            x = input_img

        # --- 2. CNN Otimizada (Menos Pooling) ---
        # Bloco 1
        x = layers.Conv2D(32, (3, 3), activation="relu", kernel_initializer="he_normal", padding="same")(x)
        x = layers.MaxPooling2D((2, 2), name="pool1")(x) # 180 -> 90
        
        # Bloco 2
        x = layers.Conv2D(64, (3, 3), activation="relu", kernel_initializer="he_normal", padding="same")(x)
        x = layers.MaxPooling2D((2, 2), name="pool2")(x) # 90 -> 45
        
        # Bloco 3 (SEM POOLING)
        # Removemos o pool3 para manter a largura em 45. Isso ajuda o CTC.
        x = layers.Conv2D(128, (3, 3), activation="relu", kernel_initializer="he_normal", padding="same")(x)
        x = layers.Dropout(0.3)(x) 

        # Reshape
        # Largura final é img_width // 4 (pois fizemos 2 pools de 2x)
        new_width = self.img_width // 4
        # Altura e canais são fundidos nas features
        new_height_features = (self.img_height // 4) * 128
        
        x = layers.Reshape(target_shape=(new_width, new_height_features), name="reshape")(x)
        x = layers.Dense(64, activation="relu", name="dense1")(x)
        x = layers.Dropout(0.2)(x)

        # RNN
        x = layers.Bidirectional(layers.LSTM(128, return_sequences=True, dropout=0.25))(x)
        x = layers.Bidirectional(layers.LSTM(64, return_sequences=True, dropout=0.25))(x)

        # Output
        x = layers.Dense(self.vocab_size + 1, activation="softmax", name="dense2")(x)

        # CTC Loss
        output = CTCLayer(name="ctc_loss")(labels, x)

        self.model = keras.models.Model(inputs=[input_img, labels], outputs=output)
        self.prediction_model = keras.models.Model(inputs=input_img, outputs=x)

        # Otimizador
        try:
            # Tenta usar legacy para Mac
            opt = keras.optimizers.legacy.Adam(learning_rate=0.001, clipnorm=1.0)
        except:
            opt = keras.optimizers.Adam(learning_rate=0.001, clipnorm=1.0)
            
        self.model.compile(optimizer=opt)

    def decode_batch_predictions(self, pred):
        input_len = np.ones(pred.shape[0]) * pred.shape[1]
        results = keras.backend.ctc_decode(pred, input_length=input_len, greedy=True)[0][0][:, :self.max_length]
        
        output_text = []
        for res in results:
            output_text.append(self.num_to_label(res))
        return output_text

    def prepare_data(self, data_path, batch_size=32):
        data = np.load(data_path, allow_pickle=True)
        
        captchas_dict = {}
        for item in data:
            label = item['label']
            if label not in captchas_dict: captchas_dict[label] = []
            captchas_dict[label].append(item)
            
        unique_labels = list(captchas_dict.keys())
        train_labels_raw, val_labels_raw = train_test_split(unique_labels, test_size=0.15, random_state=42)
        
        all_labels = train_labels_raw + val_labels_raw
        self.create_character_mappings(all_labels)

        def build_dataset(label_list):
            X_data = []
            y_data = []
            for lbl in label_list:
                if lbl not in captchas_dict: continue
                for item in captchas_dict[lbl]:
                    img = item['image']
                    
                    # Transposição correta para CTC (Largura deve ser o primeiro eixo espacial)
                    # Queremos: (Largura, Altura, Canais)
                    if img.shape[0] < img.shape[1]: 
                        img = img.T 
                    
                    if len(img.shape) == 2:
                        img = np.expand_dims(img, axis=-1)
                    
                    X_data.append(img)
                    y_data.append(self.label_to_num(lbl))
            
            y_ragged = tf.ragged.constant(y_data)
            y_dense = y_ragged.to_tensor(default_value=self.vocab_size)
            
            return np.array(X_data), y_dense

        X_train, y_train = build_dataset(train_labels_raw)
        X_val, y_val = build_dataset(val_labels_raw)
        
        # --- DIAGNÓSTICO DE DADOS ---
        print(f"\n=== DIAGNÓSTICO DE DADOS ===")
        print(f"Shape Treino: {X_train.shape}")
        print(f"Valor Mínimo Pixel: {X_train.min()}")
        print(f"Valor Máximo Pixel: {X_train.max()}")
        
        # Decisão Automática de Normalização
        if X_train.max() > 1.0:
            print("Detectado range 0-255. Ativando Rescaling no modelo.")
            self.use_rescaling = True
        else:
            print("Detectado range 0-1 (ou similar). DESATIVANDO Rescaling para evitar black-out.")
            self.use_rescaling = False
        print("============================\n")

        train_ds = tf.data.Dataset.from_tensor_slices(({"image": X_train, "label": y_train})).batch(batch_size).prefetch(tf.data.AUTOTUNE)
        val_ds = tf.data.Dataset.from_tensor_slices(({"image": X_val, "label": y_val})).batch(batch_size).prefetch(tf.data.AUTOTUNE)
        
        return train_ds, val_ds

    def predict_batch(self, images):
        preds = self.prediction_model.predict(images, verbose=0)
        return self.decode_batch_predictions(preds)

    def train(self, data_path, epochs=50, batch_size=32, save_dir="captcha_ml/models"):
        os.makedirs(save_dir, exist_ok=True)
        
        train_ds, val_ds = self.prepare_data(data_path, batch_size=batch_size)
        
        self.create_model()
        self.model.summary()
        
        callbacks = [
            keras.callbacks.EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True),
            # ReduceLROnPlateau menos agressivo
            keras.callbacks.ReduceLROnPlateau(monitor="val_loss", patience=5, factor=0.5, min_lr=1e-6),
            SimpleMonitor(val_ds, self)
        ]
        
        history = self.model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=epochs,
            callbacks=callbacks
        )
        
        self.prediction_model.save_weights(os.path.join(save_dir, "ctc_model.weights.h5"))
        
        metadata = {
            'char_to_num': self.char_to_num,
            'num_to_char': self.num_to_char,
            'img_dims': (self.img_width, self.img_height),
            'vocab_size': self.vocab_size,
            'use_rescaling': self.use_rescaling # Salvar essa config
        }
        with open(os.path.join(save_dir, 'meta.pkl'), 'wb') as f:
            pickle.dump(metadata, f)
            
        return history

    def load_model(self, model_dir="captcha_ml/models"):
        with open(os.path.join(model_dir, 'meta.pkl'), 'rb') as f:
            meta = pickle.load(f)
            
        self.char_to_num = meta['char_to_num']
        self.num_to_char = meta['num_to_char']
        self.img_width, self.img_height = meta['img_dims']
        self.vocab_size = meta['vocab_size']
        self.use_rescaling = meta.get('use_rescaling', True)
        
        self.create_model()
        weights_path = os.path.join(model_dir, "ctc_model_weights.h5")
        if os.path.exists(weights_path):
            self.prediction_model.load_weights(weights_path)
            print("Modelo carregado!")
        else:
            print(f"Erro: Pesos não encontrados em {weights_path}")

    def predict(self, image):
        if image.shape[0] < image.shape[1]: 
            image = image.T
        if len(image.shape) == 2:
            image = np.expand_dims(image, axis=-1)
        
        image = np.expand_dims(image, axis=0)
        preds = self.prediction_model.predict(image, verbose=0)
        return self.decode_batch_predictions(preds)[0]

if __name__ == "__main__":
    model = CaptchaModel()
    data_path = "captcha_ml/data/processed/processed_data.npy"
    if os.path.exists(data_path):
        model.train(data_path, epochs=50, batch_size=32)