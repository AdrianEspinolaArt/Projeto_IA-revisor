import tkinter as tk

from avaliador_texto import AvaliadorTexto


class InterfaceGrafica:
    def iniciar_revisao(self):
        arquivo = self.caixa_texto_arquivo.get()
        perfil = self.caixa_texto_perfil.get()
        feedback = AvaliadorTexto.avaliar_texto(arquivo, perfil)
        self.caixa_texto_feedback.config(text=feedback)

    def fechar(self):
        self.janela.destroy()


if __name__ == "__main__":
    janela = tk.Tk()
    janela.title("Revisor de texto")

    caixa_texto_arquivo = tk.Entry(janela, width=50)
    botao_iniciar = tk.Button(janela, text="Iniciar revisão")
    botao_fechar = tk.Button(janela, text="Fechar")
    caixa_texto_feedback = tk.Label(janela, text="Feedback")

    caixa_texto_arquivo.pack()
    botao_iniciar.pack()
    botao_fechar.pack()
    caixa_texto_feedback.pack()

    botao_iniciar.bind("<Button-1>", interface_grafica.iniciar_revisao)
    botao_fechar.bind("<Button-1>", interface_grafica.fechar)

    janela.mainloop()
