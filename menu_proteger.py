import secrets
import streamlit as st
import pypdf
from io import BytesIO

from utilizadades import pegar_dados_pdf

_SENHA_MIN_CHARS = 6


def exibir_menu_proteger(coluna):
    with coluna:
        st.markdown("""
        # Proteger PDF com senha

        Adicione uma senha de abertura ao seu PDF.
        """)

        arquivo_pdf = st.file_uploader(
            label="Selecione o arquivo PDF...",
            type="pdf",
            accept_multiple_files=False,
        )

        desativado = arquivo_pdf is None

        senha = st.text_input("Senha:", type="password", disabled=desativado)
        confirmar = st.text_input("Confirmar senha:", type="password", disabled=desativado)
        nome_saida = st.text_input(
            "Nome do arquivo de saída (sem .pdf)", value="pdf_protegido", disabled=desativado
        )

        if st.button("Proteger PDF", use_container_width=True, type="primary", disabled=desativado):
            if not senha:
                st.error("Informe uma senha.")
                return
            if len(senha) < _SENHA_MIN_CHARS:
                st.error(f"A senha deve ter no mínimo {_SENHA_MIN_CHARS} caracteres.")
                return
            if senha != confirmar:
                st.error("As senhas não coincidem.")
                return

            leitor = pypdf.PdfReader(arquivo_pdf)
            escritor = pypdf.PdfWriter()
            for page in leitor.pages:
                escritor.add_page(page)

            # owner_password aleatório impede remoção de restrições sem a senha do dono
            # use_128bit=False ativa AES 256-bit
            owner_pwd = secrets.token_hex(32)
            escritor.encrypt(user_password=senha, owner_password=owner_pwd, use_128bit=False)

            dados = pegar_dados_pdf(escritor)
            nome_base = nome_saida.strip().replace(" ", "_") or "pdf_protegido"

            st.success("PDF protegido com sucesso!")
            st.download_button(
                "Download do PDF protegido",
                type="primary",
                data=dados,
                file_name=f"{nome_base}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
