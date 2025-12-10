import os
import pysrt
import webvtt
from pypdf import PdfReader


class FileManager:
    @staticmethod
    def extrair_texto_pdfs(lista_caminhos_pdf):
        texto_completo = ""
        for caminho in lista_caminhos_pdf:
            if not os.path.exists(caminho):
                continue
            try:
                reader = PdfReader(caminho)
                for page in reader.pages:
                    texto_completo += page.extract_text() + "\n"
            except Exception as e:
                print(f"Erro ao ler PDF {caminho}: {e}")
        return texto_completo

    @staticmethod
    def ler_legenda(caminho_arquivo):
        """
        Lê SRT ou VTT e retorna um objeto iterável de legendas.
        Usa Duck Typing: ambos os objetos (pysrt e webvtt) têm o atributo '.text'.
        """
        try:
            if caminho_arquivo.lower().endswith(".srt"):
                return pysrt.open(caminho_arquivo, encoding="utf-8")
            elif caminho_arquivo.lower().endswith(".vtt"):
                return webvtt.read(caminho_arquivo)
            else:
                raise ValueError("Formato não suportado (apenas .srt ou .vtt)")
        except Exception as e:
            raise Exception(f"Falha ao abrir legenda: {e}")

    @staticmethod
    def salvar_legenda(subs, caminho_original, sulfixo="_corrigido"):
        """
        Salva mantendo o formato original.
        """
        base, ext = os.path.splitext(caminho_original)
        novo_caminho = f"{base}{sulfixo}{ext}"

        # O método .save() funciona tanto para pysrt quanto para webvtt!
        # Apenas garantimos o encoding para o SRT.
        if ext.lower() == ".srt":
            subs.save(novo_caminho, encoding="utf-8")
        else:
            subs.save(novo_caminho)  # WebVTT já salva em UTF-8 por padrão

        return novo_caminho
