from avaliador_texto import AvaliadorTexto
from interface_grafica import InterfaceGrafica

if __name__ == "__main__":
    perfil_padrao = "Resenha"  # Escolha o perfil desejado
    avaliador = AvaliadorTexto(perfil=perfil_padrao)
    interface = InterfaceGrafica(avaliador)
    interface.mainloop()
