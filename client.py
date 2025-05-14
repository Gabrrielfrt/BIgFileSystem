import Pyro5.api
import os
import base64


class BigFileSclient:
    def __init__(self):
        self.sistema = None

    def conectar(self, uri):
        try:
            self.sistema = Pyro5.api.Proxy(uri)
            print("Conectado ao servidor com sucesso!")
            return True
        except Exception as e:
            print(f"Falha ao conectar no servidor: {str(e)}")
            return False

    def copy(self, origem, destino):
        origem = origem.strip()
        destino = destino.strip()
    
        # Upload (cliente → servidor)
        if not origem.startswith("remote:") and destino.startswith("remote:"):
            try:
                if not os.path.exists(origem):
                    print(f"Erro: Arquivo local '{origem}' não encontrado")
                    return
    
                with open(origem, "rb") as f:
                    dados = f.read()
                    if len(dados) == 0:
                        print("Aviso: Arquivo de origem está vazio")
    
                dados_codificados = base64.b64encode(dados).decode('utf-8')
                server_path = destino[len("remote:"):].lstrip('/')
                print(f"Enviando '{origem}' para servidor (remote:{server_path})...")
    
                resultado = self.sistema.copy_to_server(server_path, dados_codificados)
                print(resultado)
    
            except Exception as e:
                print(f"Erro no upload: {str(e)}")
    
        # Download (servidor → cliente)
        elif origem.startswith("remote:") and not destino.startswith("remote:"):
            try:
                server_path = origem[len("remote:"):].lstrip('/')
                print(f"Solicitando '{server_path}' do servidor...")
    
                resposta = self.sistema.copy_to_client(server_path)
                if isinstance(resposta, dict) and "erro" in resposta:
                    print(f"Erro no servidor: {resposta['erro']}")
                    return
    
                dados_codificados = resposta["dados"]
                dados = base64.b64decode(dados_codificados)
    
                with open(destino, "wb") as f:
                    f.write(dados)
    
                print(f"Arquivo salvo localmente em '{destino}' ({len(dados)} bytes)")
    
            except Exception as e:
                print(f"Erro no download: {str(e)}")
    
        else:
            print("Operação de cópia não suportada entre esses caminhos.")

    def operacoes(self):
        try:
            print("\nNetwork File System")
            print("Comandos disponíveis:")
            print("  LS                        - Listar arquivos no servidor")
            print("  CP <origem> <destino>     - Copiar arquivo entre cliente e servidor")
            print("                              Use 'remote:/caminho' para caminhos do servidor")
            print("  RM  remote:/caminho        - Remova um arquivo no diretorio remoto")
            print("  HELP                      - Mostrar este menu")
            print("  EXIT                      - Sair do programa")
            print()

            entrada = input(">").strip()
            if not entrada:
                return

            partes = entrada.split(maxsplit=2)
            comando = partes[0].upper()

            if comando == "LS":
                resultado = self.sistema.listar()
                print(f"Arquivos: {resultado}")

            elif comando == "CP":
                if len(partes) != 3:
                    print("Uso correto: CP <origem> <destino>")
                else:
                    _, origem, destino = partes
                    self.copy(origem, destino)

            elif comando == "HELP":
                print("Comandos disponíveis:")
                print("  LS                        - Listar arquivos no servidor")
                print("  CP <origem> <destino>     - Copiar arquivo entre cliente e servidor")
                print("                              Use 'remote:/caminho' para caminhos do servidor")
                print("  RM  remote:/caminho        - Remova um arquivo no diretorio remoto")
                print("  HELP                      - Mostrar este menu")
                print("  EXIT                      - Sair do programa")

            elif comando == "RM":
                if len(partes) != 2:
                    print("Uso correto: RM remote:/caminho ")
                else:
                    _, caminho = partes
                    self.rm(origem, caminho)                


            elif comando == "EXIT":
                print("Encerrando cliente...")
                exit()

            else:
                print("Comando inválido. Digite HELP para ajuda.")

        except Exception as e:
            print(f"Erro ao executar operação: {str(e)}")


def main():
    cliente = BigFileSclient()

    uri = input("Digite a URI do servidor (ex: PYRO:obj_123@localhost:9090): ")
    if not cliente.conectar(uri):
        return

    while True:
        cliente.operacoes()


if __name__ == "__main__":
    main()
