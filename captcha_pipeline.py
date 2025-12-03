import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import os
from sklearn.model_selection import train_test_split
import pickle
import sys

# --- CONFIGURAÇÃO ---
DEBUG_OVERFIT = False

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

        # Dados já entram 0.0 (Preto) e 1.0 (Branco) do prepare_data
        x = input_img 

        # CNN Bloco 1
        x = layers.Conv2D(32, (3, 3), padding="same", kernel_initializer="he_normal")(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation("relu")(x)
        x = layers.MaxPooling2D((2, 2), name="pool1")(x)
        
        # CNN Bloco 2
        x = layers.Conv2D(64, (3, 3), padding="same", kernel_initializer="he_normal")(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation("relu")(x)
        x = layers.MaxPooling2D((2, 2), name="pool2")(x)

        # CNN Bloco 3
        x = layers.Conv2D(128, (3, 3), padding="same", kernel_initializer="he_normal")(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation("relu")(x)
        x = layers.MaxPooling2D((2, 2), name="pool3")(x) 

        # Reshape
        new_width = self.img_width // 8
        new_height_features = (self.img_height // 8) * 128
        x = layers.Reshape(target_shape=(new_width, new_height_features), name="reshape")(x)
        
        x = layers.Dense(128, activation="relu")(x)
        x = layers.Dropout(0.2)(x)

        # RNN
        x = layers.Bidirectional(layers.LSTM(256, return_sequences=True, dropout=0.2))(x)
        x = layers.Bidirectional(layers.LSTM(128, return_sequences=True, dropout=0.2))(x)

        x = layers.Dense(self.vocab_size + 1, activation="softmax", name="dense2")(x)

        output = CTCLayer(name="ctc_loss")(labels, x)

        self.model = keras.models.Model(inputs=[input_img, labels], outputs=output)
        self.prediction_model = keras.models.Model(inputs=input_img, outputs=x)

        opt = keras.optimizers.Adam(learning_rate=0.001)
        self.model.compile(optimizer=opt)

    def prepare_data(self, data_path, batch_size=32):
        data = np.load(data_path, allow_pickle=True)
        
        captchas_dict = {}
        for item in data:
            lbl = item['label']
            if lbl not in captchas_dict: captchas_dict[lbl] = []
            captchas_dict[lbl].append(item)
            
        unique_labels = list(captchas_dict.keys())
        train_labels, val_labels = train_test_split(unique_labels, test_size=0.1, random_state=42)
        
        self.create_character_mappings(unique_labels)
        
        def build_arrays(labels_subset):
            X, y = [], []
            for lbl in labels_subset:
                if lbl not in captchas_dict: continue
                for item in captchas_dict[lbl]:
                    img = item['image'] 
                    
                    # Garante normalização (0-1)
                    img = img.astype(np.float32)
                    if img.max() > 1.0: img = img / 255.0
                    
                    # Transposição se necessário
                    if img.shape[0] < img.shape[1]: img = img.T
                    if len(img.shape) == 2: img = np.expand_dims(img, axis=-1)
                    
                    # Threshold: Texto Branco, Fundo Preto
                    img_binary = np.where(img < 0.7, 1.0, 0.0)
                    
                    X.append(img_binary)
                    y.append(self.label_to_num(lbl))
            
            y_ragged = tf.ragged.constant(y)
            y_dense = y_ragged.to_tensor(default_value=self.vocab_size)
            return np.array(X), y_dense

        X_train, y_train = build_arrays(train_labels)
        X_val, y_val = build_arrays(val_labels)
        
        print(f"\nDados: Min={X_train.min()}, Max={X_train.max()}, Média={X_train.mean():.4f}")
        
        if DEBUG_OVERFIT:
            indices = np.random.randint(0, len(X_train), 32)
            X_train = np.tile(X_train[indices], (10, 1, 1, 1))
            y_train = np.tile(y_train[indices], (10, 1))
            X_val, y_val = X_train[:32], y_train[:32]

        train_ds = tf.data.Dataset.from_tensor_slices(({"image": X_train, "label": y_train})).shuffle(5000).batch(batch_size).prefetch(tf.data.AUTOTUNE)
        val_ds = tf.data.Dataset.from_tensor_slices(({"image": X_val, "label": y_val})).batch(batch_size).prefetch(tf.data.AUTOTUNE)
        
        return train_ds, val_ds

    def train(self, data_path, epochs=100, batch_size=32):
        # 1. DEFINIÇÃO DE CAMINHOS ABSOLUTOS
        base_dir = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.join(base_dir, "captcha_ml", "models")
        os.makedirs(models_dir, exist_ok=True)
        
        checkpoint_path = os.path.join(models_dir, "ctc_model_checkpoint.weights.h5")
        final_weights_path = os.path.join(models_dir, "ctc_model.weights.h5")
        meta_path = os.path.join(models_dir, "meta.pkl")
        
        print(f"\n📂 Diretório de salvamento: {models_dir}")

        train_ds, val_ds = self.prepare_data(data_path, batch_size)
        self.create_model()
        self.model.summary()
        
        # --- CRÍTICO: SALVAR METADADOS AGORA (Antes do treino começar) ---
        print("💾 Salvando metadados (dicionário de caracteres)...")
        with open(meta_path, 'wb') as f:
            pickle.dump({
                'char_to_num': self.char_to_num, 
                'num_to_char': self.num_to_char, 
                'dims': (self.img_width, self.img_height), 
                'vocab_size': self.vocab_size
            }, f)
        print("✅ meta.pkl salvo com sucesso!")
        # -----------------------------------------------------------------
        
        if os.path.exists(checkpoint_path):
            print(f"🔄 Retomando checkpoint: {checkpoint_path}")
            try:
                self.prediction_model.load_weights(checkpoint_path)
                print("✅ Pesos carregados!")
            except:
                print("⚠️ Erro ao carregar pesos antigos (iniciando do zero).")
        
        class TextMonitor(keras.callbacks.Callback):
            def __init__(self, wrapper): 
                super().__init__()
                self.wrapper = wrapper
            def on_epoch_end(self, epoch, logs=None):
                if (epoch + 1) % 3 != 0 and epoch != 0: return
                print(f"\n--- Check Época {epoch+1} ---")
                total_s, correct_s = 0, 0
                for batch in val_ds.take(1):
                    preds = self.wrapper.prediction_model.predict(batch['image'], verbose=0)
                    decoded = self.wrapper.decode_batch_predictions(preds)
                    real_labels = [self.wrapper.num_to_label(l.numpy()) for l in batch['label']]
                    for i in range(len(decoded)):
                        if decoded[i] == real_labels[i]: correct_s += 1
                        if i < 2: print(f"Pred: {decoded[i]:<5} | Real: {real_labels[i]:<5} | {'✅' if decoded[i]==real_labels[i] else '❌'}")
                    total_s = len(decoded)
                    break
                print(f"📊 Acurácia Batch: {(correct_s/total_s)*100:.1f}%")
                print("-" * 30)

        self.model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=epochs,
            callbacks=[
                keras.callbacks.ReduceLROnPlateau(monitor='val_loss', patience=4, factor=0.5, verbose=1, min_lr=1e-6),
                keras.callbacks.EarlyStopping(monitor='val_loss', patience=12, restore_best_weights=True),
                keras.callbacks.ModelCheckpoint(
                    filepath=checkpoint_path,
                    save_weights_only=True,
                    monitor='val_loss',
                    mode='min',
                    save_best_only=True,
                    verbose=1 
                ),
                TextMonitor(self)
            ]
        )
        
        self.prediction_model.save_weights(final_weights_path)
        print(f"\n✅ Treinamento finalizado. Modelo salvo em: {final_weights_path}")

    def decode_batch_predictions(self, pred):
        input_len = np.ones(pred.shape[0]) * pred.shape[1]
        results = keras.backend.ctc_decode(pred, input_length=input_len, greedy=True)[0][0][:, :self.max_length]
        output_text = []
        for res in results:
            output_text.append(self.num_to_label(res))
        return output_text

if __name__ == "__main__":
    if os.path.basename(os.getcwd()) == "captcha_ml": os.chdir("..")
    
    # Caminho absoluto para garantir que encontra os dados
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "captcha_ml", "data", "processed", "processed_data.npy")
    
    model = CaptchaModel()
    
    if os.path.exists(data_path):
        model.train(data_path, epochs=100, batch_size=32)
    else:
        # Tenta fallback relativo
        if os.path.exists("captcha_ml/data/processed/processed_data.npy"):
            model.train("captcha_ml/data/processed/processed_data.npy", epochs=100, batch_size=32)
        else:
            print(f"❌ Erro: Dados não encontrados em {data_path}")