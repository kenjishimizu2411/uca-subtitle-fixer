import google.generativeai as genai
import re

# --- CONFIGURAÇÃO: DICIONÁRIO DE PRODUTOS DA ALTERDATA (FORÇA BRUTA) ---
GLOSSARIO_FORCE = {
    "Alterdata": [
        r"alter\s*data",
        r"alta\s*data",
        r"outer\s*data",
        r"auto\s*data",
        r"outra\s*data",
    ],
    "Spice Desktop": [
        r"spi\s*se",
        r"spa\s*desktop",
        r"os\s*pais",
        r"os\s*pães",
        r"spice\s*desktop",
        r"space\s*desktop",
    ],
    "o Spice": [r"o\s*pais", r"o\s*pai", r"o\s*spi", r"no\s*spi", r"os\s*pais"],
    "Comanda": [r"comando"],
    "Bimer": [r"bimer", r"bimmer", r"bima", r"bime"],
    "Pack": [r"pack", r"pec", r"péq"],
    "Shop": [r"shop", r"xope"],
    "BI": [r"\bbi\b"],
    "House Mix": [r"house\s*mix"],
}


class AIService:
    def __init__(self, api_key_usuario):
        if not api_key_usuario:
            raise ValueError("API Key não fornecida!")

        genai.configure(api_key=api_key_usuario)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def _aplicar_pente_fino(self, texto):
        """
        Garantia final via código (Regex) para Marcas e Português Básico.
        """
        texto_limpo = texto

        # --- 1. CORREÇÃO DE PORTUGUÊS VÍCIO DE TRANSCRIÇÃO ---
        regras_gramaticais = [
            (r"(?i)\bvae\b", "vai"),
            (r"(?i)\beh\b", "é"),
            (r"(?i)\btah\b", "tá"),
            (r"(?i)\bnaum\b", "não"),
            (r"(?i)\bakie\b", "aqui"),
            (r"(?i)\bvc\b", "você"),
            (r"(?i)\btb\b", "também"),
            # Novos erros comuns detectados
            (r"(?i)moztrar", "mostrar"),
            (r"(?i)figurra", "figura"),
        ]

        for erro, correcao in regras_gramaticais:
            texto_limpo = re.sub(erro, correcao, texto_limpo)

        # --- 2. APLICAÇÃO DO GLOSSÁRIO TÉCNICO ---
        for termo_correto, lista_erros in GLOSSARIO_FORCE.items():
            for erro_regex in lista_erros:
                pattern = f"(?i)\\b({erro_regex})\\b"
                try:
                    texto_limpo = re.sub(pattern, termo_correto, texto_limpo)
                except Exception:
                    continue
        return texto_limpo

    def corrigir_srt_completo(self, srt_content, contexto_pdfs):
        """
        Prompt Refinado: Foco total em Ortografia e Termos
        """
        prompt = f"""
        ### SUAS PERSONAS:
        1. **Revisor Gramatical Sênior:** Você tem "TOC" com erros ortográficos. "Moztrar" e "figurra" são inaceitáveis.
        2. **Especialista Técnico Alterdata:** Você conhece os produtos (Spice, Bimer, Pack) e corrige seus nomes.

        ### TAREFA:
        Corrigir este arquivo SRT gerado por uma transcrição de áudio de baixa qualidade.
        
        ### REGRAS DE OURO (Siga nesta ordem):
        1. **ORTOGRAFIA AGRESSIVA:** O texto original está cheio de erros como "moztrar" (mostrar), "figurra" (figura), "vae" (vai). CORRIJA TODOS. Não deixe passar nenhum erro de português.
        2. **TERMOS TÉCNICOS:**
           - "Alter data" -> "Alterdata"
           - "Os pais" / "Spi se" -> "Spice"
           - "Comando" -> "Comanda"
        3. **ESTRUTURA:** Mantenha os timestamps intactos.

        ### EXEMPLOS DE CORREÇÃO:
        [Errado] "vou te moztrar a figurra do comando alter data"
        [Certo]  "vou te mostrar a figura do Comanda Alterdata"

        [Errado] "configurar os pais eh facil"
        [Certo]  "configurar o Spice é fácil"

        ### TEXTO PARA CORRIGIR:
        {srt_content}
        """

        try:
            # Temperatura 0.4: Mais liberdade para corrigir erros ortográficos bizarros
            response = self.model.generate_content(
                prompt, generation_config={"temperature": 0.4}
            )
            texto_ia = response.text.strip()

            # Aplica o Pente Fino (Python) para garantir o que a IA deixar passar
            return self._aplicar_pente_fino(texto_ia)

        except Exception as e:
            print(f"Erro IA: {e}")
            return self._aplicar_pente_fino(srt_content)
