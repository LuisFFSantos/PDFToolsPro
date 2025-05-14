import streamlit as st
import pypdf

from utilizadades import pegar_dados_pdf


def exibir_menu_combinar(coluna):
    with coluna:
        st.markdown("""
        # Combinar PDFs
        
        Selecione dois ou mais arquivos PDF para combinar:
        """)

        arquivos_pdf = st.file_uploader(
            label='Selecione os arquivos PDF para combinar...',
            type='pdf',
            accept_multiple_files=True,
        )
        if arquivos_pdf:
            botoes_desativados = False
        else:
            botoes_desativados = True
        clicou_processar = st.button(
            'Clique para processar o arquivo PDF...',
            use_container_width=True,
            disabled=botoes_desativados,
        )
        if clicou_processar:
            dados_pdf = combinar_arquivos_pdf(arquivos_pdf=arquivos_pdf)
            nome_arquivo = f'combinado.pdf'
            st.download_button(
                'Clique para fazer download do arquivo PDF...',
                type='primary',
                data=dados_pdf,
                file_name=nome_arquivo,
                mime='application/pdf',
                use_container_width=True,
            )

def combinar_arquivos_pdf(arquivos_pdf):
    escritor = pypdf.PdfWriter()
    for arquivo_pdf in arquivos_pdf:
        leitor = pypdf.PdfReader(arquivo_pdf)
        for pagina in leitor.pages:
            escritor.add_page(pagina)
    dados_pdf = pegar_dados_pdf(escritor=escritor)
    return dados_pdf
