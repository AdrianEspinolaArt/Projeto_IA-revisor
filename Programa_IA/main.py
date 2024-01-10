# main.py
from avaliador_texto import AvaliadorTexto
from interface_grafica import InterfaceGrafica

if __name__ == "__main__":
    avaliador = AvaliadorTexto()
    interface = InterfaceGrafica(avaliador)
    interface.mainloop()
