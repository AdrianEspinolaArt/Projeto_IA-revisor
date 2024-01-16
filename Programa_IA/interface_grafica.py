import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time
from resenha import AvaliadorTexto

class InterfaceGrafica(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Avaliador de Texto")
        self.geometry("800x800")  # Ajustei o tamanho do aplicativo
        self.configure(bg="#F0F0F0")  # Cor de fundo

        # Mapeamento de nomes para tornar os critérios mais legíveis
        self.mapeamento_nomes = {
            'Formatacao': 'Formatação',
            'Linhas': 'Linhas',
            'Citacoes': 'Citações',
            'Lingua_Portuguesa': 'Língua Portuguesa',
            'Adequacao': 'Adequação'
        }

        # Variável para armazenar o perfil selecionado
        self.var_perfil = tk.StringVar(self)
        self.var_perfil.set("Resenha")  # Perfil padrão

        # Seletor de perfil
        self.lbl_seletor_perfil = tk.Label(self, text="Selecione o Perfil:", bg="#F0F0F0", font=("Helvetica", 12))
        self.lbl_seletor_perfil.grid(row=0, column=0, pady=10, padx=(20, 0), sticky="e")  # Ajuste para alinhar à direita
        self.dropdown_perfil = ttk.Combobox(self, textvariable=self.var_perfil, values=["Resenha", "Artigo"],
                                           font=("Helvetica", 12), state="readonly")
        self.dropdown_perfil.grid(row=0, column=1, pady=10, padx=(0, 20), sticky="w")  # Ajuste para alinhar à esquerda

        # Botão para selecionar o arquivo
        self.btn_selecionar_arquivo = tk.Button(self, text="Selecionar Arquivo", command=self.selecionar_arquivo,
                                                font=("Helvetica", 12), bg="#4CAF50", fg="white")
        self.btn_selecionar_arquivo.grid(row=1, column=0, pady=5, padx=(100, 0), sticky="w")  # Ajuste na opção padx

        # Botão de iniciar
        self.btn_iniciar = tk.Button(self, text="Iniciar Avaliação", command=self.iniciar_avaliacao,
                                    font=("Helvetica", 12), bg="#008CBA", fg="white")
        self.btn_iniciar.grid(row=1, column=1, pady=5, padx=(0, 100), sticky="e")  # Ajuste na opção padx

        # Frame para detalhes da pontuação
        self.frame_detalhes_pontuacao = tk.Frame(self, bg="#F0F0F0")
        self.frame_detalhes_pontuacao.grid(row=3, column=0, columnspan=2, pady=10, padx=20)  # Ajuste na opção padx

        # Label para exibir a pontuação total
        self.lbl_pontuacao_total = tk.Label(self.frame_detalhes_pontuacao, text="Pontuação: N/A", bg="#F0F0F0",
                                            font=("Helvetica", 14, "bold"))
        self.lbl_pontuacao_total.grid(row=0, column=0, columnspan=2, pady=10)

        # Frame para exibir os critérios e pontuações
        self.frame_critérios = tk.Frame(self.frame_detalhes_pontuacao, bg="#F0F0F0")
        self.frame_critérios.grid(row=1, column=0, columnspan=2, pady=10, padx=(20, 20))  # Ajuste na opção padx

        # Configurar o grid para que os elementos possam expandir para ocupar o espaço disponível
        for i in range(4):
            self.grid_rowconfigure(i, weight=1)
            self.grid_columnconfigure(0, weight=1)

    def selecionar_arquivo(self):
        caminho_arquivo = filedialog.askopenfilename(filetypes=[("Arquivos DOCX", "*.docx")])
        if caminho_arquivo:
            self.caminho_arquivo = caminho_arquivo
            self.lbl_pontuacao_total.config(text="Pontuação: N/A")
            self.atualizar_detalhes_critérios({})  # Limpar detalhes dos critérios

    def iniciar_avaliacao(self):
        if hasattr(self, 'caminho_arquivo') and self.caminho_arquivo:
            self.tempo_inicio = time.time()
            if self.var_perfil.get() == "Resenha":
                from resenha import AvaliadorTexto
                self.avaliador = AvaliadorTexto(perfil="Resenha")
            elif self.var_perfil.get() == "Artigo":
                from artigo import AvaliadorArtigo
                self.avaliador = AvaliadorArtigo(perfil="Artigo")

            self.avaliar_arquivo(self.caminho_arquivo)
        else:
            messagebox.showinfo("Aviso", "Selecione um arquivo antes de iniciar a avaliação.")

    def avaliar_arquivo(self, caminho_arquivo):
        pontuacoes_detalhadas = self.avaliador.avaliar_texto(caminho_arquivo)

        self.tempo_fim = time.time()
        tempo_decorrido = self.tempo_fim - self.tempo_inicio

        # Exibe os detalhes da pontuação total
        pontuacao_total = sum(pontuacao['pontuacao'] for pontuacao in pontuacoes_detalhadas.values())
        self.lbl_pontuacao_total.config(text=f"Pontuação: {pontuacao_total:.2f}")

        # Exibe os detalhes dos critérios
        self.atualizar_detalhes_critérios(pontuacoes_detalhadas)

    def atualizar_detalhes_critérios(self, pontuacoes_detalhadas):
        # Limpar widgets antigos
        for widget in self.frame_critérios.winfo_children():
            widget.destroy()

        # Criar widgets para cada critério
        for i, (criterio, pontuacao) in enumerate(pontuacoes_detalhadas.items(), start=1):
            # Nome formatado do critério usando o mapeamento
            nome_formatado = self.mapeamento_nomes.get(criterio, criterio)

            # Label para o nome do critério
            lbl_criterio = tk.Label(self.frame_critérios, text=nome_formatado, bg="#F0F0F0", font=("Helvetica", 12, "bold"))
            lbl_criterio.grid(row=i, column=0, padx=(20, 0), pady=5, sticky="w")  # Ajuste para alinhar à esquerda

            # Label para a pontuação do critério
            lbl_pontuacao = tk.Label(self.frame_critérios, text=f"Pontuação: {pontuacao['pontuacao']:.2f}", bg="#F0F0F0",
                                     font=("Helvetica", 12))
            lbl_pontuacao.grid(row=i, column=1, padx=(0, 20), pady=5, sticky="e")  # Ajuste para alinhar à direita

            # Label para a justificativa do critério
            lbl_justificativa = tk.Label(self.frame_critérios, text=pontuacao['justificativa'], bg="#F0F0F0",
                                         font=("Helvetica", 10))
            lbl_justificativa.grid(row=i, column=2, padx=20, pady=5, sticky="w", columnspan=2)  # Ajuste para alinhar à esquerda

if __name__ == "__main__":
    app = InterfaceGrafica()
    app.mainloop()
