#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo interativo de uso do scrapper do BID da CBF

Este script ajuda você a usar o scrapper, com suporte a resolução automática de captcha.
"""

from scrapper.scrapper import buscar_dados_bid
import webbrowser
import time
import os
import sys

# Verificar se o sistema de ML está disponível
try:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from captcha_ml.captcha_solver import CaptchaSolver
    
    # Tentar carregar o modelo
    solver = CaptchaSolver()
    ML_AVAILABLE = solver.is_loaded
except:
    ML_AVAILABLE = False

def main():
    print("="*70)
    print("  BID CBF - Scrapper Interativo")
    if ML_AVAILABLE:
        print("  🤖 Com resolução automática de captcha!")
    print("="*70)
    print()
    
    # Mostrar status do ML
    if ML_AVAILABLE:
        print("✅ Sistema de ML ativo - captchas serão resolvidos automaticamente")
        
        # Mostrar info do modelo
        info = solver.get_model_info()
        print(f"   Caracteres suportados: {len(info['characters'])} tipos")
        print()
    else:
        print("⚠️  Sistema de ML não disponível - será necessário resolver captcha manualmente")
        print("   💡 Para ativar ML: python3 captcha_pipeline.py collect --num 50")
        print()
    
    # Solicitar dados do usuário
    uf = input("Digite a UF (ex: AL, SP, RJ): ").strip().upper()
    data = input("Digite a data (dd/mm/yyyy, ex: 13/03/2020): ").strip()
    
    # Validação básica
    if len(uf) != 2:
        print("Erro: UF deve ter 2 letras")
        return
    
    if len(data) != 10 or data[2] != '/' or data[5] != '/':
        print("Erro: Data deve estar no formato dd/mm/yyyy")
        return
    
    print()
    print("="*70)
    
    if ML_AVAILABLE:
        print("  EXECUTANDO BUSCA COM ML")
        print("="*70)
        print()
        print("🤖 Tentando buscar dados com resolução automática de captcha...")
        
        try:
            # Tentar busca automática primeiro
            registros = buscar_dados_bid(uf, data, auto_solve=True)
            
            print(f"✅ Sucesso! {len(registros)} registros encontrados")
            print()
            
            # Mostrar resultados
            # Mostrar resultados
            print()
            print("="*70)
            print(f"  RESULTADOS ({len(registros)} registros encontrados)")
            print("="*70)
            print()
            
            if len(registros) == 0:
                print("Nenhum registro encontrado para os filtros especificados.")
                return
            
            # Formato CSV
            print('jogador;operacao;data_publicacao;clube')
            for registro in registros:
                print("{};{};{};{}".format(
                    registro['jogador'],
                    registro['operacao'], 
                    registro['publicacao'],
                    registro['clube']
                ))
            
            # Salvar em arquivo?
            print()
            salvar = input("\nDeseja salvar os resultados em um arquivo? (s/n): ").strip().lower()
            
            if salvar == 's':
                nome_arquivo = f"bid_{uf}_{data.replace('/', '-')}.csv"
                with open(nome_arquivo, 'w', encoding='utf-8') as f:
                    f.write('jogador;operacao;data_publicacao;clube\n')
                    for registro in registros:
                        f.write("{};{};{};{}\n".format(
                            registro['jogador'],
                            registro['operacao'],
                            registro['publicacao'],
                            registro['clube']
                        ))
                print(f"✅ Resultados salvos em {nome_arquivo}")
            return
            
        except Exception as e:
            print(f"❌ Resolução automática falhou: {e}")
            print("🔄 Tentando modo manual...")
            print()
    
    # Modo manual (fallback)
    print("  INSTRUÇÕES PARA OBTER O CAPTCHA")
    print("="*70)
    print()
    print("1. Vou abrir o site do BID no seu navegador")
    print("2. Preencha:")
    print(f"   - Data: {data}")
    print(f"   - UF: {uf}")
    print("3. Clique no botão de busca")
    print("4. Um captcha aparecerá - anote o código")
    print("5. Volte aqui e digite o código do captcha")
    print()
    
    resposta = input("Pressione ENTER para abrir o navegador (ou 'n' para cancelar): ").strip()
    
    if resposta.lower() == 'n':
        print("Operação cancelada.")
        return
    
    # Abrir o site
    print("\nAbrindo https://bid.cbf.com.br/ no navegador...")
    webbrowser.open('https://bid.cbf.com.br/')
    
    print()
    captcha = input("Digite o código do CAPTCHA (em maiúsculas): ").strip().upper()
    
    if not captcha:
        print("Erro: Captcha não pode estar vazio")
        return
    
    print()
    print("Buscando dados...")
    print()
    
    try:
        # Buscar os dados
        registros = buscar_dados_bid(uf, data, captcha_code=captcha)
        
        # Exibir resultados
        print()
        print("="*70)
        print(f"  RESULTADOS ({len(registros)} registros encontrados)")
        print("="*70)
        print()
        
        if len(registros) == 0:
            print("Nenhum registro encontrado para os filtros especificados.")
            return
        
        # Formato CSV
        print('jogador;operacao;data_publicacao;clube')
        for registro in registros:
            print("{};{};{};{}".format(
                registro['jogador'],
                registro['operacao'],
                registro['publicacao'],
                registro['clube']
            ))
        
        # Salvar em arquivo?
        print()
        salvar = input("\nDeseja salvar os resultados em um arquivo? (s/n): ").strip().lower()
        
        if salvar == 's':
            nome_arquivo = f"bid_{uf}_{data.replace('/', '-')}.csv"
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write('jogador;operacao;data_publicacao;clube\n')
                for registro in registros:
                    f.write("{};{};{};{}\n".format(
                        registro['jogador'],
                        registro['operacao'],
                        registro['publicacao'],
                        registro['clube']
                    ))
            print(f"\nArquivo salvo: {nome_arquivo}")
    
    except Exception as e:
        print()
        print("="*70)
        print("  ERRO")
        print("="*70)
        print(f"\n{str(e)}\n")
        print("Possíveis causas:")
        print("- Captcha incorreto")
        print("- Sessão expirada")
        print("- Data no formato errado")
        print("- Problemas de conexão")
        print()

if __name__ == '__main__':
    main()

