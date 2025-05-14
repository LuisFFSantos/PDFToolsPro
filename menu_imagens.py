import streamlit as st
import pypdf

from PIL import Image
import tempfile
from pathlib import Path

from utilizadades import pegar_dados_pdf


def exibir_menu_imagens(coluna):
    with coluna:
        st.markdown("""
        # Imagens para PDF
        
        Selecione as imagens para gerar um PDf com elas:
        """)

        imagens = st.file_uploader(
            label='Selecione as imagens que irão para o arquivo PDF...',
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
        )
        if imagens:
            botoes_desativados = False
        else:
            botoes_desativados = True
        clicou_processar = st.button(
            'Clique para processar o arquivo PDF...',
            use_container_width=True,
            disabled=botoes_desativados,
        )
        if clicou_processar:
            dados_pdf = gerar_arquivo_pdf_com_imagens(imagens=imagens)
            nome_arquivo = f'imagens.pdf'
            st.download_button(
                'Clique para fazer download do arquivo PDF...',
                type='primary',
                data=dados_pdf,
                file_name=nome_arquivo,
                mime='application/pdf',
                use_container_width=True,
            )

def gerar_arquivo_pdf_com_imagens(imagens):
    imagens_pillow = []
    for imagem in imagens:
        dados_imagem = Image.open(imagem)
        if dados_imagem.mode == 'RGBA':
            dados_imagem = remover_canal_transparencia(imagem=imagem)
        imagens_pillow.append(dados_imagem)
    
    primeira_imagem = imagens_pillow[0]
    demais_imagens = imagens_pillow[1:]

    with tempfile.TemporaryDirectory() as tempdir:
        nome_arquivo = Path(tempdir) / 'temp.pdf'
        primeira_imagem.save(nome_arquivo, save_all=True, append_images=demais_imagens)
        pdf_imagens = pypdf.PdfReader(nome_arquivo)
    
    escritor = pypdf.PdfWriter()
    for pagina in pdf_imagens.pages:
        pagina_em_branco = escritor.add_blank_page(
            width=pypdf.PaperSize.A4.width,
            height=pypdf.PaperSize.A4.height,
        )
        if pagina.mediabox.top > pagina.mediabox.right:  # Imagem está na vertical
            scale = pagina_em_branco.mediabox.top / pagina.mediabox.top * 0.9
        else:
            scale = pagina_em_branco.mediabox.right / pagina.mediabox.right * 0.9
        tx = (pagina_em_branco.mediabox.right - pagina.mediabox.right * scale) / 2
        ty = (pagina_em_branco.mediabox.top - pagina.mediabox.top * scale) / 2
        transf = pypdf.Transformation().scale(scale).translate(tx=tx, ty=ty)
        pagina_em_branco.merge_transformed_page(pagina, transf, over=True)

    dados_pdf = pegar_dados_pdf(escritor=escritor)
    return dados_pdf



def remover_canal_transparencia(imagem):
    imagem_rgba = Image.open(imagem)
    imagem_rgb = Image.new('RGB', imagem_rgba.size, (255, 255, 255))
    imagem_rgb.paste(imagem_rgba, mask=imagem_rgba.split()[3])
    return imagem_rgb