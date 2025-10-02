# main.py
# VERSÃO DESKTOP DESATIVADA - USE A VERSÃO WEB

import sys

def main():
    """
    A versão desktop foi desativada.
    Use a versão web executando: python web/app.py
    """
    print("=" * 60)
    print("⚠️  VERSÃO DESKTOP DESATIVADA")
    print("=" * 60)
    print()
    print("Este sistema agora funciona apenas em modo WEB.")
    print()
    print("Para iniciar a interface web, execute:")
    print("   cd web")
    print("   python app.py")
    print()
    print("Ou use o arquivo: web/run_web.bat")
    print()
    print("Ou clique no atalho 'BCI-ON1 Web' na sua área de trabalho.")
    print("=" * 60)
    
    return False

if __name__ == "__main__":
    print("🤖 SISTEMA DE AUTOMAÇÃO SERVOPA + TODOIST")
    print()
    
    success = main()
    
    if not success:
        print("\n⚠️  Redirecionando para versão web...")
        input("Pressione ENTER para sair...")
        sys.exit(1)
