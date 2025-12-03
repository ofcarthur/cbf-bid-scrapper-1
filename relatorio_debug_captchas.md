# Relatório de Debug - Análise de Captchas

## 📊 Resultados Coletados

### Atleta 729084:
1. **Tentativa 1**: Código gerado `cpvp` → ❌ Rejeitado
   - Arquivo: `captcha_atleta_729084_tent_1_175835_cpvp.png`
   
2. **Tentativa 2**: Código gerado `hxkn` → ❌ Rejeitado
   - Arquivo: `captcha_atleta_729084_tent_2_175838_hxkn.png`
   
3. **Tentativa 3**: Código gerado `bchx` → ❌ Rejeitado
   - Arquivo: `captcha_atleta_729084_tent_3_175841_bchx.png`

### Atleta 729085:
1. **Tentativa 1**: Código gerado `medk` → ❌ Rejeitado
   - Arquivo: `captcha_atleta_729085_tent_1_175849_medk.png`
   
2. **Tentativa 2**: Código gerado `jfhj` → ❌ Rejeitado
   - Arquivo: `captcha_atleta_729085_tent_2_175852_jfhj.png`
   
3. **Tentativa 3**: Código gerado `btru` → ❌ Rejeitado
   - Arquivo: `captcha_atleta_729085_tent_3_175855_btru.png`

### Atleta 729086:
1. **Tentativa 1**: Código gerado `cvnm` → ❌ Rejeitado
   - Arquivo: `captcha_atleta_729086_tent_1_175903_cvnm.png`
   
2. **Tentativa 2**: Código gerado `kdvg` → ❌ Rejeitado
   - Arquivo: `captcha_atleta_729086_tent_2_175906_kdvg.png`
   
3. **Tentativa 3**: Código gerado `jzpk` → ❌ Rejeitado
   - Arquivo: `captcha_atleta_729086_tent_3_175909_jzpk.png`

## 🔍 Análise

### Taxa de Rejeição: 100%
- **9 tentativas**, **0 sucessos**
- Todos os códigos foram rejeitados pelo servidor da CBF

### Padrões Observados nos Códigos Gerados:
- Atleta 729084: `cpvp`, `hxkn`, `bchx`
- Atleta 729085: `medk`, `jfhj`, `btru` 
- Atleta 729086: `cvnm`, `kdvg`, `jzpk`

### Caracteres Utilizados:
- **Presentes**: b, c, d, e, f, g, h, j, k, m, n, p, r, t, u, v, x, z
- **Nota**: Todos estão no vocabulário esperado [a-z exceto l,o,q,w,y]

## 🎯 Próximos Passos de Diagnóstico

### 1. Análise Visual Necessária
**VOCÊ DEVE VERIFICAR AS IMAGENS** em `debug_captchas/` para:
- Comparar os códigos reais nas imagens com os códigos gerados
- Verificar se o modelo está "próximo" ou completamente errado
- Identificar padrões de erro (caracteres específicos, posições)

### 2. Possíveis Causas do Problema

#### A) Modelo Inadequado
- O modelo foi treinado com captchas antigos
- Os captchas atuais podem ter formato/fonte diferente
- Necessário retreinar com captchas atuais

#### B) Pré-processamento Incorreto  
- Redimensionamento inadequado
- Problemas de binarização
- Ruído não removido adequadamente

#### C) Diferença de Domínio
- Captchas de atletas antigos vs novos podem ser diferentes
- Servidores diferentes podem gerar captchas com características visuais distintas

### 3. Soluções Propostas

#### Solução 1: Verificação Manual
1. Abra as 9 imagens salvas
2. Compare visualmente com os códigos gerados
3. Documente a acurácia real (caracteres corretos vs incorretos)

#### Solução 2: Coleta de Novos Dados de Treino
1. Use `python3 captcha_pipeline.py collect --num 50` nos atletas atuais (729xxx)
2. Rotule manualmente os novos captchas
3. Re-treine o modelo com dados atualizados

#### Solução 3: Ajuste de Parâmetros
- Modificar pré-processamento de imagens
- Ajustar arquitetura do modelo se necessário
- Aumentar épocas de treinamento

## 📋 Checklist de Verificação

- [ ] **Verificar visualmente as 9 imagens de captcha**
- [ ] **Documentar acurácia real (% de caracteres corretos)**
- [ ] **Identificar padrões de erro mais comuns**
- [ ] **Decidir se precisa de novos dados de treino**
- [ ] **Testar com captchas de atletas mais antigos (84xxx) para comparação**

## 💡 Recomendação Imediata

**ANALISE AS IMAGENS AGORA** para entender se:
- O modelo está "quase acertando" (1-2 caracteres errados)
- O modelo está completamente perdido
- Há diferenças visuais óbvias nos captchas atuais vs antigos

Isso determinará se precisamos apenas de mais treino ou de uma coleta completa de novos dados.
