import nltk
from nltk.tokenize import RegexpTokenizer
from docx import Document
import spacy
from autocorrect import Speller
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import joblib
import enchant
import os

nltk.download('punkt')

class AvaliadorTexto:
    def __init__(self, perfil):
        self.perfil = perfil
        self.nlp = spacy.load('pt_core_news_lg')
        self.spell = Speller(lang='pt')
        self.gpt_model = GPT2LMHeadModel.from_pretrained("gpt2")
        self.gpt_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

        # Caminho para o arquivo de gírias
        caminho_girias = 'girias.txt'

        # Carrega as gírias do arquivo
        self.GIRIAS = self.carregar_girias(caminho_girias)

        # Constantes
        self.PONTUACAO_INICIAL = {
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

        # Contadores de erros ortográficos e gramaticais
        self.erros_ortograficos = 0
        self.erros_gramaticais = 0

        # Caminho relativo ao diretório atual
        caminho_pos_tagger = 'pos_tagger_models/POS_tagger_brill.pkl'

        # Carrega o arquivo
        self.pos_tagger = joblib.load(caminho_pos_tagger)

    def carregar_girias(self, caminho):
        if os.path.exists(caminho):
            with open(caminho, 'r', encoding='utf-8') as file:
                return [linha.strip() for linha in file.readlines()]
        else:
            print(f"Arquivo de gírias não encontrado em {caminho}. Usando lista vazia de gírias.")
            return []

    def word_tokenize_pt(self, text):
        tokenizer = RegexpTokenizer(r'\w+')
        return tokenizer.tokenize(text)

    def verificar_estilo(self, normal_style):
        return sum(self.ESTILOS[estilo] if getattr(normal_style, estilo) != valor else 0
                   for estilo, valor in self.ESTILOS.items())

    def contar_erros_ortografia(self, texto_completo):
        # Obtém uma lista de palavras originais
        palavras_originais = texto_completo.split()

        # Usa o Speller para corrigir as palavras
        palavras_corrigidas = [self.spell(palavra) for palavra in palavras_originais]

        # Compara as palavras originais com as corrigidas para contar os erros
        erros_ortografia = sum(1 for palavra_orig, palavra_corrigida in zip(palavras_originais, palavras_corrigidas) if
                               palavra_orig != palavra_corrigida)

        return erros_ortografia

    def contar_erros_gramatica(self, texto):
        # Modificando a função para usar o POS-tagger em vez do NLTK Punkt
        tagged_words = self.pos_tagger.tag(self.word_tokenize_pt(texto.text))
        erros_gramatica = sum(1 for _, tag in tagged_words if tag == 'X')

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

        if not (7 <= num_linhas <= 30):
            pontuacao -= 0.5

        return max(0, pontuacao)

    def avaliar_citacoes(self, doc):
        pontuacao = self.PONTUACAO_INICIAL['Citacoes']

        citacoes_presentes = any(
            ('"' in p.text and '(' in p.text and ')' in p.text) or
            ('(' in p.text and ')' in p.text)
            for p in doc.paragraphs
        )

        if not citacoes_presentes:
            pontuacao -= 1.0

        return max(0, pontuacao)

    def avaliar_lingua_portuguesa(self, doc):
        pontuacao_maxima = self.PONTUACAO_INICIAL['Lingua_Portuguesa']
        pontuacao = pontuacao_maxima

        texto_completo = ' '.join(paragrafo.text for paragrafo in doc.paragraphs)
        doc_spacy = self.nlp(texto_completo)

        print("Texto Completo:", texto_completo)  # Adicionado para verificar o texto completo
        print("Gírias presentes:", any(giria in texto_completo for giria in self.GIRIAS))  # Adicionado para verificar a presença de gírias

        if any(giria in texto_completo for giria in self.GIRIAS):
            pontuacao -= 0.1  # Desconto de 0.1 se houver gírias
            print("Desconto por gírias aplicado. Pontuação após desconto:", pontuacao)

        erros_ortografia = self.contar_erros_ortografia(texto_completo)
        erros_gramatica = self.contar_erros_gramatica(doc_spacy)

        print("Erros ortográficos:", erros_ortografia)  # Adicionado para verificar a contagem de erros ortográficos
        print("Erros gramaticais:", erros_gramatica)  # Adicionado para verificar a contagem de erros gramaticais

        # Ajuste dos descontos por erros ortográficos
        if 1 <= erros_ortografia <= 10:
            pontuacao -= 0.1
            print("Desconto de 0.1 por erros ortográficos aplicado.")
        elif 11 <= erros_ortografia <= 20:
            pontuacao -= 0.2
            print("Desconto de 0.2 por erros ortográficos aplicado.")
        elif erros_ortografia == 0:
            print("Nenhum erro ortográfico encontrado. Nenhum desconto aplicado.")

        # Ajuste dos descontos por erros gramaticais
        if 1 <= erros_gramatica <= 10:
            pontuacao -= 0.1
            print("Desconto de 0.1 por erros gramaticais aplicado.")
        elif 11 <= erros_gramatica <= 20:
            pontuacao -= 0.2
            print("Desconto de 0.2 por erros gramaticais aplicado.")
        elif erros_gramatica == 0:
            print("Nenhum erro gramatical encontrado. Nenhum desconto aplicado.")

        # Imprimir valores intermediários
        print("Pontuação antes dos descontos:", pontuacao)
        print("Desconto por erros ortográficos:", 0.1 if 1 <= erros_ortografia <= 10 else 0.2)
        print("Desconto por erros gramaticais:", 0.1 if 1 <= erros_gramatica <= 10 else 0.2)

        # Limita a pontuação ao valor máximo definido
        pontuacao = max(0, min(pontuacao, pontuacao_maxima))
        print("Pontuação final:", pontuacao)  # Adicionado para verificar a pontuação final

        return pontuacao
    
    def avaliar_adequacao(self, doc):
        pontuacao = self.PONTUACAO_INICIAL['Adequacao']

        for paragrafo in doc.paragraphs:
            doc_spacy = self.nlp(paragrafo.text)

            gpt_input = "Avalie a adequacao do seguinte texto: " + paragrafo.text
            gpt_output, pontuacao_adequacao = self.gpt_avaliar_coerencia(gpt_input, paragrafo.text)

            pontuacao -= pontuacao_adequacao

        return max(0, pontuacao)

    def gpt_avaliar_coerencia(self, input_text, texto_original):
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

        # Avaliar a adequação aos critérios e descontar pontos se necessário
        pontuacao_adequacao = self.avaliar_adequacao_tema(decoded_output, texto_original)
        pontuacao -= pontuacao_adequacao['tema']
        pontuacao -= pontuacao_adequacao['atendimento']
        pontuacao -= pontuacao_adequacao['genero']
        pontuacao -= pontuacao_adequacao['argumentacao']
        pontuacao -= pontuacao_adequacao['exemplificacao']

        return decoded_output, pontuacao_adequacao
    
    def avaliar_adequacao_tema(self, texto_gerado, texto_original):
        # Implemente a lógica para avaliar a adequação aos critérios comparando os dois textos
        # Retorna um dicionário com os descontos nos pontos para cada critério

        descontos = {
            'tema': 0.0,
            'atendimento': 0.0,
            'genero': 0.0,
            'argumentacao': 0.0,
            'exemplificacao': 0.0
        }

        # Lógica para avaliar cada critério e aplicar os descontos
        if self.criterio_tem_erro(texto_gerado, 'tema'):
            descontos['tema'] = 1.0

        if self.criterio_tem_erro(texto_gerado, 'atendimento'):
            descontos['atendimento'] = 1.0

        if self.criterio_tem_erro(texto_gerado, 'genero'):
            descontos['genero'] = 1.0

        if self.criterio_tem_erro(texto_gerado, 'argumentacao'):
            descontos['argumentacao'] = 0.5

        if self.criterio_tem_erro(texto_gerado, 'exemplificacao'):
            descontos['exemplificacao'] = 0.5

        return descontos

    def criterio_tem_erro(texto, criterio):
        # Implementação da lógica para verificar se há erro no texto relacionado ao critério
        # Retorna True se houver erro, False caso contrário
        # Esta é uma implementação simplificada; você pode ajustar conforme necessário.
        return criterio.lower() in texto.lower()  # Verifica se a palavra-chave do critério está presente no texto


    def gpt_avaliar_coerencia(self, input_text, texto_original):
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

        # Avaliar a adequação aos critérios e descontar pontos se necessário
        pontuacao_adequacao = self.avaliar_adequacao_tema(decoded_output, texto_original)
        pontuacao -= pontuacao_adequacao['tema']
        pontuacao -= pontuacao_adequacao['atendimento']
        pontuacao -= pontuacao_adequacao['genero']
        pontuacao -= pontuacao_adequacao['argumentacao']
        pontuacao -= pontuacao_adequacao['exemplificacao']

        return decoded_output, pontuacao_adequacao

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
            avaliacao_funcao = getattr(self,
                                       f'avaliar_{criterio.lower().replace(" ", "_").replace("ções", "coes").replace("ção", "cao")}')
            pontuacao = avaliacao_funcao(doc)

            # Adicione uma justificativa adequada para cada critério
            justificativa = self.obter_justificativa(criterio, pontuacao)

            pontuacoes_detalhadas[criterio] = {
                'pontuacao': pontuacao,
                'justificativa': justificativa,
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