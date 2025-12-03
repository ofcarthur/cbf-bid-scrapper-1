#!/usr/bin/env python3
"""
Exemplo de uso do sistema de ML para captchas do BID CBF

Este script demonstra como usar o sistema completo de machine learning
para resolver captchas automaticamente no scrapper do BID CBF.
"""

import sys
import os
from datetime import datetime, timedelta

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapper.scrapper import buscar_dados_bid
from captcha_ml.captcha_solver import CaptchaSolver

def demo_scrapper_com_ml():
    """
    Demonstra o uso do scrapper com resolução automática de captcha
    """
    print("=== DEMO: SCRAPPER BID CBF COM ML ===")
    print()
    
    # Verificar se o modelo está disponível
    solver = CaptchaSolver()
    
    if solver.is_loaded:
        print("✅ Modelo de ML carregado com sucesso!")
        
        # Mostrar informações do modelo
        info = solver.get_model_info()
        print(f"   Caracteres suportados: {info['characters']}")
        print(f"   Acurácia esperada: Ver resultados de teste")
        print()
        
        # Exemplo de busca com resolução automática
        print("🔍 Testando busca com resolução automática de captcha...")
        print("   Estado: AL (Alagoas)")
        print("   Data: 13/03/2020")
        
        try:
            # Buscar dados com auto_solve=True (padrão)
            registros = buscar_dados_bid('AL', '13/03/2020', auto_solve=True)
            
            print(f"✅ Busca concluída! {len(registros)} registros encontrados")
            
            # Mostrar alguns exemplos
            if registros:
                print("\n📋 Primeiros registros encontrados:")
                for i, registro in enumerate(registros[:3]):
                    print(f"   {i+1}. {registro['jogador']} - {registro['clube']} ({registro['operacao']})")
                
                if len(registros) > 3:
                    print(f"   ... e mais {len(registros) - 3} registros")
            
        except Exception as e:
            print(f"❌ Erro na busca: {e}")
            print("\n💡 Possíveis soluções:")
            print("   1. Verificar conexão com internet")
            print("   2. Tentar novamente (o site pode estar instável)")
            print("   3. Usar captcha_code manual se a resolução automática falhar")
    
    else:
        print("❌ Modelo de ML não está disponível")
        print("\n📚 Para ativar a resolução automática de captcha:")
        print("   1. python captcha_pipeline.py collect --num 100")
        print("   2. python captcha_pipeline.py label")
        print("   3. python captcha_pipeline.py process")
        print("   4. python captcha_pipeline.py train --epochs 100")
        print()
        
        # Demonstrar uso manual
        print("🔍 Demonstrando uso com captcha manual...")
        print("   (Esta operação falhará, mas mostra como usar)")
        
        try:
            registros = buscar_dados_bid('AL', '13/03/2020', auto_solve=False)
        except Exception as e:
            print(f"❌ Como esperado, falhou: {e}")

def demo_comparacao_performance():
    """
    Compara a performance do modelo com dados de teste
    """
    print("\n=== DEMO: PERFORMANCE DO MODELO ===")
    
    solver = CaptchaSolver()
    
    if not solver.is_loaded:
        print("❌ Modelo não disponível para teste")
        return
    
    print("🧪 Testando modelo em amostras rotuladas...")
    
    # Testar o modelo
    results = solver.test_on_samples(num_samples=10)
    
    if results:
        print(f"\n📊 Resultados da avaliação:")
        print(f"   Acurácia: {results['accuracy']:.2%}")
        print(f"   Corretos: {results['correct']}/{results['total']}")
        
        # Análise detalhada
        if results['accuracy'] >= 0.9:
            print("   🎉 Excelente! Modelo muito confiável")
        elif results['accuracy'] >= 0.8:
            print("   ✅ Bom! Modelo confiável para uso")
        elif results['accuracy'] >= 0.6:
            print("   ⚠️  Moderado. Pode precisar de mais dados de treino")
        else:
            print("   ❌ Baixo. Recomenda-se retreinar com mais dados")
        
        # Mostrar exemplos de erros
        errors = [r for r in results['results'] if not r['correct']]
        if errors:
            print(f"\n❌ Exemplos de erros ({len(errors)} total):")
            for error in errors[:3]:
                print(f"   '{error['true_label']}' → '{error['predicted_label']}'")

def demo_pipeline_completo():
    """
    Demonstra o pipeline completo desde a coleta até o uso
    """
    print("\n=== DEMO: PIPELINE COMPLETO ===")
    print()
    print("Este é o fluxo completo para criar um sistema de resolução automática:")
    print()
    
    print("1️⃣  COLETA DE DADOS")
    print("   python captcha_pipeline.py collect --num 50")
    print("   └─ Coleta 50 captchas do site BID CBF")
    print()
    
    print("2️⃣  ROTULAGEM MANUAL")
    print("   python captcha_pipeline.py label")
    print("   └─ Interface interativa para rotular cada captcha")
    print()
    
    print("3️⃣  PROCESSAMENTO")
    print("   python captcha_pipeline.py process")
    print("   └─ Preprocessa imagens e aplica aumentação de dados")
    print()
    
    print("4️⃣  TREINAMENTO")
    print("   python captcha_pipeline.py train --epochs 100")
    print("   └─ Treina modelo CNN+RNN por 100 épocas")
    print()
    
    print("5️⃣  AVALIAÇÃO")
    print("   python captcha_pipeline.py test --samples 10")
    print("   └─ Testa modelo em amostras de validação")
    print()
    
    print("6️⃣  USO AUTOMÁTICO")
    print("   from scrapper.scrapper import buscar_dados_bid")
    print("   registros = buscar_dados_bid('SP', '01/01/2024')")
    print("   └─ Captcha resolvido automaticamente!")
    print()
    
    # Verificar status atual
    print("📋 STATUS ATUAL DO SISTEMA:")
    
    # Verificar dados coletados
    raw_dir = "captcha_ml/data/raw"
    labeled_dir = "captcha_ml/data/labeled"
    processed_file = "captcha_ml/data/processed/processed_data.npy"
    model_file = "captcha_ml/models/best_model.h5"
    
    if os.path.exists(raw_dir):
        raw_count = len([f for f in os.listdir(raw_dir) if f.endswith('.png')])
        print(f"   📥 Captchas coletados: {raw_count}")
    else:
        print("   📥 Captchas coletados: 0")
    
    if os.path.exists(labeled_dir):
        labeled_count = len([f for f in os.listdir(labeled_dir) if f.endswith('.png')])
        print(f"   🏷️  Captchas rotulados: {labeled_count}")
    else:
        print("   🏷️  Captchas rotulados: 0")
    
    if os.path.exists(processed_file):
        print("   ⚙️  Dados processados: ✅")
    else:
        print("   ⚙️  Dados processados: ❌")
    
    if os.path.exists(model_file):
        print("   🧠 Modelo treinado: ✅")
        
        # Testar modelo se disponível
        solver = CaptchaSolver()
        if solver.is_loaded:
            print("   🚀 Status: PRONTO PARA USO!")
        else:
            print("   ⚠️  Status: Modelo existe mas falhou ao carregar")
    else:
        print("   🧠 Modelo treinado: ❌")
        print("   📊 Status: NECESSÁRIO TREINAMENTO")

def main():
    print("🎯 SISTEMA DE ML PARA CAPTCHAS BID CBF")
    print("=" * 50)
    
    # Demo básico
    demo_scrapper_com_ml()
    
    # Demo de performance
    demo_comparacao_performance()
    
    # Demo do pipeline
    demo_pipeline_completo()
    
    print("\n" + "=" * 50)
    print("💡 Para começar a usar:")
    print("   1. Execute: python captcha_pipeline.py collect --num 50")
    print("   2. Siga as instruções para rotular e treinar")
    print("   3. Use o scrapper normalmente - captchas serão resolvidos automaticamente!")

if __name__ == "__main__":
    main()
