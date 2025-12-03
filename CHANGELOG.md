# Changelog

## [2.0.0] - 2024-10-18

### 🔄 Mudanças Importantes

O site do BID da CBF foi completamente reformulado. Esta versão atualiza o scrapper para funcionar com a nova estrutura.

### ✨ Novas Funcionalidades

- Suporte ao novo endpoint da API (`/busca-json`)
- Extração automática do token CSRF
- Gerenciamento de sessão com cookies
- Script interativo (`exemplo_interativo.py`) que guia o usuário no processo
- Campos adicionais nos dados retornados (apelido, código do atleta, etc.)
- Mensagens de erro mais descritivas

### 🚨 Breaking Changes

- **CAPTCHA Obrigatório**: O scrapper agora requer que o usuário resolva um captcha manualmente
- **Assinatura da função alterada**: `buscar_dados_bid()` agora aceita um terceiro parâmetro `captcha_code`
- **Formato de retorno expandido**: Novos campos disponíveis nos registros

### 🔧 Correções

- Corrigido erro 404 ao usar o endpoint antigo
- Atualizado para usar o novo formato JSON de resposta (antes era HTML dentro do JSON)
- Corrigido cabeçalhos HTTP para compatibilidade com o novo site

### 📚 Documentação

- README atualizado com instruções detalhadas
- Adicionado FAQ sobre o captcha
- Documentação dos campos retornados
- Exemplos de uso atualizados

### 🗑️ Removido

- Endpoint antigo (`/a/bid/carregar/json/`) não é mais usado
- Parsing de HTML removido (agora usa JSON direto)

---

## [1.0.0] - Versão Original

### ✨ Funcionalidades Iniciais

- Busca de dados do BID por UF e data
- Parsing de HTML dos resultados
- Exportação em formato CSV

### 📌 Nota

Esta versão funcionava com o site antigo do BID que não requeria captcha.

