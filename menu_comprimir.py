import streamlit as st
import fitz
from io import BytesIO


_NIVEIS = {
    "Leve": {
        "descricao": "Remove objetos redundantes e comprime streams. Sem perda de qualidade. Redução típica: 10–25%.",
        "aviso": None,
    },
    "Moderada": {
        "descricao": "Re-renderiza páginas em 150 DPI com compressão JPEG. Leve perda de qualidade visual. Redução típica: 30–55%.",
        "aviso": "O texto do PDF resultante não será pesquisável (páginas viram imagens).",
    },
    "Máxima": {
        "descricao": "Re-renderiza páginas em 96 DPI com compressão JPEG agressiva. Redução típica: 55–80%.",
        "aviso": "O texto do PDF resultante não será pesquisável. Indicado apenas para visualização/envio.",
    },
}


def _tamanho_legivel(n_bytes: int) -> str:
    if n_bytes < 1024:
        return f"{n_bytes} B"
    elif n_bytes < 1024 ** 2:
        return f"{n_bytes / 1024:.1f} KB"
    return f"{n_bytes / 1024 ** 2:.1f} MB"


def _comprimir_pdf(pdf_bytes: bytes, nivel: str) -> bytes:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    if nivel == "Leve":
        buf = BytesIO()
        doc.save(
            buf,
            garbage=4,
            deflate=True,
            deflate_images=True,
            deflate_fonts=True,
            clean=True,
        )
        return buf.getvalue()

    # Moderada e Máxima: re-renderiza cada página como imagem JPEG
    dpi, qualidade = (150, 75) if nivel == "Moderada" else (96, 50)
    escala = dpi / 72

    novo_doc = fitz.open()
    for page in doc:
        mat = fitz.Matrix(escala, escala)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img_bytes = pix.tobytes("jpeg", jpg_quality=qualidade)
        img_doc = fitz.open("jpeg", img_bytes)
        novo_doc.insert_pdf(img_doc)

    buf = BytesIO()
    novo_doc.save(buf, garbage=4, deflate=True)
    return buf.getvalue()


def exibir_menu_comprimir(coluna):
    with coluna:
        st.markdown("""
        # Comprimir PDF

        Reduza o tamanho do arquivo PDF para facilitar o envio por e-mail ou armazenamento.
        """)

        arquivo_pdf = st.file_uploader(
            label="Selecione o arquivo PDF...",
            type="pdf",
            accept_multiple_files=False,
        )

        nivel = st.radio(
            "Nível de compressão:",
            options=list(_NIVEIS.keys()),
            horizontal=True,
        )

        info = _NIVEIS[nivel]
        st.caption(info["descricao"])
        if info["aviso"]:
            st.warning(info["aviso"])

        nome_saida = st.text_input(
            "Nome do arquivo de saída (sem .pdf)",
            value="pdf_comprimido",
            disabled=arquivo_pdf is None,
        )

        if st.button(
            "Comprimir PDF",
            use_container_width=True,
            type="primary",
            disabled=arquivo_pdf is None,
        ):
            pdf_bytes = arquivo_pdf.read()
            tamanho_original = len(pdf_bytes)

            with st.spinner("Comprimindo..."):
                pdf_comprimido = _comprimir_pdf(pdf_bytes, nivel)

            tamanho_final = len(pdf_comprimido)
            reducao = (1 - tamanho_final / tamanho_original) * 100

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Tamanho original", _tamanho_legivel(tamanho_original))
            col_b.metric("Tamanho final", _tamanho_legivel(tamanho_final))
            col_c.metric("Redução", f"{reducao:.1f}%")

            if tamanho_final >= tamanho_original:
                st.info("O arquivo já estava bem otimizado. Nenhuma redução significativa foi obtida.")

            nome_base = nome_saida.strip().replace(" ", "_") or "pdf_comprimido"
            st.download_button(
                "Download do PDF comprimido",
                type="primary",
                data=pdf_comprimido,
                file_name=f"{nome_base}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
