import streamlit as st
import pypdf
from io import BytesIO

from utilizadades import pegar_dados_pdf


def exibir_menu_remover_senha(coluna):
    with coluna:
        st.markdown("""
        # Remover senha do PDF

        Desbloqueie um PDF protegido por senha.
        """)

        arquivo_pdf = st.file_uploader(
            label="Selecione o arquivo PDF protegido...",
            type="pdf",
            accept_multiple_files=False,
        )

        desativado = arquivo_pdf is None

        senha = st.text_input("Senha atual:", type="password", disabled=desativado)
        nome_saida = st.text_input(
            "Nome do arquivo de saída (sem .pdf)", value="pdf_desbloqueado", disabled=desativado
        )

        if st.button("Remover senha", use_container_width=True, type="primary", disabled=desativado):
            if not senha:
                st.error("Informe a senha atual do PDF.")
                return

            try:
                leitor = pypdf.PdfReader(arquivo_pdf)

                if not leitor.is_encrypted:
                    st.info("Este PDF não está protegido por senha.")
                    return

                resultado = leitor.decrypt(senha)
                if resultado == pypdf.PasswordType.NOT_DECRYPTED:
                    st.error("Senha incorreta. Não foi possível desbloquear o PDF.")
                    return

                escritor = pypdf.PdfWriter()
                for page in leitor.pages:
                    escritor.add_page(page)

                dados = pegar_dados_pdf(escritor)
                nome_base = nome_saida.strip().replace(" ", "_") or "pdf_desbloqueado"

                st.success("Senha removida com sucesso!")
                st.download_button(
                    "Download do PDF desbloqueado",
                    type="primary",
                    data=dados,
                    file_name=f"{nome_base}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

            except Exception as e:
                st.error(f"Erro ao processar o PDF: {e}")
