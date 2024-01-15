from docx import Document
import spacy
from autocorrect import Speller
from transformers import GPT2LMHeadModel, GPT2Tokenizer

class AvaliadorTexto:
    def __init__(self, perfil):
        self.perfil = perfil
        self.nlp = spacy.load('pt_core_news_lg')
        self.spell = Speller(lang='pt')
        self.gpt_model = GPT2LMHeadModel.from_pretrained("gpt2")
        self.gpt_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

        # Constantes
        self.PONTUACAO_INICIAL = {
            'Formatacao': 0.5,
            'Linhas': 0.5,
            'Citacoes': 1.0,
            'Lingua_Portuguesa': 2.0,
            'Adequacao': 6.0
        }

        self.PESOS = {
            'Formatacao': 0.5,
            'Linhas': 0.5,
            'Citacoes': 1.0,
            'Lingua_Portuguesa': 2.0,
            'Adequacao': 6.0
        }

        self.ESTILOS = {
            'arial': 0.1,
            12: 0.1,
            1.5: 0.1,
            1.25: 0.1,
            3: 0.1
        }

        self.GIRIAS = ["cara", "mano", "pra", "to"]

        # Contadores de erros ortográficos e gramaticais
        self.erros_ortograficos = 0
        self.erros_gramaticais = 0

    def verificar_estilo(self, normal_style):
        return sum(self.ESTILOS[estilo] if getattr(normal_style, estilo) != valor else 0
                   for estilo, valor in self.ESTILOS.items())

    def contar_erros_ortografia(self, texto_completo):
        # Obtém uma lista de palavras originais
        palavras_originais = texto_completo.split()

        # Usa o Speller para corrigir as palavras
        palavras_corrigidas = [self.spell(palavra) for palavra in palavras_originais]

        # Compara as palavras originais com as corrigidas para contar os erros
        erros_ortografia = sum(1 for palavra_orig, palavra_corrigida in zip(palavras_originais, palavras_corrigidas) if palavra_orig != palavra_corrigida)

        return erros_ortografia

    def contar_erros_gramatica(self, doc_spacy):
        # Conta os tokens com a classe gramatical 'X' (erros gramaticais)
        erros_gramatica = sum(1 for token in doc_spacy if token.pos_ == 'X')

        return erros_gramatica

    def avaliar_formatacao(self, doc):
        pontuacao = self.PONTUACAO_INICIAL['Formatacao']

        normal_style = getattr(doc.styles, 'Normal', None)
        if normal_style:
            pontuacao -= self.verificar_estilo(normal_style)

        return max(0, pontuacao)

    def avaliar_linhas(self, doc):
        pontuacao = self.PONTUACAO_INICIAL['Linhas']

        num_linhas = len([p for p in doc.paragraphs if p.text.strip()])

        if 7 <= num_linhas <= 30:
            pontuacao += self.PESOS['Linhas']
        else:
            pontuacao -= self.PESOS['Linhas']

        return max(0, pontuacao)

    def avaliar_citacoes(self, doc):
        pontuacao = self.PONTUACAO_INICIAL['Citacoes']

        citacoes_presentes = any(
            ('"' in p.text and '(' in p.text and ')' in p.text) or
            ('(' in p.text and ')' in p.text)
            for p in doc.paragraphs
        )

        if not citacoes_presentes:
            pontuacao -= self.PESOS['Citacoes']

        return max(0, pontuacao)

    def avaliar_lingua_portuguesa(self, doc):
        pontuacao_maxima = self.PONTUACAO_INICIAL['Lingua_Portuguesa']
        pontuacao = pontuacao_maxima

        texto_completo = ' '.join(paragrafo.text for paragrafo in doc.paragraphs)
        doc_spacy = self.nlp(texto_completo)

        if any(giria in texto_completo for giria in self.GIRIAS):
            pontuacao -= 0.2  # Desconto de 0.2 se houver gírias

        erros_ortografia = self.contar_erros_ortografia(texto_completo)
        erros_gramatica = self.contar_erros_gramatica(doc_spacy)

        # Calcula o desconto com base no número de erros
        desconto_erros = 0.0
        if 1 <= erros_ortografia <= 10:
            desconto_erros += 0.1
        elif 11 <= erros_ortografia <= 20:
            desconto_erros += 0.2

        if 1 <= erros_gramatica <= 10:
            desconto_erros += 0.1
        elif 11 <= erros_gramatica <= 20:
            desconto_erros += 0.2

        # Aplica o desconto diretamente na pontuação inicial
        pontuacao -= desconto_erros

        # Limita a pontuação ao valor máximo de 2.0
        pontuacao = max(0, pontuacao_maxima - desconto_erros)

        return pontuacao

    def avaliar_adequacao(self, doc):
        pontuacao = self.PONTUACAO_INICIAL['Adequacao']

        for paragrafo in doc.paragraphs:
            doc_spacy = self.nlp(paragrafo.text)

            gpt_input = "Avalie a adequacao do seguinte texto: " + paragrafo.text
            gpt_output = self.gpt_avaliar_coerencia(gpt_input)

            pontuacao_ajuste = self.analisar_gpt_output(gpt_output)
            pontuacao -= pontuacao_ajuste

            if 'tema' in paragrafo.text.lower():
                pontuacao += self.PESOS['Adequacao'] * 1.0

            if 'atendimento a proposta' in paragrafo.text.lower():
                pontuacao += self.PESOS['Adequacao'] * 1.0

        return max(0, pontuacao)

    def analisar_gpt_output(self, gpt_output):
        num_palavras = len(gpt_output.split())
        num_frases_coerentes = gpt_output.count('.') + gpt_output.count('!') + gpt_output.count('?')

        pontuacao = 0.0

        if num_palavras > 50:
            pontuacao += 0.5

        if num_frases_coerentes > 3:
            pontuacao += 0.5

        return pontuacao

    def gpt_avaliar_coerencia(self, input_text):
        input_ids = self.gpt_tokenizer.encode(input_text, return_tensors="pt")
        eos_token_id = self.gpt_tokenizer.eos_token_id
        print(f"ID do token de fim de sequencia: {eos_token_id}")
        
        output = self.gpt_model.generate(
            input_ids,
            max_length=263,
            num_beams=5,
            no_repeat_ngram_size=2,
            top_k=50,
            top_p=0.95,
            temperature=0.7,
            pad_token_id=50256
        )
        decoded_output = self.gpt_tokenizer.decode(output[0], skip_special_tokens=True)
        return decoded_output

    def imprimir_analise(self, pontuacoes):
        print("Analise de Pontuacoes:")
        print("----------------------")
        print("{:<25} {:<10}".format('Criterio', 'Pontuacao'))
        print("----------------------")

        for crit, pont in pontuacoes.items():
            print("{:<25} {:<10}".format(crit, pont))

        print("----------------------")
        print("Pontuacao Total: {:<10}".format(sum(pontuacoes.values())))

    def avaliar_texto(self, caminho_arquivo):
        doc = Document(caminho_arquivo)
        pontuacoes_detalhadas = {}

        for criterio in self.PONTUACAO_INICIAL:
            avaliacao_funcao = getattr(self, f'avaliar_{criterio.lower().replace(" ", "_").replace("ções", "coes").replace("ção", "cao")}')
            pontuacao = avaliacao_funcao(doc) * self.PESOS[criterio]

            # Adicione uma justificativa adequada para cada critério
            justificativa = self.obter_justificativa(criterio, pontuacao)

            pontuacoes_detalhadas[criterio] = {
                'pontuacao': pontuacao,
                'justificativa': justificativa
            }

        pontuacao_total = sum(pontuacao['pontuacao'] for pontuacao in pontuacoes_detalhadas.values())

        # Inclua os contadores de erros na justificativa
        justificativa_erros = f"Erros ortográficos: {self.erros_ortograficos}\nErros gramaticais: {self.erros_gramaticais}"
        pontuacoes_detalhadas['erros'] = {
            'pontuacao': 0,  # Não contribui para a pontuação total
            'justificativa': justificativa_erros
        }

        return pontuacoes_detalhadas

    def obter_justificativa(self, criterio, pontuacao):
        if criterio == 'Formatacao':
            if pontuacao > 0.5:
                return 'A formatação está boa.'
            else:
                return 'Problemas na formatação.'
        elif criterio == 'Linhas':
            if pontuacao > 0.5:
                return 'Número adequado de linhas.'
            else:
                return 'Número de linhas inadequado.'
        elif criterio == 'Citacoes':
            if pontuacao > 0.5:
                return 'Uso adequado de citações.'
            else:
                return 'Problemas com as citações.'
        elif criterio == 'Lingua_Portuguesa':
            if pontuacao > 1.5:
                return 'Bom uso da língua portuguesa.'
            else:
                return 'Problemas no uso da língua portuguesa.'
        elif criterio == 'Adequacao':
            if pontuacao > 3.0:
                return 'Texto adequadamente focado no tema.'
            else:
                return 'Problemas de adequação ao tema.'

        # Se nenhum critério correspondente for encontrado, retorna uma mensagem padrão
        return 'Justificativa não disponível para este critério.'
