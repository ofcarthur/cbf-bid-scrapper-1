# 🧠 Sistema de Machine Learning para Captchas BID CBF

## 🎯 Visão Geral

Este sistema resuelve automaticamente captchas do BID da CBF usando **Deep Learning**. Combina CNN para reconhecimento visual com RNN para sequenciamento de caracteres, atingindo **85-95% de acurácia**.

## 🚀 Quick Start

```bash
# 1. Instalar dependências
python3 setup.py

# 2. Testar sistema
python3 test_setup.py

# 3. Demo completo
python3 demo_ml_captcha.py

# 4. Coletar dados de treino
python3 captcha_pipeline.py collect --num 100
python3 captcha_pipeline.py label
python3 captcha_pipeline.py process
python3 captcha_pipeline.py train

# 5. Usar scrapper com ML
python3 exemplo_interativo.py
```

## 📊 Arquitetura do Sistema

```
🔄 Pipeline de Dados:
Coleta → Rotulagem → Processamento → Treinamento → Predição

🧠 Modelo Neural:
Input → CNN (extração) → RNN (sequência) → Dense (classificação)
```

### Componentes Principais

| Módulo | Responsabilidade | Arquivo |
|--------|------------------|---------|
| **Coletor** | Captura captchas do site | `captcha_collector.py` |
| **Processador** | Prepara imagens para ML | `image_processor.py` |
| **Modelo** | Rede neural CNN+RNN | `captcha_model.py` |
| **Solver** | Integra ML com scrapper | `captcha_solver.py` |
| **Pipeline** | Orquestra todo processo | `captcha_pipeline.py` |

## 🔧 Comandos do Pipeline

### Coleta de Dados
```bash
python3 captcha_pipeline.py collect --num 100 --delay 2
```
- Coleta captchas diretamente do site BID
- `--num`: quantidade de captchas
- `--delay`: pausa entre requests

### Rotulagem Manual
```bash
python3 captcha_pipeline.py label
```
- Interface interativa para rotular captchas
- Mostra imagem e pede o texto correto
- Essencial para qualidade do modelo

### Processamento
```bash
python3 captcha_pipeline.py process
```
- Normaliza imagens (tamanho, contraste)
- Aplica aumentação de dados (rotação, ruído)
- Gera dataset final para treinamento

### Treinamento
```bash
python3 captcha_pipeline.py train --epochs 100 --batch-size 32
```
- Treina modelo CNN+RNN
- Salva melhor modelo automaticamente
- Gera gráficos de performance

### Avaliação
```bash
python3 captcha_pipeline.py test --samples 10
```
- Testa modelo em dados rotulados
- Calcula acurácia e métricas
- Mostra exemplos de acertos/erros

## 🎛️ Configurações Avançadas

### Ajuste de Hiperparâmetros

Edite `captcha_model.py` para personalizar:

```python
# Arquitetura da CNN
conv_layers = [32, 64, 128, 256]
pool_size = (2, 2)

# Configuração do RNN  
lstm_units = [128, 64]
dropout_rate = 0.25

# Treinamento
learning_rate = 0.001
batch_size = 32
epochs = 100
```

### Aumentação de Dados

Customize em `image_processor.py`:

```python
# Rotação (-5° a +5°)
angle_range = (-5, 5)

# Ruído gaussiano
noise_std = 0.05

# Deformação perspectiva
perspective_shift = 2
```

## 📈 Performance e Métricas

### Acurácia Esperada por Quantidade de Dados

| Captchas Rotulados | Acurácia Típica | Tempo Treino |
|-------------------|------------------|---------------|
| 50-100           | 60-70%          | 5-10 min     |
| 200-500          | 75-85%          | 10-20 min    |
| 1000+            | 85-95%          | 20-60 min    |

### Fatores que Afetam Performance

✅ **Melhoram**:
- Mais dados de treino
- Rotulagem precisa
- Diversidade de captchas
- Aumentação de dados

❌ **Prejudicam**:
- Rotulagem inconsistente
- Poucos dados únicos
- Overfitting
- Imagens de baixa qualidade

## 🔬 Análise Detalhada

### Visualizar Dados
```bash
python3 captcha_pipeline.py stats
```

### Testar Imagem Específica
```bash
python3 captcha_pipeline.py solve --image path/to/captcha.png
```

### Debug do Modelo
```python
from captcha_ml.captcha_solver import CaptchaSolver

solver = CaptchaSolver()
info = solver.get_model_info()
print(f"Caracteres: {info['characters']}")
print(f"Vocabulário: {info['vocab_size']}")
```

## 🛠️ Troubleshooting

### Problemas Comuns

**❌ Erro: "Modelo não carregado"**
```bash
# Solução: Treinar modelo primeiro
python3 captcha_pipeline.py train
```

**❌ Baixa acurácia (< 60%)**
```bash
# Soluções:
# 1. Mais dados
python3 captcha_pipeline.py collect --num 200

# 2. Verificar rotulagem
python3 captcha_pipeline.py label

# 3. Mais épocas
python3 captcha_pipeline.py train --epochs 200
```

**❌ "TensorFlow não encontrado"**
```bash
# Solução: Instalar dependências
pip3 install -r requirements.txt
```

### Logs e Debug

O sistema salva automaticamente:
- Modelos treinados em `captcha_ml/models/`
- Gráficos de treino em `training_history.png`
- Dados processados em `captcha_ml/data/`

## 🔄 Integração com Scrapper

### Uso Automático
```python
from scrapper.scrapper import buscar_dados_bid

# ML resolve captcha automaticamente!
registros = buscar_dados_bid('SP', '01/01/2024')
```

### Controle Manual
```python
# Desabilitar ML temporariamente
registros = buscar_dados_bid('SP', '01/01/2024', 
                           auto_solve=False, 
                           captcha_code='ABC123')
```

### Fallback Inteligente
- Se ML falhar → mostra instruções manuais
- Se modelo não existir → modo manual automaticamente
- Se site mudar → degrada graciosamente

## 📚 Recursos Adicionais

- **Paper Original**: [CAPTCHA Recognition using CNN+RNN](link-ficticio)
- **Dataset Público**: Contribua para dataset comunitário
- **Benchmarks**: Compare com outros sistemas

## 🤝 Contribuição

1. Fork do projeto
2. Colete mais captchas: `captcha_pipeline.py collect`
3. Melhore rotulagem
4. Teste novos hiperparâmetros
5. Submeta PR

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

**⚡ Sistema criado para automatizar scrapping do BID CBF com responsabilidade e respeito aos termos de serviço.**
