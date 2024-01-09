# interface_grafica.py
import tkinter as tk
from tkinter import filedialog
from docx import Document
from avaliador_texto import AvaliadorTexto

def criar_interface_grafica():
    def abrir_arquivo():
        caminho_arquivo = filedialog.askopenfilename(defaultextension=".docx", filetypes=[("Documentos Word", "*.docx")])
        if caminho_arquivo:
            doc = Document(caminho_arquivo)
            texto_do_aluno = '\n'.join([paragrafo.text for paragrafo in doc.paragraphs])

            # Aqui você pode usar a escolha do perfil para criar uma instância específica do AvaliadorTexto
            perfil_selecionado = perfil_var.get()
            avaliador = AvaliadorTexto(perfil_selecionado)

            # Avaliar o texto e obter a pontuação final
            pontuacao_final = avaliador.avaliar_texto(caminho_arquivo)

            # Aqui você pode exibir a pontuação final ou realizar outras ações com ela
            print(f"Pontuação final do texto: {pontuacao_final}")

    root = tk.Tk()
    root.title("Avaliador de Texto")

    # Adicionando opção para escolher o perfil
    perfil_var = tk.StringVar(root)
    perfis_disponiveis = ["Resenha", "OutroPerfil"]  # Adicione outros perfis conforme necessário
    perfil_var.set(perfis_disponiveis[0])  # Definindo o perfil padrão

    perfil_label = tk.Label(root, text="Escolha o Perfil:")
    perfil_label.pack()

    perfil_menu = tk.OptionMenu(root, perfil_var, *perfis_disponiveis)
    perfil_menu.pack()

    abrir_button = tk.Button(root, text="Abrir Arquivo", command=abrir_arquivo)
    abrir_button.pack(pady=20)

    # Restante do código da interface...

    root.mainloop()

# Executar a interface
criar_interface_grafica()

# Adicione uma pausa para que o console não seja fechado imediatamente
input("Pressione Enter para sair...")
