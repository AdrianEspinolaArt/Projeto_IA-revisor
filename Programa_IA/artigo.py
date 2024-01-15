from docx import Document
import spacy
from autocorrect import Speller
from transformers import GPT2LMHeadModel, GPT2Tokenizer

class AvaliadorArtigo:
    def __init__(self):
        self.nlp = spacy.load('pt_core_news_lg')
        self.spell = Speller(lang='pt')
        self.gpt_model = GPT2LMHeadModel.from_pretrained("gpt2")
        self.gpt_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

        # Constantes específicas para o novo perfil
        self.PONTUACAO_INICIAL = {
            'Criterio1': 0.5,
            'Criterio2': 0.5,
            # Adicione mais critérios conforme necessário
        }

        self.PESOS = {
            'Criterio1': 0.5,
            'Criterio2': 0.5,
            # Adicione mais critérios conforme necessário
        }

        # Adicione outros atributos específicos para o novo perfil

    # Adapte os métodos conforme necessário para avaliar os critérios do novo perfil
    def avaliar_criterio1(self, doc):
        # Lógica para avaliar o Critério 1
        pass

    def avaliar_criterio2(self, doc):
        # Lógica para avaliar o Critério 2
        pass

    # Adicione mais métodos para avaliar outros critérios

    def avaliar_texto(self, caminho_arquivo):
        doc = Document(caminho_arquivo)
        pontuacoes = {}

        for criterio in self.PONTUACAO_INICIAL:
            pontuacoes[criterio] = getattr(self, f'avaliar_{criterio.lower().replace(" ", "_")}')(
                doc) * self.PESOS[criterio]

        self.imprimir_analise(pontuacoes)

        pontuacao_total = sum(pontuacoes.values())
        return pontuacao_total
