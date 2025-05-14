import streamlit as st
import pypdf

from pathlib import Path
from utilizadades import pegar_dados_pdf


def exibir_menu_extrair(coluna):
    with coluna:
        st.markdown("""
        # Extrair páginas do PDF

        Selecione o arquivo PDF e escolha as páginas a extrair:
        """)

        arquivo_pdf = st.file_uploader(
            label='Selecione o arquivo PDF...',
            type='pdf',
            accept_multiple_files=False,
        )

        modo = st.radio("Modo de seleção de páginas:", ["Intervalo", "Avulsas"])

        if arquivo_pdf:
            leitor = pypdf.PdfReader(arquivo_pdf)
            total_paginas = len(leitor.pages)
            botoes_desativados = False
        else:
            total_paginas = 1
            botoes_desativados = True

        paginas = []

        # Entrada para nome personalizado do arquivo
        nome_personalizado = st.text_input(
            "Nome do arquivo (sem .pdf)",
            value="arquivo_extraido",
            max_chars=50,
            disabled=botoes_desativados
        )

        if modo == "Intervalo" and not botoes_desativados:
            col1, col2 = st.columns(2)
            with col1:
                pagina_inicial = st.number_input(
                    'Página inicial',
                    min_value=1,
                    max_value=total_paginas,
                    value=1,
                    step=1
                )
            with col2:
                pagina_final = st.number_input(
                    'Página final',
                    min_value=pagina_inicial,
                    max_value=total_paginas,
                    value=pagina_inicial,
                    step=1
                )
            paginas = list(range(int(pagina_inicial), int(pagina_final) + 1))

        elif modo == "Avulsas":
            input_paginas = st.text_input("Digite as páginas separadas por vírgula (ex: 1, 3, 5)", disabled=botoes_desativados)
            try:
                paginas = [int(p.strip()) for p in input_paginas.split(",") if p.strip().isdigit()]
            except ValueError:
                paginas = []

        clicou_processar = st.button(
            'Clique para processar o PDF...',
            use_container_width=True,
            disabled=botoes_desativados,
        )

        if clicou_processar:
            dados_pdf = extrair_paginas_personalizadas(arquivo_pdf, paginas)
            if not dados_pdf:
                st.warning("Páginas inválidas ou não encontradas.")
                return

            nome_base = nome_personalizado.strip().replace(" ", "_") or "arquivo_extraido"

            if modo == "Intervalo":
                nome_arquivo = f"{nome_base}_pgs_{pagina_inicial}a{pagina_final}.pdf"
            else:
                nome_arquivo = f"{nome_base}_pgs_{len(paginas)}paginas.pdf"

            st.download_button(
                'Clique para fazer download do PDF extraído...',
                type='primary',
                data=dados_pdf,
                file_name=nome_arquivo,
                mime='application/pdf',
                use_container_width=True,
            )


def extrair_paginas_pdf(arquivo_pdf, pagina_inicial, pagina_final):
    leitor = pypdf.PdfReader(arquivo_pdf)
    escritor = pypdf.PdfWriter()

    try:
        for i in range(int(pagina_inicial) - 1, int(pagina_final)):
            escritor.add_page(leitor.pages[i])
    except IndexError:
        return None

    return pegar_dados_pdf(escritor=escritor)


def extrair_paginas_personalizadas(arquivo_pdf, paginas):
    leitor = pypdf.PdfReader(arquivo_pdf)
    escritor = pypdf.PdfWriter()

    total_paginas = len(leitor.pages)
    paginas_validas = [p for p in paginas if 1 <= p <= total_paginas]

    if not paginas_validas:
        return None

    for p in paginas_validas:
        escritor.add_page(leitor.pages[p - 1])

    return pegar_dados_pdf(escritor)



