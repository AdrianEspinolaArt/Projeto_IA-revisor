# main.py
from avaliador_texto import AvaliadorTexto
from interface_grafica import criar_interface_grafica

if __name__ == "__main__":
    avaliador = AvaliadorTexto()
    criar_interface_grafica(avaliador)
