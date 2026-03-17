import streamlit as st
import pypdf
import zipfile
from io import BytesIO

from utilizadades import pegar_dados_pdf


def _pdf_parte(indices: list[int], leitor: pypdf.PdfReader) -> bytes:
    escritor = pypdf.PdfWriter()
    for i in indices:
        escritor.add_page(leitor.pages[i])
    return pegar_dados_pdf(escritor)


def _criar_zip(partes: list[tuple[str, bytes]]) -> bytes:
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for nome, dados in partes:
            zf.writestr(nome, dados)
    return buf.getvalue()


def exibir_menu_dividir(coluna):
    with coluna:
        st.markdown("""
        # Dividir PDF

        Separe um PDF em múltiplos arquivos menores.
        """)

        arquivo_pdf = st.file_uploader(
            label="Selecione o arquivo PDF...",
            type="pdf",
            accept_multiple_files=False,
        )

        if not arquivo_pdf:
            return

        pdf_bytes = arquivo_pdf.read()
        leitor = pypdf.PdfReader(BytesIO(pdf_bytes))
        if leitor.is_encrypted:
            st.error("Este PDF está protegido por senha. Remova a senha primeiro usando a função **Remover senha**.")
            return
        total = len(leitor.pages)
        st.info(f"PDF carregado: **{total} página(s)**")

        modo = st.radio(
            "Modo de divisão:",
            ["A cada N páginas", "Por intervalos personalizados", "Uma página por arquivo"],
            horizontal=True,
        )

        partes: list[tuple[str, list[int]]] = []

        if modo == "A cada N páginas":
            n = int(st.number_input(
                "Dividir a cada quantas páginas:",
                min_value=1, max_value=total - 1, value=1, step=1,
            ))
            for i, start in enumerate(range(0, total, n)):
                fim = min(start + n, total)
                partes.append((f"parte_{i+1:02d}_pgs_{start+1}a{fim}.pdf", list(range(start, fim))))

        elif modo == "Por intervalos personalizados":
            st.caption("Um intervalo por linha no formato início-fim. Exemplo: 1-3")
            texto = st.text_area("Intervalos:", placeholder="1-3\n4-7\n8-10", height=140)
            for i, linha in enumerate(texto.strip().splitlines()):
                linha = linha.strip()
                if not linha:
                    continue
                try:
                    inicio, fim = [int(x.strip()) for x in linha.split("-")]
                    if 1 <= inicio <= fim <= total:
                        partes.append((f"parte_{i+1:02d}_pgs_{inicio}a{fim}.pdf", list(range(inicio - 1, fim))))
                    else:
                        st.warning(f"Intervalo fora do range: **{linha}** (PDF tem {total} páginas)")
                except Exception:
                    st.warning(f"Formato inválido: **'{linha}'**. Use o formato '1-3'.")

        else:  # Uma página por arquivo
            partes = [(f"pagina_{i+1:03d}.pdf", [i]) for i in range(total)]

        if partes:
            st.info(f"Serão gerados **{len(partes)} arquivo(s)** dentro do ZIP.")

        nome_zip = st.text_input("Nome do arquivo ZIP de saída (sem .zip)", value="pdf_dividido")

        if st.button("Dividir e baixar ZIP", use_container_width=True, type="primary"):
            if not partes:
                st.error("Nenhum intervalo válido definido.")
                return

            leitor_final = pypdf.PdfReader(BytesIO(pdf_bytes))
            arquivos = [(nome, _pdf_parte(indices, leitor_final)) for nome, indices in partes]

            zip_bytes = _criar_zip(arquivos)
            nome_base = nome_zip.strip().replace(" ", "_") or "pdf_dividido"

            st.success(f"PDF dividido em **{len(arquivos)} arquivo(s)**!")
            st.download_button(
                "Download do ZIP",
                type="primary",
                data=zip_bytes,
                file_name=f"{nome_base}.zip",
                mime="application/zip",
                use_container_width=True,
            )
