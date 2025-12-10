import flet as ft
import os
import sys
import time
from src.services.file_manager import FileManager
from src.services.ai_service import AIService


def resource_path(relative_path):
    """Obtém o caminho absoluto para recursos, funcionando para dev e para PyInstaller"""
    try:
        # PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# --- CORES E DESIGN (PALETA UCA REFINADA) ---
UCA_PURPLE = "#482174"  # A cor oficial
UCA_PURPLE_BORDER = "#7c4dff"
UCA_BG = "#121212"
UCA_SURFACE = "#1e1e1e"
ACCENT_GREEN = "#00e676"
ACCENT_ORANGE = "#ffab00"
TEXT_WHITE = "#ffffff"
TEXT_GREY = "#e0e0e0"
BUTTON_BG = "#262626"


class SubtitleCorrectorApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()

        # --- ESTADO DA APLICAÇÃO ---
        self.folder_path = None
        self.pdf_paths = []
        self.api_key = None  # Aqui guardaremos a chave do usuário

        self.init_components()

    def setup_page(self):
        self.page.title = "UCA - SUBFIX"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = UCA_BG
        self.page.window_maximized = True
        self.page.window_icon = resource_path("assets/logo_uca.ico")
        self.page.padding = 30

    def init_components(self):
        # DIALOGS (Seletores de Arquivo)
        self.pick_srt_folder_dialog = ft.FilePicker(on_result=self.on_folder_result)
        self.pick_pdf_dialog = ft.FilePicker(on_result=self.on_pdf_result)
        self.page.overlay.extend([self.pick_srt_folder_dialog, self.pick_pdf_dialog])

        # NOVO DIALOG: Input de API Key
        self.input_api_field = ft.TextField(
            label="Cole sua Google API Key (Gemini)",
            password=True,
            can_reveal_password=True,
            bgcolor="#262626",
            border_color=UCA_PURPLE_BORDER,
            color="white",
        )
        self.api_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Configuração de Segurança"),
            content=ft.Column(
                [
                    ft.Text(
                        "Para usar a inteligência artificial, insira sua chave gratuita do Google AI Studio.",
                        size=12,
                    ),
                    ft.Divider(height=10, color="transparent"),
                    self.input_api_field,
                ],
                height=120,
                width=400,
            ),
            actions=[
                ft.TextButton(
                    "Cancelar", on_click=lambda e: self.fechar_dialogo_api(False)
                ),
                ft.ElevatedButton(
                    "Salvar Chave",
                    bgcolor=ACCENT_GREEN,
                    color="black",
                    on_click=lambda e: self.fechar_dialogo_api(True),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(self.api_dialog)

        self.card_shadow = ft.BoxShadow(
            spread_radius=0, blur_radius=15, color="#50000000", offset=ft.Offset(0, 8)
        )

        # 6. HEADER COM LOGO
        self.header = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Image(
                            src="logo_uca.png",
                            width=60,
                            height=60,
                            fit=ft.ImageFit.CONTAIN,
                        ),
                        padding=5,
                        bgcolor="white",
                        border_radius=3,
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                "UCA - SubFix",
                                size=28,
                                weight="bold",
                                color=TEXT_WHITE,
                                font_family="Segoe UI",
                            ),
                            ft.Text(
                                "IA integrada para correção de legendas",
                                size=14,
                                color=TEXT_GREY,
                            ),
                        ],
                        spacing=0,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ]
            ),
            bgcolor=UCA_PURPLE,
            padding=5,
            border_radius=15,
            shadow=self.card_shadow,
            border=ft.border.all(1, "#333333"),
        )

        # --- BOTÕES DOS PASSOS ---
        secondary_button_style = ft.ButtonStyle(
            color=TEXT_WHITE,
            bgcolor={"": BUTTON_BG, "hovered": "#353535"},
            side={
                "": ft.BorderSide(1, UCA_PURPLE),
                "hovered": ft.BorderSide(1, UCA_PURPLE_BORDER),
            },
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=10,
            elevation=4,
        )

        # Step 1
        self.btn_folder = ft.ElevatedButton(
            "Selecione uma pasta com legendas",
            icon="folder_open",
            style=secondary_button_style,
            on_click=lambda _: self.pick_srt_folder_dialog.get_directory_path(),
            height=55,
            width=350,
        )
        self.txt_folder = ft.Text("Pendente", color=TEXT_GREY, size=11, italic=True)

        # Step 2
        self.btn_pdf = ft.ElevatedButton(
            "Escolha seus arquivos de contexto (PDF)",
            icon="picture_as_pdf",
            style=secondary_button_style,
            on_click=lambda _: self.pick_pdf_dialog.pick_files(allow_multiple=True),
            height=55,
            width=350,
        )
        self.txt_pdf = ft.Text("Opcional", color=TEXT_GREY, size=11, italic=True)

        # Step 3
        self.btn_api = ft.ElevatedButton(
            "Configurar API Key Google AI Studio",
            icon="key",
            style=secondary_button_style,
            on_click=lambda _: self.abrir_dialogo_api(),  # Agora abre o dialog
            height=55,
            width=350,
        )
        self.txt_api = ft.Text("Obrigatório", color=TEXT_GREY, size=11, italic=True)

        # Botão Ação
        self.btn_processar = ft.ElevatedButton(
            "EXECUTAR CORREÇÃO",
            icon="play_arrow",
            style=ft.ButtonStyle(
                color="#000000",
                bgcolor={"": ACCENT_GREEN, "disabled": "#2b2b2b"},
                elevation={"press": 2, "": 10},
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            height=65,
            width=300,
            disabled=True,
            on_click=self.processar_arquivos,
        )

        # --- DASHBOARD ---
        self.lbl_status = ft.Text(
            "Aguardando início...", color=UCA_PURPLE_BORDER, size=16, weight="bold"
        )
        self.progress_bar = ft.ProgressBar(
            value=0, color=ACCENT_GREEN, bgcolor="#333333", height=4, border_radius=2
        )

        # Log
        self.log_view = ft.ListView(
            expand=True, spacing=4, padding=10, auto_scroll=True
        )
        self.container_log = ft.Container(
            content=self.log_view,
            expand=True,
            bgcolor="#0a0a0a",
            border_radius=8,
            padding=20,
            border=ft.border.all(1, "#333333"),
        )

        # --- MONTAGEM DO LAYOUT ---
        self.page.add(
            self.header,
            ft.Divider(height=15, color="transparent"),
            # CARD DE CONTROLE
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Painel de Controle",
                            weight="bold",
                            color=TEXT_WHITE,
                            size=18,
                        ),
                        ft.Divider(height=10, color="transparent"),
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(
                                            "Step 1", color=ACCENT_GREEN, weight="bold"
                                        ),
                                        self.btn_folder,
                                        self.txt_folder,
                                    ],
                                    expand=1,
                                ),
                                ft.Column(
                                    [
                                        ft.Text(
                                            "Step 2", color=ACCENT_GREEN, weight="bold"
                                        ),
                                        self.btn_pdf,
                                        self.txt_pdf,
                                    ],
                                    expand=1,
                                ),
                                ft.Column(
                                    [
                                        ft.Text(
                                            "Step 3",
                                            color=ACCENT_GREEN,  # Laranja pq é critico
                                            weight="bold",
                                        ),
                                        self.btn_api,
                                        self.txt_api,
                                    ],
                                    expand=1,
                                ),
                            ],
                            spacing=20,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Divider(height=20, color="#333333"),
                        ft.Row(
                            [self.btn_processar], alignment=ft.MainAxisAlignment.CENTER
                        ),
                    ]
                ),
                bgcolor=UCA_SURFACE,
                padding=10,
                border_radius=15,
                shadow=self.card_shadow,
                border=ft.border.all(1, "#2d2d2d"),
            ),
            ft.Divider(height=10, color="transparent"),
            ft.Row([self.lbl_status], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self.progress_bar,
            ft.Divider(height=5, color="transparent"),
            ft.Row(
                [
                    ft.Text(
                        "Log de Execução:", color=TEXT_GREY, size=12, weight="bold"
                    ),
                    ft.Container(expand=True),
                ]
            ),
            # 1. O LOG
            self.container_log,
            # 2. O RODAPÉ
            ft.Container(
                content=ft.Text(
                    "developed by Kenji Shimizu",
                    color="#4DFFFFFF",
                    size=10,
                    italic=True,
                    weight="bold",
                ),
                alignment=ft.alignment.center_right,
                padding=ft.padding.only(top=5, bottom=0),
                on_click=lambda _: self.page.launch_url(
                    "https://github.com/kenjishimizu2411"
                ),
                ink=True,
            ),
        )

    # --- LÓGICA DO DIALOG DE API ---
    def abrir_dialogo_api(self):
        self.api_dialog.open = True
        self.page.update()

    def fechar_dialogo_api(self, salvar):
        if salvar:
            chave = self.input_api_field.value.strip()
            if len(chave) > 10:  # Validação básica
                self.api_key = chave
                self.txt_api.value = "Chave Configurada (Pronto)"
                self.txt_api.color = ACCENT_GREEN
                self.btn_api.icon = "check_circle"
                self.btn_api.style.side = {"": ft.BorderSide(1, ACCENT_GREEN)}
            else:
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("Chave inválida!"), bgcolor="red"
                )
                self.page.snack_bar.open = True

        self.api_dialog.open = False
        self.check_ready()  # Verifica se pode liberar o botão geral
        self.page.update()

    # --- OUTROS EVENTOS ---
    def on_folder_result(self, e):
        if e.path:
            self.folder_path = e.path
            self.txt_folder.value = f"📂 {os.path.basename(e.path)}"
            self.txt_folder.color = ACCENT_GREEN
            self.check_ready()
            self.page.update()

    def on_pdf_result(self, e):
        if e.files:
            self.pdf_paths = [f.path for f in e.files]
            self.txt_pdf.value = f"📄 {len(self.pdf_paths)} arquivos"
            self.txt_pdf.color = ACCENT_GREEN
            self.check_ready()
            self.page.update()

    def check_ready(self):
        # AGORA SÓ LIBERA SE TIVER PASTA **E** API KEY
        if self.folder_path and self.api_key:
            self.btn_processar.disabled = False
        else:
            self.btn_processar.disabled = True
        self.page.update()

    def log(self, msg, color="white"):
        if color == "black":
            color = "white"
        self.log_view.controls.append(
            ft.Text(msg, color=color, font_family="Consolas", size=12)
        )
        self.page.update()

    def processar_arquivos(self, e):
        self.btn_processar.disabled = True
        self.lbl_status.value = "Inicializando Motores..."
        self.page.update()

        try:
            # --- MUDANÇA CRÍTICA: Passamos a chave do usuário para o serviço ---
            ai_service = AIService(self.api_key)

            self.log(">>> Iniciando...", "grey")

            contexto = FileManager.extrair_texto_pdfs(self.pdf_paths)
            self.log(f"Memória Contextual: {len(contexto)} chars.", ACCENT_GREEN)

            exts = (".srt", ".vtt")
            arquivos = [
                f for f in os.listdir(self.folder_path) if f.lower().endswith(exts)
            ]
            total = len(arquivos)

            if total == 0:
                self.log("Erro: Pasta vazia.", "red")
                return

            for i, arquivo in enumerate(arquivos):
                caminho = os.path.join(self.folder_path, arquivo)
                self.lbl_status.value = f"Processando: {arquivo} ({i+1}/{total})"
                self.progress_bar.value = (i) / total
                self.page.update()

                with open(caminho, "r", encoding="utf-8") as f:
                    srt_content = f.read()

                self.log(f"[{i+1}/{total}] Analisando {arquivo}...", "cyan")

                start_ia = time.time()
                try:
                    srt_corrigido = ai_service.corrigir_srt_completo(
                        srt_content, contexto
                    )
                    tempo_ia = time.time() - start_ia

                    srt_limpo = (
                        srt_corrigido.replace("```srt", "").replace("```", "").strip()
                    )
                    novo_nome = arquivo.replace(".srt", "_corrigido.srt").replace(
                        ".vtt", "_corrigido.vtt"
                    )
                    novo_caminho = os.path.join(self.folder_path, novo_nome)

                    with open(novo_caminho, "w", encoding="utf-8") as f_out:
                        f_out.write(srt_limpo)

                    self.log(f"   └── Concluído em {tempo_ia:.1f}s.", ACCENT_GREEN)

                except Exception as err:
                    self.log(f"   └── Falha: {err}", "red")

                time.sleep(2)

            # Finalização
            self.lbl_status.value = "Processo Finalizado com Sucesso!"
            self.lbl_status.color = ACCENT_GREEN
            self.progress_bar.value = 1
            self.log("--------------------------------------------------", "grey")
            self.log("✅ PROCESSO FINALIZADO. ARQUIVOS SALVOS.", ACCENT_GREEN)
            self.page.update()

            snack = ft.SnackBar(
                ft.Text("Sucesso! Correção Finalizada."), bgcolor=ACCENT_GREEN
            )
            self.page.overlay.append(snack)
            snack.open = True

        except Exception as e:
            self.log(f"CRÍTICO: {e}", "red")
        finally:
            self.btn_processar.disabled = False
            self.page.update()
