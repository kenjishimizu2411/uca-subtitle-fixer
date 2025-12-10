import flet as ft
from src.ui.home_page import SubtitleCorrectorApp
from dotenv import load_dotenv
import os


def main(page: ft.Page):
    # Carrega variáveis de ambiente (Segurança)
    load_dotenv()

    # Verifica se a API KEY existe antes de abrir
    if not os.getenv("GOOGLE_API_KEY"):
        page.add(
            ft.Text(
                "ERRO CRÍTICO: Arquivo .env não configurado ou sem chave!",
                color="red",
                size=30,
            )
        )
        return

    # Inicia a Aplicação
    app = SubtitleCorrectorApp(page)


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
