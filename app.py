import streamlit as st
from streamlit_option_menu import option_menu

import menu_combinar
import menu_extrair
import menu_marca_dagua
import menu_imagens
import menu_organizar
import menu_comprimir
import menu_dividir
import menu_proteger
import menu_remover_senha
import menu_pdf_imagens

st.set_page_config(
    page_title='PDFToolsPro - LTA',
    page_icon='📄',
    layout='wide'
)

with st.sidebar:
    st.title("🛠️ PDFToolsPro - LTA")
    st.caption("Todas as ferramentas PDF em um só lugar")
    st.divider()

    escolha = option_menu(
        menu_title=None,
        options=[
            "Extrair página",
            "Dividir PDF",
            "Organizar PDF",
            "Combinar PDFs",
            "Comprimir PDF",
            "Proteger com senha",
            "Remover senha",
            "Imagens para PDF",
            "PDF para Imagens",
            "Adicionar marca d'água",
        ],
        icons=[
            "file-earmark-pdf-fill",
            "scissors",
            "layout-wtf",
            "plus-square-fill",
            "file-zip-fill",
            "lock-fill",
            "unlock-fill",
            "file-earmark-richtext-fill",
            "images",
            "droplet-fill",
        ],
        default_index=0,
    )

_, col2, _ = st.columns([1, 3, 1])

with col2:
    match escolha:
        case "Extrair página":
            menu_extrair.exibir_menu_extrair(coluna=col2)
        case "Dividir PDF":
            menu_dividir.exibir_menu_dividir(coluna=col2)
        case "Organizar PDF":
            menu_organizar.exibir_menu_organizar(coluna=col2)
        case "Combinar PDFs":
            menu_combinar.exibir_menu_combinar(coluna=col2)
        case "Comprimir PDF":
            menu_comprimir.exibir_menu_comprimir(coluna=col2)
        case "Proteger com senha":
            menu_proteger.exibir_menu_proteger(coluna=col2)
        case "Remover senha":
            menu_remover_senha.exibir_menu_remover_senha(coluna=col2)
        case "Imagens para PDF":
            menu_imagens.exibir_menu_imagens(coluna=col2)
        case "PDF para Imagens":
            menu_pdf_imagens.exibir_menu_pdf_imagens(coluna=col2)
        case "Adicionar marca d'água":
            menu_marca_dagua.exibir_menu_marca_dagua(coluna=col2)
