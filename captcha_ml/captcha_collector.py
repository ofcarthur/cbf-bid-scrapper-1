import requests
import base64
import os
from PIL import Image
import io
import time
from datetime import datetime

class CaptchaCollector:
    """
    Classe responsável por coletar captchas do BID da CBF para treinar o modelo
    """
    
    def __init__(self, data_dir="captcha_ml/data"):
        self.data_dir = data_dir
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://bid.cbf.com.br',
            'Referer': 'https://bid.cbf.com.br/'
        }
        
        # Criar diretórios se não existirem
        os.makedirs(f"{self.data_dir}/raw", exist_ok=True)
        os.makedirs(f"{self.data_dir}/labeled", exist_ok=True)
        os.makedirs(f"{self.data_dir}/processed", exist_ok=True)
    
    def get_captcha_image(self):
        """
        Obtém uma imagem de captcha do BID da CBF
        
        Returns:
            PIL.Image: Imagem do captcha ou None se erro
        """
        try:
            # Primeiro acessa a página principal
            response_home = self.session.get('https://bid.cbf.com.br/', headers=self.headers, timeout=10)
            
            if response_home.status_code != 200:
                print(f"Erro ao acessar página principal: {response_home.status_code}")
                return None
            
            # Obter o captcha 
            captcha_response = self.session.get('https://bid.cbf.com.br/get-captcha-base64', 
                                              headers=self.headers, timeout=10)
            
            if captcha_response.status_code != 200:
                print(f"Erro ao obter captcha: Status {captcha_response.status_code}")
                return None
            
            content_type = captcha_response.headers.get('content-type', '').lower()
            
            # Verificar se é uma imagem direta ou JSON
            if 'image' in content_type:
                # Resposta é uma imagem direta
                image = Image.open(io.BytesIO(captcha_response.content))
                return image
            elif 'json' in content_type:
                # Resposta é JSON com base64
                try:
                    captcha_data = captcha_response.json()
                    if 'image' in captcha_data:
                        base64_string = captcha_data['image']
                        if base64_string.startswith('data:image'):
                            base64_string = base64_string.split(',')[1]
                        image_data = base64.b64decode(base64_string)
                        image = Image.open(io.BytesIO(image_data))
                        return image
                except Exception as e:
                    print(f"Erro decodificando JSON: {e}")
                    return None
            else:
                # Tentar como base64 puro (texto)
                try:
                    response_text = captcha_response.text.strip()
                    # Remover prefixo se presente
                    if response_text.startswith('data:image'):
                        response_text = response_text.split(',')[1]
                    
                    image_data = base64.b64decode(response_text)
                    image = Image.open(io.BytesIO(image_data))
                    print("✓ Captcha decodificado como base64 puro")
                    return image
                except Exception as e:
                    print(f"Erro decodificando base64: {e}")
                    print(f"Content-Type: {content_type}")
                    print(f"Response length: {len(captcha_response.text)}")
                    return None
                
        except Exception as e:
            print(f"Erro ao obter captcha: {e}")
            return None
    
    def collect_captchas(self, num_captchas=100, delay=2):
        """
        Coleta múltiplos captchas e salva para análise
        
        Args:
            num_captchas: Número de captchas a coletar
            delay: Delay entre requests em segundos
        """
        print(f"Coletando {num_captchas} captchas...")
        
        collected = 0
        for i in range(num_captchas):
            try:
                image = self.get_captcha_image()
                if image:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    filename = f"captcha_{timestamp}.png"
                    filepath = os.path.join(self.data_dir, "raw", filename)
                    
                    image.save(filepath)
                    collected += 1
                    print(f"Captcha {collected}/{num_captchas} salvo: {filename}")
                else:
                    print(f"Falhou ao obter captcha {i+1}")
                
                # Delay para não sobrecarregar o servidor
                time.sleep(delay)
                
            except Exception as e:
                print(f"Erro coletando captcha {i+1}: {e}")
                continue
        
        print(f"\nColeta concluída! {collected} captchas salvos em {self.data_dir}/raw/")
        return collected
    
    def interactive_labeling(self):
        """
        Interface interativa para rotular captchas coletados
        """
        raw_dir = os.path.join(self.data_dir, "raw")
        labeled_dir = os.path.join(self.data_dir, "labeled")
        
        # Listar arquivos não rotulados
        raw_files = [f for f in os.listdir(raw_dir) if f.endswith('.png')]
        labeled_files = [f for f in os.listdir(labeled_dir) if f.endswith('.png')]
        
        # Extrair nomes base dos arquivos rotulados (remover prefixo do label)
        labeled_basenames = set()
        for f in labeled_files:
            # Formato: label_captcha_timestamp.png -> pegar tudo após o primeiro _
            parts = f.split('_', 1)
            if len(parts) > 1:
                labeled_basenames.add(parts[1])
        
        # Filtrar apenas arquivos que não foram rotulados
        unlabeled = [f for f in raw_files if f not in labeled_basenames]
        
        if not unlabeled:
            print("Todos os captchas já foram rotulados!")
            return
        
        print(f"\n{len(unlabeled)} captchas para rotular...")
        print("Instruções:")
        print("- Digite o texto que você vê no captcha")
        print("- Digite 'skip' para pular")
        print("- Digite 'quit' para sair")
        print("-" * 50)
        
        for filename in unlabeled:
            filepath = os.path.join(raw_dir, filename)
            
            try:
                # Mostrar a imagem (requer matplotlib ou pillow com display)
                image = Image.open(filepath)
                print(f"\nArquivo: {filename}")
                print(f"Tamanho: {image.size}")
                
                # Salvar temporariamente para visualização
                temp_path = "/tmp/current_captcha.png"
                image.save(temp_path)
                print(f"Captcha salvo temporariamente em: {temp_path}")
                print("Abra o arquivo para visualizar a imagem")
                
                label = input("\nDigite o texto do captcha: ").strip()
                
                if label.lower() == 'quit':
                    break
                elif label.lower() == 'skip':
                    continue
                elif label:
                    # Salvar com o rótulo no nome do arquivo
                    labeled_filename = f"{label}_{filename}"
                    labeled_path = os.path.join(labeled_dir, labeled_filename)
                    
                    # Salvar na pasta labeled
                    image.save(labeled_path)
                    
                    # REMOVER o arquivo original da pasta raw
                    os.remove(filepath)
                    
                    print(f"✓ Rotulado e salvo como: {labeled_filename}")
                    print(f"✓ Arquivo removido de raw/")
                else:
                    print("Rótulo vazio, pulando...")
                    
            except Exception as e:
                print(f"Erro processando {filename}: {e}")
                continue
        
        print("\nRotulagem concluída!")
    
    def show_statistics(self):
        """
        Mostra estatísticas dos captchas coletados
        """
        raw_dir = os.path.join(self.data_dir, "raw")
        labeled_dir = os.path.join(self.data_dir, "labeled")
        
        raw_count = len([f for f in os.listdir(raw_dir) if f.endswith('.png')])
        labeled_count = len([f for f in os.listdir(labeled_dir) if f.endswith('.png')])
        
        print("\n=== ESTATÍSTICAS DOS CAPTCHAS ===")
        print(f"Captchas coletados: {raw_count}")
        print(f"Captchas rotulados: {labeled_count}")
        print(f"Captchas pendentes: {raw_count - labeled_count}")
        
        if labeled_count > 0:
            # Analisar os rótulos
            labeled_files = [f for f in os.listdir(labeled_dir) if f.endswith('.png')]
            labels = [f.split('_')[0] for f in labeled_files]
            
            print(f"\nComprimento dos rótulos:")
            lengths = [len(label) for label in labels]
            print(f"- Mínimo: {min(lengths)} caracteres")
            print(f"- Máximo: {max(lengths)} caracteres")
            print(f"- Médio: {sum(lengths)/len(lengths):.1f} caracteres")
            
            # Caracteres únicos
            unique_chars = set(''.join(labels))
            print(f"\nCaracteres únicos encontrados: {sorted(unique_chars)}")
            print(f"Total de caracteres únicos: {len(unique_chars)}")

if __name__ == "__main__":
    collector = CaptchaCollector()
    
    print("=== COLETOR DE CAPTCHAS BID CBF ===")
    print("1. Coletar captchas")
    print("2. Rotular captchas")
    print("3. Ver estatísticas")
    
    choice = input("Escolha uma opção (1-3): ")
    
    if choice == "1":
        num = int(input("Quantos captchas coletar? "))
        collector.collect_captchas(num)
    elif choice == "2":
        collector.interactive_labeling()
    elif choice == "3":
        collector.show_statistics()
