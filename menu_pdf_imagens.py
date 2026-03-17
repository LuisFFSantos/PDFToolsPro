import streamlit as st
import fitz
import zipfile
from io import BytesIO


def exibir_menu_pdf_imagens(coluna):
    with coluna:
        st.markdown("""
        # PDF para Imagens

        Exporte as páginas do PDF como imagens PNG ou JPEG compactadas em um ZIP.
        """)

        arquivo_pdf = st.file_uploader(
            label="Selecione o arquivo PDF...",
            type="pdf",
            accept_multiple_files=False,
        )

        desativado = arquivo_pdf is None

        col1, col2 = st.columns(2)
        with col1:
            formato = st.selectbox("Formato:", ["PNG", "JPEG"], disabled=desativado)
        with col2:
            dpi = st.selectbox("Resolução (DPI):", [72, 96, 150, 300], index=2, disabled=desativado)

        nome_zip = st.text_input(
            "Nome do arquivo ZIP de saída (sem .zip)", value="pdf_imagens", disabled=desativado
        )

        if arquivo_pdf:
            pdf_bytes = arquivo_pdf.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            total = len(doc)
            doc.close()
            st.info(f"PDF carregado: **{total} página(s)**")

        if st.button("Exportar imagens", use_container_width=True, type="primary", disabled=desativado):
            fmt = formato.lower()
            escala = dpi / 72

            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            total = len(doc)

            buf_zip = BytesIO()
            with st.spinner(f"Exportando {total} página(s)..."):
                with zipfile.ZipFile(buf_zip, "w", zipfile.ZIP_DEFLATED) as zf:
                    for i, page in enumerate(doc):
                        mat = fitz.Matrix(escala, escala)
                        pix = page.get_pixmap(matrix=mat, alpha=(fmt == "png"))
                        if fmt == "jpeg":
                            img_bytes = pix.tobytes("jpeg", jpg_quality=90)
                        else:
                            img_bytes = pix.tobytes("png")
                        zf.writestr(f"pagina_{i+1:03d}.{fmt}", img_bytes)

            doc.close()
            nome_base = nome_zip.strip().replace(" ", "_") or "pdf_imagens"

            st.success(f"**{total} imagem(ns)** exportada(s)!")
            st.download_button(
                "Download do ZIP",
                type="primary",
                data=buf_zip.getvalue(),
                file_name=f"{nome_base}.zip",
                mime="application/zip",
                use_container_width=True,
            )
