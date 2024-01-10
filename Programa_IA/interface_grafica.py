import tkinter as tk
from tkinter import filedialog
from docx import Document
from avaliador_texto import AvaliadorTexto

class InterfaceGrafica(tk.Tk):

    def __init__(self, avaliador):
        super().__init__()
        self.avaliador = avaliador
        self.title("Avaliador de Texto")

        # Adicionando opção para escolher o perfil
        self.perfil_var = tk.StringVar(self)
        self.perfis_disponiveis = ["Resenha", "OutroPerfil"]  # Adicione outros perfis conforme necessário
        self.perfil_var.set(self.perfis_disponiveis[0])  # Definindo o perfil padrão

        self.perfil_label = tk.Label(self, text="Escolha o Perfil:")
        self.perfil_label.pack()

        self.perfil_menu = tk.OptionMenu(self, self.perfil_var, *self.perfis_disponiveis)
        self.perfil_menu.pack()

        self.abrir_button = tk.Button(self, text="Abrir Arquivo", command=self.abrir_arquivo)
        self.abrir_button.pack(pady=20)

    def abrir_arquivo(self):
        caminho_arquivo = filedialog.askopenfilename(defaultextension=".docx", filetypes=[("Documentos Word", "*.docx")])
        if caminho_arquivo:
            doc = Document(caminho_arquivo)
            texto_do_aluno = '\n'.join([paragrafo.text for paragrafo in doc.paragraphs])

            # Aqui você pode usar a escolha do perfil para criar uma instância específica do AvaliadorTexto
            perfil_selecionado = self.perfil_var.get()
            avaliador = AvaliadorTexto(perfil_selecionado)

            # Avaliar o texto e obter a pontuação final
            pontuacao_final = avaliador.avaliar_texto(caminho_arquivo)

            # Exibir a pontuação final
            self.mostrar_mensagem(f"Pontuação final do texto: {pontuacao_final}")

    def mostrar_mensagem(self, mensagem):
        mensagem_label = tk.Label(self, text=mensagem)
        mensagem_label.pack()

if __name__ == "__main__":
    # Executar a interface
    interface = InterfaceGrafica(avaliador=None)  # Avaliador será passado quando criamos a interface no main.py
    interface.mainloop()

    # Adicione uma pausa para que o console não seja fechado imediatamente
    input("Pressione Enter para sair...")
