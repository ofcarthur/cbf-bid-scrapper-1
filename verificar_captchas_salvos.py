#!/usr/bin/env python3
"""
VERIFICAÇÃO DOS CAPTCHAS SALVOS - Testar se as predições estão certas
"""

import os
import glob
from captcha_ml.captcha_solver import CaptchaSolver

def verificar_captchas_salvos():
    """Verifica se os captchas salvos pelo scrapper têm as predições corretas"""
    
    # Carregar solver
    solver = CaptchaSolver()
    if not solver.is_loaded:
        print("❌ Modelo não carregado!")
        return
    
    # Pegar todas as imagens de debug
    debug_files = glob.glob("debug_captchas/*.png")
    
    if not debug_files:
        print("❌ Nenhuma imagem encontrada em debug_captchas/")
        return
    
    print(f"🔍 Encontradas {len(debug_files)} imagens de debug")
    print("="*60)
    
    corretos = 0
    total = 0
    
    for img_path in sorted(debug_files):
        filename = os.path.basename(img_path)
        
        # Extrair o código predito do nome do arquivo
        # Formato: captcha_atleta_729084_tent_1_195858_sbt.png
        if "_" in filename:
            parts = filename.split("_")
            if len(parts) >= 6:
                codigo_esperado = parts[-1].replace(".png", "")
                
                # Testar o modelo nesta imagem
                resultado = solver.solve_captcha_from_file(img_path)
                
                # Verificar se bate
                is_correct = resultado == codigo_esperado
                if is_correct:
                    corretos += 1
                total += 1
                
                status = "✅" if is_correct else "❌"
                print(f"{status} {filename}")
                print(f"    Esperado: '{codigo_esperado}'")
                print(f"    Modelo:   '{resultado}'")
                
                if not is_correct:
                    print(f"    ⚠️ DIVERGÊNCIA! Scrapper salvou como '{codigo_esperado}' mas modelo retorna '{resultado}'")
                print()
            else:
                print(f"⚠️ Formato de arquivo inválido: {filename}")
        else:
            print(f"⚠️ Formato de arquivo inválido: {filename}")
    
    # Resumo
    accuracy = (corretos / total * 100) if total > 0 else 0
    print("="*60)
    print(f"📊 RESULTADO:")
    print(f"   Corretos: {corretos}/{total}")
    print(f"   Acurácia: {accuracy:.1f}%")
    
    if accuracy >= 90:
        print("✅ MODELO ESTÁ FUNCIONANDO CORRETAMENTE!")
        print("   O problema pode estar na validação do servidor CBF.")
    elif accuracy >= 50:
        print("⚠️ MODELO PARCIALMENTE CORRETO")
        print("   Há algumas divergências que precisam ser investigadas.")
    else:
        print("❌ MODELO COM PROBLEMAS")
        print("   Muitas divergências entre predição salva e atual.")

if __name__ == "__main__":
    verificar_captchas_salvos()
