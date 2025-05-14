import os
import Pyro5.api
import base64



current_dir = os.path.dirname(os.path.abspath(__file__))
directory_path = os.path.join(current_dir, "FSroot")

def iniciar_servidor():   
    os.makedirs(directory_path, exist_ok=True)

    print("Iniciando servidor RMI...")
    daemon = Pyro5.api.Daemon()
    uri = daemon.register(sistemaArquivos)
    
    print(f"Servidor iniciado com sucesso!")
    print(f"URI do objeto: {uri}")
    print("Aguardando conexões de clientes...")
    
    daemon.requestLoop()

@Pyro5.api.expose
class sistemaArquivos:

    def listar(self):
        files = os.listdir(directory_path)
        return files

    def copy_to_server(self, server_path, dados_codificados):
        try:
            dados = base64.b64decode(dados_codificados)
            if not isinstance(dados, bytes):
                raise ValueError("Dados devem ser do tipo bytes")

            server_path = server_path.lstrip('/')
            full_path = os.path.join(directory_path, server_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, 'wb') as f:
                f.write(dados)

            size = os.path.getsize(full_path)
            return f"Arquivo '{server_path}' salvo com sucesso ({size} bytes)"

        except Exception as e:
            return f"Erro ao salvar: {str(e)}"

    def copy_to_client(self, server_path):
        try:
            
            server_path = server_path.lstrip('/')
            full_path = os.path.join(directory_path, server_path)

            if not os.path.exists(full_path):
                return {"erro": f"Arquivo '{server_path}' não encontrado"}

            with open(full_path, 'rb') as f:
                dados = f.read()

            dados_codificados = base64.b64encode(dados).decode('utf-8')
            return {"dados": dados_codificados}

        except Exception as e:
            return {"erro": str(e)}
    
    def rm(self, path):
        try:
            full_path = os.path.join(directory_path, path)
            if os.path.isfile(full_path):
                os.remove(full_path)
                return f"Arquivo {path} removido com sucesso."
            elif os.path.isdir(full_path):
                os.rmdir(full_path)
                return f"Diretório {path} removido com sucesso."
            else:
                return f"Erro: {path} não existe."
        except Exception as e:
            return f"Erro ao remover {path}: {str(e)}"
        
    def pwd(self):
        return directory_path
    
if __name__ == "__main__":
    iniciar_servidor()
