import Pyro4
import os

Pyro4.config.SERIALIZER = 'pickle'
Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')


class BigFileSclient:
    def __init__(self):
        self.sistema = None

    def conectar(self, uri):
            try:
                self.sistema = Pyro4.Proxy(uri)
                print("Conectado ao servidor com sucesso!")
                return True
            except Exception as e:
                print(f"Falha ao conectar no servidor: {str(e)}")
                return False

    def copy(self, origem, destino):
        origem = origem.strip()
        destino = destino.strip()

        # Upload (cliente → servidor)
        if not origem.startswith("/FSroot") and destino.startswith("/FSroot"):
            try:
                with open(origem, "rb") as f:
                    dados = f.read()
                server_path = destino[len("/FSroot"):].lstrip('/')
                resultado = self.sistema.copy_to_server(server_path, dados)
                print(resultado)
            except Exception as e:
                print(f"Erro ao enviar arquivo: {e}")

        # Download (servidor → cliente)
        elif origem.startswith("/FSroot") and not destino.startswith("/FSroot"):
            try:
                nome_origem = origem[len("/FSroot"):].lstrip('/')
                dados = self.sistema.copy_from_server(nome_origem)
                with open(destino, "wb") as f:
                    f.write(dados)
                print(f"Arquivo salvo em {destino}")
            except Exception as e:
                print(f"Erro ao baixar arquivo: {e}")

        else:
            print("Erro: Um dos caminhos deve estar dentro de /FSroot (servidor), e o outro deve ser local.")


    def operacoes(self):
        try:
            print("Comandos disponíveis:")
            print("  LS                        - Listar arquivos no servidor")
            print("  CP <origem> <destino>     - Copiar arquivo entre cliente e servidor")
            print("                              Use /FSroot/... para caminhos do servidor")
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
                print("                              Use /FSroot/... para caminhos do servidor")
                print("  HELP                      - Mostrar este menu")
                print("  EXIT                      - Sair do programa")

            elif comando == "PWD":
                resultado = self.sistema.pwd()
                print(resultado)

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
        print("\n--- Big File System 1.5 ---")
        cliente.operacoes()
        
        continuar = input("\nDeseja fazer outra operação? (s/n): ").lower()
        if continuar != 's':
            break


if __name__ == "__main__":
    main()