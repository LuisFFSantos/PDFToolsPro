import streamlit as st
import pypdf

from pathlib import Path
from utilizadades import pegar_dados_pdf


def exibir_menu_marca_dagua(coluna):
    with coluna:
        st.markdown("""
        # Adicionar marca d'água no PDF
        
        Selecione um arquivo PDF e uma marca d'água nos seletores abaixo:
        """)


        arquivo_pdf = st.file_uploader(
            label='Selecione o arquivo PDF...',
            type='pdf',
            accept_multiple_files=False,
        )
        arquivo_marca = st.file_uploader(
            label="Selecione o arquivo contendo a marca d'água...",
            type='pdf',
            accept_multiple_files=False,
        )
        if arquivo_pdf and arquivo_marca:
            botoes_desativados = False
        else:
            botoes_desativados = True
        clicou_processar = st.button(
            'Clique para processar o arquivo PDF...',
            use_container_width=True,
            disabled=botoes_desativados,
        )
        if clicou_processar:
            dados_pdf = adicionar_marca_dagua(arquivo_pdf=arquivo_pdf, arquivo_marca=arquivo_marca)
            nome_arquivo = f'{Path(arquivo_pdf.name).stem}_marca.pdf'
            st.download_button(
                'Clique para fazer download do arquivo PDF...',
                type='primary',
                data=dados_pdf,
                file_name=nome_arquivo,
                mime='application/pdf',
                use_container_width=True,
            )


def adicionar_marca_dagua(arquivo_pdf, arquivo_marca):
    leitor_pdf = pypdf.PdfReader(arquivo_pdf)
    leitor_marca = pypdf.PdfReader(arquivo_marca)
    escritor = pypdf.PdfWriter()

    for pagina in leitor_pdf.pages:
        # Criar uma nova instância da marca d'água a cada iteração
        pagina_marca = leitor_marca.pages[0]

        escala_x = pagina.mediabox.width / pagina_marca.mediabox.width
        escala_y = pagina.mediabox.height / pagina_marca.mediabox.height
        transf = pypdf.Transformation().scale(escala_x, escala_y)

        # Clonamos explicitamente a página para evitar efeitos colaterais
        nova_pagina = pagina  # ou pagina.copy() se estiver usando PyPDF2 mais recente

        nova_pagina.merge_transformed_page(pagina_marca, transf, over=False)
        escritor.add_page(nova_pagina)

    return pegar_dados_pdf(escritor)

