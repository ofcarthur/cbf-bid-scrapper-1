#!/usr/bin/env python3
"""
Teste rápido do sistema de ML para captchas

Execute este arquivo para verificar se tudo está funcionando corretamente.
"""

def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print("🧪 Testando imports...")
    
    modules_to_test = [
        ("requests", "requests"),
        ("BeautifulSoup4", "bs4"),
        ("TensorFlow", "tensorflow"),
        ("OpenCV", "cv2"),
        ("NumPy", "numpy"),
        ("Pillow", "PIL"),
        ("scikit-learn", "sklearn"),
        ("matplotlib", "matplotlib"),
    ]
    
    success = True
    for name, module in modules_to_test:
        try:
            __import__(module)
            print(f"   ✅ {name}")
        except ImportError as e:
            print(f"   ❌ {name}: {e}")
            success = False
    
    return success

def test_project_structure():
    """Testa se a estrutura do projeto está correta"""
    print("\n📁 Testando estrutura do projeto...")
    
    import os
    
    required_files = [
        "scrapper/scrapper.py",
        "captcha_ml/__init__.py",
        "captcha_ml/captcha_collector.py",
        "captcha_ml/image_processor.py", 
        "captcha_ml/captcha_model.py",
        "captcha_ml/captcha_solver.py",
        "captcha_pipeline.py",
        "demo_ml_captcha.py",
        "requirements.txt"
    ]
    
    required_dirs = [
        "captcha_ml/data/raw",
        "captcha_ml/data/labeled",
        "captcha_ml/data/processed",
        "captcha_ml/models"
    ]
    
    success = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}")
            success = False
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"   ✅ {dir_path}/")
        else:
            print(f"   ❌ {dir_path}/")
            success = False
    
    return success

def test_basic_functionality():
    """Testa funcionalidades básicas"""
    print("\n⚙️ Testando funcionalidades básicas...")
    
    try:
        # Testar importação do scrapper original
        from scrapper.scrapper import buscar_dados_bid
        print("   ✅ Scrapper importado")
        
        # Testar importação dos módulos de ML
        from captcha_ml.captcha_collector import CaptchaCollector
        from captcha_ml.image_processor import ImageProcessor
        from captcha_ml.captcha_model import CaptchaModel
        from captcha_ml.captcha_solver import CaptchaSolver
        print("   ✅ Módulos ML importados")
        
        # Testar criação de objetos
        collector = CaptchaCollector()
        processor = ImageProcessor()
        model = CaptchaModel()
        solver = CaptchaSolver()
        print("   ✅ Objetos criados")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def main():
    print("🔧 TESTE RÁPIDO - SISTEMA ML CAPTCHAS")
    print("=" * 45)
    
    all_good = True
    
    # Teste 1: Imports
    if not test_imports():
        all_good = False
    
    # Teste 2: Estrutura
    if not test_project_structure():
        all_good = False
    
    # Teste 3: Funcionalidades
    if not test_basic_functionality():
        all_good = False
    
    print("\n" + "=" * 45)
    
    if all_good:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("\n✅ Sistema pronto para uso!")
        print("\n📋 Próximos passos:")
        print("   1. python3 demo_ml_captcha.py")
        print("   2. python3 captcha_pipeline.py collect --num 50")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("\n🔧 Soluções:")
        print("   1. Execute: python3 setup.py")
        print("   2. Verifique: pip3 install -r requirements.txt")
        print("   3. Verifique se todos os arquivos estão presentes")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
