#!/usr/bin/env python3
"""
Demo completo do CBF BID Scrapper com ML

Este script demonstra todas as funcionalidades do scrapper:
1. Busca geral por UF e data (endpoint busca-json)
2. Busca específica por atleta (endpoint atleta-historico-json)
3. Resolução automática de captcha com Machine Learning

Ambos os endpoints funcionam com o mesmo modelo ML treinado!
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapper.scrapper import buscar_dados_bid, buscar_historico_atleta

def demo_busca_geral():
    """Demonstra busca geral por UF e data"""
    print("="*80)
    print("🔍 DEMO 1: BUSCA GERAL POR UF E DATA")
    print("="*80)
    print("📅 Endpoint: /busca-json")
    print("🎯 Buscando: Alagoas (AL), 13/03/2020")
    print("🤖 Resolução automática de captcha: ATIVADA")
    print("-"*80)
    
    try:
        registros = buscar_dados_bid('AL', '13/03/2020', auto_solve=True)
        
        print(f"✅ SUCESSO! {len(registros)} registros encontrados")
        
        # Mostrar alguns registros como exemplo
        if registros:
            print("\n📋 Primeiros registros:")
            for i, registro in enumerate(registros[:3], 1):
                print(f"\n--- Registro {i} ---")
                print(f"  Jogador: {registro.get('jogador', 'N/A')}")
                print(f"  Clube: {registro.get('clube', 'N/A')}")
                print(f"  Operação: {registro.get('operacao', 'N/A')}")
                print(f"  Publicação: {registro.get('publicacao', 'N/A')}")
            
            if len(registros) > 3:
                print(f"\n... e mais {len(registros) - 3} registros")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

def demo_busca_atleta():
    """Demonstra busca específica por atleta"""
    print("\n" + "="*80)
    print("🏆 DEMO 2: BUSCA ESPECÍFICA POR ATLETA")
    print("="*80)
    print("📊 Endpoint: /atleta-historico-json")
    print("🎯 Buscando: Atleta código 84629")
    print("🤖 Resolução automática de captcha: ATIVADA")
    print("-"*80)
    
    try:
        dados_atleta = buscar_historico_atleta('84629', auto_solve=True)
        
        print("✅ SUCESSO! Dados do atleta obtidos")
        print("\n👤 Informações do Atleta:")
        print("-"*40)
        
        if isinstance(dados_atleta, dict):
            campos_importantes = [
                ('nome', 'Nome'),
                ('apelido', 'Apelido'), 
                ('codigo_atleta', 'Código'),
                ('clube', 'Clube'),
                ('tipocontrato', 'Tipo de Contrato'),
                ('data_nascimento', 'Data de Nascimento'),
                ('datapublicacao', 'Data de Publicação')
            ]
            
            for key, label in campos_importantes:
                valor = dados_atleta.get(key, 'N/A')
                print(f"  {label}: {valor}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

def main():
    """Executar demonstração completa"""
    print("🏆 CBF BID SCRAPPER - DEMONSTRAÇÃO COMPLETA")
    print("🤖 Sistema de Machine Learning para Captchas")
    print("🌐 Testando com endpoints reais da CBF")
    
    # Demo 1: Busca geral
    success1 = demo_busca_geral()
    
    # Demo 2: Busca específica por atleta
    success2 = demo_busca_atleta()
    
    # Resultado final
    print("\n" + "="*80)
    print("📊 RESUMO DOS TESTES")
    print("="*80)
    
    resultados = []
    resultados.append(f"🔍 Busca Geral (UF/Data): {'✅ SUCESSO' if success1 else '❌ FALHOU'}")
    resultados.append(f"🏆 Busca por Atleta: {'✅ SUCESSO' if success2 else '❌ FALHOU'}")
    
    for resultado in resultados:
        print(resultado)
    
    if success1 and success2:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ O sistema está funcionando perfeitamente")
        print("🤖 Resolução automática de captcha operacional")
        print("🌐 Integração com endpoints reais da CBF confirmada")
    else:
        print("\n⚠️  Alguns testes falharam")
        print("💡 Verifique se o modelo ML está treinado:")
        print("   python3 captcha_pipeline.py train")
    
    print("="*80)

if __name__ == "__main__":
    main()
