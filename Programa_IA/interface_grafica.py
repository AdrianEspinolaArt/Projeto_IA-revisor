import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time
from resenha import AvaliadorTexto
from artigo import AvaliadorArtigo
from docx import Document

class InterfaceGrafica(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Avaliador de Texto")
        self.geometry("1400x900")  # Ajustei o tamanho do aplicativo
        self.configure(bg="#F0F0F0")  # Cor de fundo

        # Mapeamento de nomes para tornar os critérios mais legíveis
        self.mapeamento_nomes = {
            'Formatacao': 'Formatação:',
            'Linhas': 'Linhas:',
            'Citacoes': 'Citações:',
            'Lingua_Portuguesa': 'Língua Portuguesa:',
            'Adequacao': 'Adequação:'
        }

        # Variável para armazenar o perfil selecionado
        self.var_perfil = tk.StringVar(self)
        self.var_perfil.set("Resenha")  # Perfil padrão

        # Seletor de perfil
        self.lbl_seletor_perfil = tk.Label(self, text="Selecione o Perfil:", bg="#F0F0F0", font=("Helvetica", 12))
        self.lbl_seletor_perfil.grid(row=0, column=0, pady=10, padx=(100, 0), sticky="e")  # Ajuste para alinhar à direita
        self.dropdown_perfil = ttk.Combobox(self, textvariable=self.var_perfil, values=["Resenha", "Artigo"],
                                           font=("Helvetica", 12), state="readonly")
        self.dropdown_perfil.grid(row=0, column=1, pady=10, padx=(0, 20), sticky="w")  # Ajuste para alinhar à esquerda

        # Botão para selecionar o arquivo
        self.btn_selecionar_arquivo = tk.Button(self, text="Selecionar Arquivo", command=self.selecionar_arquivo,
                                                font=("Helvetica", 12), bg="#4CAF50", fg="white")
        self.btn_selecionar_arquivo.grid(row=1, column=0, pady=5, padx=(500, 0), sticky="w")  # Ajuste na opção padx

        # Botão de iniciar
        self.btn_iniciar = tk.Button(self, text="Iniciar Avaliação", command=self.iniciar_avaliacao,
                                    font=("Helvetica", 12), bg="#008CBA", fg="white")
        self.btn_iniciar.grid(row=1, column=1, pady=5, padx=(0, 500), sticky="e")  # Ajuste na opção padx

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

        # Frame retangular para feedback
        self.frame_feedback = tk.Frame(self.frame_detalhes_pontuacao, bg="white", width=500, height=200)
        self.frame_feedback.grid(row=3, column=0, padx=(20, 20), pady=5, sticky="n")

        self.texto_avaliado = tk.Text(self.frame_detalhes_pontuacao, wrap="word", height=10, width=70, bg="white", font=("Helvetica", 10))
        self.texto_avaliado.grid(row=4, column=0, columnspan=2, pady=10, padx=(20, 20))  # Ajuste na opção padx

        # Componente de texto para exibir o log
        self.texto_log = tk.Text(self.frame_detalhes_pontuacao, wrap="word", height=15, width=50, bg="white", font=("Helvetica", 10))
        self.texto_log.grid(row=1, column=4, padx=(20, 20), pady=5, sticky="n")

        # Adicione um botão para exibir o log
        self.btn_exibir_log = tk.Button(self.frame_detalhes_pontuacao, text="Exibir Log", command=self.exibir_log,
                                       font=("Helvetica", 12), bg="#008CBA", fg="white")
        self.btn_exibir_log.grid(row=2, column=4, pady=5, padx=(20, 20), sticky="e")



        # Configurar o grid para que os elementos possam expandir para ocupar o espaço disponível
        for i in range(4):
            self.grid_rowconfigure(i, weight=1)
            self.grid_columnconfigure(0, weight=1)
    

    def limpar_feedback(self):
        # Destrói todos os widgets no frame de feedback
        for widget in self.frame_feedback.winfo_children():
            widget.destroy()        

    def selecionar_arquivo(self):
        caminho_arquivo = filedialog.askopenfilename(filetypes=[("Arquivos DOCX", "*.docx")])
        if caminho_arquivo:
            self.caminho_arquivo = caminho_arquivo
            self.lbl_pontuacao_total.config(text="Pontuação: N/A")
            self.atualizar_detalhes_critérios({})
            
            # Limpar o conteúdo do Text Widget
            self.texto_avaliado.delete('1.0', tk.END)

    def iniciar_avaliacao(self):
        if hasattr(self, 'caminho_arquivo') and self.caminho_arquivo:
            # Verifica se o arquivo tem a extensão .docx
            if not self.caminho_arquivo.lower().endswith('.docx'):
                messagebox.showinfo("Aviso", "Selecione um arquivo DOCX válido.")
                return

            self.tempo_inicio = time.time()

            # Importa a classe apropriada com base no perfil
            if self.var_perfil.get() == "Resenha":
                self.avaliador = AvaliadorTexto(perfil="Resenha")
            elif self.var_perfil.get() == "Artigo":
                self.avaliador = AvaliadorArtigo(perfil="Artigo")

            # Avalia o arquivo e obtém a tupla de retorno
            resultado_avaliacao = self.avaliador.avaliar_texto(self.caminho_arquivo)

            # Extrai as pontuações detalhadas e o texto avaliado da tupla
            pontuacoes_detalhadas, texto_avaliado = resultado_avaliacao

            # Exibe os detalhes dos critérios
            self.atualizar_detalhes_critérios(pontuacoes_detalhadas)

            # Limpa o conteúdo anterior
            self.texto_avaliado.delete('1.0', tk.END)

            # Adiciona o texto ao widget de texto
            self.texto_avaliado.insert(tk.END, texto_avaliado)

            # Chama o método contar_erros_ortografia para obter as palavras incorretas
            self.avaliador.contar_erros_ortografia(texto_avaliado)

            # Itera sobre as palavras incorretas e aplica a formatação ao texto
            for palavra_incorreta in self.avaliador.palavras_incorretas:
                start_index = '1.0'
                while True:
                    start_index = self.texto_avaliado.search(palavra_incorreta, start_index, stopindex=tk.END)
                    if not start_index:
                        break
                    end_index = f'{start_index}+{len(palavra_incorreta)}c'
                    self.texto_avaliado.tag_add('incorreta', start_index, end_index)
                    start_index = end_index

            # Aplica a formatação desejada às palavras incorretas
            self.texto_avaliado.tag_config('incorreta', foreground='red', underline=True)

            # Exibe a interface de feedback com as palavras incorretas destacadas
            self.exibir_interface_feedback(pontuacoes_detalhadas)

        else:
            messagebox.showinfo("Aviso", "Selecione um arquivo antes de iniciar a avaliação.")

    def exibir_log(self):
        try:
            with open("log.txt", "r") as arquivo_log:
                conteudo_log = arquivo_log.read()
                self.texto_log.delete('1.0', tk.END)  # Limpar o conteúdo anterior
                self.texto_log.insert(tk.END, conteudo_log)
        except FileNotFoundError:
            messagebox.showinfo("Aviso", "O arquivo de log não foi encontrado.")


    def avaliar_arquivo(self, caminho_arquivo):
        doc = Document(caminho_arquivo)
        # Avalia o arquivo e obtém a tupla de retorno
        resultado_avaliacao = self.avaliador.avaliar_texto(caminho_arquivo)

        # Extrai as pontuações detalhadas e o texto avaliado da tupla
        pontuacoes_detalhadas, texto_avaliado = resultado_avaliacao

        # Exibe os detalhes da pontuação total
        pontuacao_total = sum(pontuacao['pontuacao'] for pontuacao in pontuacoes_detalhadas.values())
        self.lbl_pontuacao_total.config(text=f"Pontuação: {pontuacao_total:.2f}")

        # Exibe os detalhes dos critérios
        self.atualizar_detalhes_critérios(pontuacoes_detalhadas)

        # Exibe o texto avaliado no widget de texto
        self.texto_avaliado.delete('1.0', tk.END)  # Limpa o conteúdo anterior
        self.texto_avaliado.insert(tk.END, texto_avaliado)

        # Acessa a lista de palavras incorretas e destaca no texto avaliado
        for palavra_incorreta in self.avaliador.palavras_incorretas:
            self.destacar_palavra_incorreta(palavra_incorreta)
   
    def destacar_palavra_incorreta(self, palavra_incorreta):
        # Encontrar todas as ocorrências da palavra incorreta no texto avaliado
        start_index = '1.0'
        while True:
            start_index = self.texto_avaliado.search(palavra_incorreta, start_index, tk.END)
            if not start_index:
                break

            end_index = f'{start_index}+{len(palavra_incorreta)}c'
            self.texto_avaliado.tag_add('incorreta', start_index, end_index)
            start_index = end_index

        # Aplicar estilo para destacar a palavra incorreta
        self.texto_avaliado.tag_config('incorreta', foreground='red', font=('Helvetica', 10, 'bold'))

    def atualizar_detalhes_critérios(self, pontuacoes_detalhadas):
        # Limpar widgets antigos no frame_critérios
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
            lbl_pontuacao = tk.Label(self.frame_critérios, text=f" {pontuacao['pontuacao']:.2f}", bg="#F0F0F0",
                                    font=("Helvetica", 12))
            lbl_pontuacao.grid(row=i, column=1, padx=(0, 20), pady=5, sticky="e")  # Ajuste para alinhar à direita

            # Label para a justificativa do critério
            lbl_justificativa = tk.Label(self.frame_critérios, text=pontuacao['justificativa'], bg="#F0F0F0",
                                        font=("Helvetica", 10))
            lbl_justificativa.grid(row=i, column=2, padx=20, pady=5, sticky="w", columnspan=2)  # Ajuste para alinhar à esquerda
    

        # Adiciona detalhes de pontuação na área de justificativas
        pontuacao_total = sum(pontuacao['pontuacao'] for pontuacao in pontuacoes_detalhadas.values())
        lbl_pontuacao_total = tk.Label(self.frame_detalhes_pontuacao, text=f"Pontuação: {pontuacao_total:.2f}", bg="#F0F0F0",
                                    font=("Helvetica", 14, "bold"))
        lbl_pontuacao_total.grid(row=0, column=0, columnspan=2, pady=10)
        
        for widget in self.frame_feedback.winfo_children():
            widget.grid_forget()
       
        # Adiciona feedback
        if pontuacao_total > 0:
            feedback = self.obter_feedback(pontuacao_total)
            lbl_feedback = tk.Label(self.frame_feedback, text=f"Feedback: {feedback}",
                                    font=("Helvetica", 10), wraplength=400)
            lbl_feedback.grid(row=3, column=1, columnspan=4, pady=5)

    def obter_feedback(self, pontuacao):
        if pontuacao < 6.0:
            return "Aluno, infelizmente seu trabalho não atingiu nota suficiente. De acordo com os requisitos apresentados, são necessárias muitas melhorias. Verifique a grade de correção para entender as falhas."
        elif 6.0 <= pontuacao <= 7.9:
            return "Aluno, seu trabalho está bom, mas precisa de algumas melhorias em relação aos requisitos de avaliação. Verifique a grade de correção para entender o que precisa ser ajustado para obter uma nota melhor."
        elif 8.0 <= pontuacao <= 9.9:
            return "Aluno, ótimo trabalho! Ele preenche grande parte dos requisitos de avaliação com nota acima da média. Verifique a grade de correção para entender o que precisaria melhorar."
        elif pontuacao >= 10.0:
            return "Parabéns, Aluno, excelente trabalho, cumpre todos os requisitos de avaliação com nota máxima!"
        else:
            return "Feedback não disponível"

if __name__ == "__main__":
    app = InterfaceGrafica()
    app.mainloop()