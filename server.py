import os
import Pyro4

Pyro4.config.SERIALIZER = 'pickle'
Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')


current_dir = os.path.dirname(os.path.abspath(__file__))
directory_path = os.path.join(current_dir,"FSroot")

def iniciar_servidor():   
    os.makedirs(directory_path, exist_ok=True)

    print("Iniciando servidor RMI...")
    daemon = Pyro4.Daemon()
    uri = daemon.register(sistemaArquivos)
    
    print(f"Servidor iniciado com sucesso!")
    print(f"URI do objeto: {uri}")
    print("Aguardando conexões de clientes...")
    
    daemon.requestLoop()

@Pyro4.expose
class sistemaArquivos:
    
    def listar(self):
        files = os.listdir(directory_path)
        return files

    
    def copy_to_server(self, server_path, dados):
        full_path = os.path.join(directory_path, server_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        try:
            with open(full_path, 'wb') as f:
                f.write(dados)
            return f"Arquivo {server_path} salvo no servidor."
        except Exception as e:
            return f"Erro ao salvar no servidor: {str(e)}"
    
    def copy_from_server(self, nome):
        file_path = os.path.join(directory_path, nome)
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Erro ao ler do servidor: {str(e)}")
        
    
    def pwd(self):
        return os.getcwd()
    

if __name__ == "__main__":
    iniciar_servidor()