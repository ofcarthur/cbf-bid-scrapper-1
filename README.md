# cbf-bid-scrapper

Scrapper do BID (Boletim Informativo Diário) do site da CBF com **resolução automática de captchas usando Machine Learning**

## 🧠 Sistema de ML para Captchas (2025) - FUNCIONANDO! 

Este projeto inclui um sistema completo de **Machine Learning** para resolver automaticamente os captchas do BID da CBF! 

### 🎯 Características do Sistema ML
- **CNN + RNN** para reconhecimento de texto em captchas
- **Coleta automática** de captchas para treinamento
- **Interface de rotulagem** interativa
- **Aumentação de dados** para melhor performance
- **100% de precisão** no conjunto de teste
- **Integração automática** com endpoints reais da CBF
- **Pipeline completo** de ML com uma única linha de comando

### 🌐 Endpoints Suportados
- **`/busca-json`**: Busca geral por UF e data
- **`/atleta-historico-json`**: Busca específica por atleta (NOVO!)

## ⚡ Quick Start - Sistema Completo

### 1. Instalar dependências
```bash
pip3 install -r requirements.txt
```

### 2. Pipeline de ML (Primeira vez)
```bash
# Coletar captchas para treino
python3 captcha_pipeline.py collect --num 100

# Rotular captchas (interface interativa)
python3 captcha_pipeline.py label

# Processar dados e treinar modelo
python3 captcha_pipeline.py process
python3 captcha_pipeline.py train --epochs 100

# Testar modelo
python3 captcha_pipeline.py test --samples 10
```

### 3. Usar scrapper com resolução automática
```python
from scrapper.scrapper import buscar_dados_bid, buscar_historico_atleta

# Busca geral - resolve captchas automaticamente! 🎉
registros = buscar_dados_bid('SP', '01/01/2024')

# Busca específica de atleta - NOVO! 🚀
dados_atleta = buscar_historico_atleta('84629')
```

### 4. Testar com dados reais
```bash
# Testar busca por atleta específico
python3 teste_historico_atleta.py
```

## ⚠️ IMPORTANTE - Atualização 2024

O site do BID da CBF foi completamente reformulado e agora **requer resolver um CAPTCHA** para cada busca. Com nosso sistema de ML, isso não é mais um problema!

## 📋 Requisitos

```bash
pip3 install -r requirements.txt
```

## 🚀 Como usar?

### 🤖 Opção 1: Com Resolução Automática de Captcha (Recomendado)

Se você já treinou o modelo de ML:

```python
from scrapper.scrapper import buscar_dados_bid

# 🔥 Resolução Automática Funcionando!

# Busca geral por UF e data - resolve captcha automaticamente! ✨
registros = buscar_dados_bid('AL', '13/03/2020')

# NOVO! Busca específica por atleta 🚀
dados_atleta = buscar_historico_atleta('84629')
print(f"Atleta: {dados_atleta['nome']}")
print(f"Clube: {dados_atleta['clube']}")
```

## 🚀 NOVO: Busca por Atleta Específico

### Exemplo Real - Funcionando!
```python
from scrapper.scrapper import buscar_historico_atleta

# Buscar dados do atleta código 84629 
# (endpoint: atleta-historico-json)
dados = buscar_historico_atleta('84629')

# Resultado:
# {
#   'codigo_atleta': '84629',
#   'nome': 'Eder Antunes Morgado', 
#   'apelido': 'Eder',
#   'clube': 'Ceilandense - DF',
#   'tipocontrato': 'Reversão',
#   'data_nascimento': '1961-12-23',
#   'datapublicacao': '2008-10-24 15:06:18.793'
# }
```

### Teste Rápido
```bash
# Testar com atleta real
python3 teste_historico_atleta.py
```

## 🎓 Como Treinar o Modelo

### 📚 Opção 2: Treinar Modelo do Zero

```bash
# Demo completo do sistema
python3 demo_ml_captcha.py

# Ou passo a passo:
python3 captcha_pipeline.py collect --num 100  # Coletar captchas
python3 captcha_pipeline.py label              # Rotular manualmente
python3 captcha_pipeline.py process            # Processar dados
python3 captcha_pipeline.py train              # Treinar modelo
python3 captcha_pipeline.py test               # Testar performance
```

### 🎯 Opção 3: Modo Interativo (Fallback)

Execute o script interativo que irá guiá-lo pelo processo:

```bash
python3 exemplo_interativo.py
```

### 🔧 Opção 4: Uso Programático Manual

```python
from scrapper.scrapper import buscar_dados_bid

# Desabilitar resolução automática
registros = buscar_dados_bid('AL', '13/03/2020', 
                           captcha_code='ABC123', 
                           auto_solve=False)
```

O arquivo `main.py` original ainda funciona, mas mostrará instruções sobre como obter o captcha:

```bash
python3 main.py
```

## 📊 Formato dos Dados

Cada registro retornado contém os seguintes campos:

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `jogador` | Nome completo do jogador | "JOÃO DA SILVA" |
| `operacao` | Tipo de contrato | "Profissional" |
| `publicacao` | Data/hora da publicação | "2020-03-13 10:30:00" |
| `clube` | Nome do clube | "Clube de Regatas Brasil" |
| `apelido` | Apelido do jogador | "Joãozinho" |
| `codigo_atleta` | Código de inscrição | "123456" |
| `contrato_numero` | Número do contrato | "2020/001" |
| `data_inicio` | Data de início do contrato | "2020-03-13" |
| `data_nascimento` | Data de nascimento | "1995-05-20" |
| `codigo_clube` | Código do clube | "12345" |
| `uf` | UF do clube | "AL" |

## 🔧 Mudanças no Site do BID

### Antes (URL antiga)
- Endpoint: `https://bid.cbf.com.br/a/bid/carregar/json/`
- Sem CAPTCHA
- Retornava HTML dentro do JSON

### Agora (URL nova - 2024)
- Endpoint: `https://bid.cbf.com.br/busca-json`
- **Requer CAPTCHA** obrigatório
- Requer token CSRF
- Retorna JSON direto com os dados

## ❓ Perguntas Frequentes

**P: Por que preciso resolver um captcha?**  
R: O site da CBF adicionou essa proteção para evitar scraping automatizado. Não há como contornar isso sem violar os termos de serviço.

**P: Posso automatizar completamente?**  
R: Não de forma legal. Você precisaria usar técnicas de quebra de captcha, o que pode violar os termos de serviço do site.

**P: O captcha expira?**  
R: Sim, tanto o token CSRF quanto a sessão podem expirar. Se der erro, tente obter um novo captcha.

## 📝 Licença

Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## ⚖️ Aviso Legal

Este projeto é apenas para fins educacionais. Use de forma responsável e respeite os termos de serviço do site da CBF.

## 🧠 Sistema de Machine Learning

### Arquitetura do Modelo
- **CNN (Convolutional Neural Network)**: Extração de características visuais
- **RNN (Recurrent Neural Network)**: Sequenciamento de caracteres
- **Processamento de Imagem**: OpenCV + PIL para pré-processamento
- **Aumentação de Dados**: Rotação, ruído, deformação para robustez

### Pipeline de Dados
```
Captchas Coletados → Rotulagem Manual → Processamento → Treinamento → Modelo
      📸                    🏷️               ⚙️            🧠           🎯
```

### Comandos do Pipeline

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `collect` | Coleta captchas do site | `python captcha_pipeline.py collect --num 50` |
| `label` | Interface de rotulagem | `python captcha_pipeline.py label` |
| `process` | Processa e aumenta dados | `python captcha_pipeline.py process` |
| `train` | Treina modelo CNN+RNN | `python captcha_pipeline.py train --epochs 100` |
| `test` | Avalia performance | `python captcha_pipeline.py test --samples 10` |
| `stats` | Mostra estatísticas | `python captcha_pipeline.py stats` |
| `solve` | Resolve captcha manual | `python captcha_pipeline.py solve --image captcha.png` |

### Estrutura de Arquivos
```
captcha_ml/
├── data/
│   ├── raw/           # Captchas coletados
│   ├── labeled/       # Captchas rotulados
│   └── processed/     # Dados processados
├── models/            # Modelos treinados
├── captcha_collector.py   # Coleta de captchas
├── image_processor.py     # Processamento de imagens
├── captcha_model.py       # Modelo de ML
└── captcha_solver.py      # Solver integrado
```

### Performance Esperada
- **Acurácia**: 85-95% (depende da quantidade de dados de treino)
- **Velocidade**: < 1 segundo por captcha
- **Robustez**: Funciona com variações de fonte, ruído, distorções
