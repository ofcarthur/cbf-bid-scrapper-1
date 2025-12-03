#!/usr/bin/env python3
"""
Script de instalação e configuração do sistema de ML para captchas BID CBF
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ é necessário")
        print(f"   Versão atual: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def install_dependencies():
    """Instala as dependências do projeto"""
    print("📦 Instalando dependências...")
    
    try:
        # Atualizar pip
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        
        # Instalar dependências do requirements.txt
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        
        print("✅ Dependências instaladas com sucesso!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro instalando dependências: {e}")
        return False

def create_directories():
    """Cria a estrutura de diretórios necessária"""
    print("📁 Criando estrutura de diretórios...")
    
    dirs = [
        'captcha_ml',
        'captcha_ml/data',
        'captcha_ml/data/raw',
        'captcha_ml/data/labeled', 
        'captcha_ml/data/processed',
        'captcha_ml/models'
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"   📂 {dir_path}")
    
    print("✅ Diretórios criados!")

def check_system_requirements():
    """Verifica requisitos do sistema"""
    print("🔍 Verificando requisitos do sistema...")
    
    # Verificar sistema operacional
    os_name = platform.system()
    print(f"   OS: {os_name}")
    
    # Verificar se é macOS (por causa do OpenCV)
    if os_name == "Darwin":
        print("   🍎 macOS detectado - pode precisar de dependências adicionais")
        print("   💡 Se houver problemas com OpenCV, execute: brew install opencv")
    
    # Verificar RAM disponível (aproximadamente)
    try:
        import psutil
        ram_gb = psutil.virtual_memory().total / (1024**3)
        print(f"   💾 RAM: {ram_gb:.1f}GB")
        
        if ram_gb < 4:
            print("   ⚠️  RAM baixa - treinamento pode ser lento")
        else:
            print("   ✅ RAM suficiente")
            
    except ImportError:
        print("   ❓ Não foi possível verificar RAM (psutil não instalado)")
    
    return True

def test_installation():
    """Testa se a instalação funcionou"""
    print("🧪 Testando instalação...")
    
    # Testar imports principais
    try:
        import tensorflow as tf
        print(f"   ✅ TensorFlow {tf.__version__}")
    except ImportError as e:
        print(f"   ❌ TensorFlow: {e}")
        return False
    
    try:
        import cv2
        print(f"   ✅ OpenCV {cv2.__version__}")
    except ImportError as e:
        print(f"   ❌ OpenCV: {e}")
        return False
    
    try:
        import numpy as np
        print(f"   ✅ NumPy {np.__version__}")
    except ImportError as e:
        print(f"   ❌ NumPy: {e}")
        return False
    
    try:
        from PIL import Image
        print("   ✅ Pillow")
    except ImportError as e:
        print(f"   ❌ Pillow: {e}")
        return False
    
    # Testar módulos do projeto
    try:
        from captcha_ml.captcha_collector import CaptchaCollector
        print("   ✅ CaptchaCollector")
    except ImportError as e:
        print(f"   ❌ CaptchaCollector: {e}")
        return False
    
    try:
        from captcha_ml.image_processor import ImageProcessor
        print("   ✅ ImageProcessor")
    except ImportError as e:
        print(f"   ❌ ImageProcessor: {e}")
        return False
    
    try:
        from captcha_ml.captcha_model import CaptchaModel
        print("   ✅ CaptchaModel")
    except ImportError as e:
        print(f"   ❌ CaptchaModel: {e}")
        return False
    
    print("✅ Todos os componentes funcionando!")
    return True

def show_next_steps():
    """Mostra os próximos passos"""
    print("\n🎉 INSTALAÇÃO CONCLUÍDA!")
    print("=" * 50)
    print()
    print("📋 PRÓXIMOS PASSOS:")
    print()
    print("1️⃣  Demonstração:")
    print("   python3 demo_ml_captcha.py")
    print()
    print("2️⃣  Começar pipeline de ML:")
    print("   python3 captcha_pipeline.py collect --num 50")
    print("   python3 captcha_pipeline.py label")
    print("   python3 captcha_pipeline.py process") 
    print("   python3 captcha_pipeline.py train")
    print()
    print("3️⃣  Usar scrapper com ML:")
    print("   from scrapper.scrapper import buscar_dados_bid")
    print("   registros = buscar_dados_bid('SP', '01/01/2024')")
    print()
    print("💡 DICAS:")
    print("   - Colete pelo menos 100 captchas para bom treinamento")
    print("   - Seja preciso na rotulagem - qualidade > quantidade")
    print("   - Teste o modelo antes de usar em produção")
    print()

def main():
    print("🚀 SETUP - SISTEMA ML CAPTCHAS BID CBF")
    print("=" * 50)
    print()
    
    # Verificar Python
    if not check_python_version():
        return 1
    
    # Verificar sistema
    check_system_requirements()
    print()
    
    # Criar diretórios
    create_directories()
    print()
    
    # Instalar dependências
    if not install_dependencies():
        return 1
    print()
    
    # Testar instalação
    if not test_installation():
        print("\n❌ Instalação incompleta - verifique os erros acima")
        return 1
    
    # Próximos passos
    show_next_steps()
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
