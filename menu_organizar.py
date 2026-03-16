import streamlit as st
import pypdf
from io import BytesIO
from streamlit_sortables import sort_items

from utilizadades import pegar_dados_pdf


_LABELS_ROTACAO = {
    0: "Sem rotação",
    90: "90° (↻ horário)",
    180: "180°",
    270: "90° (↺ anti-horário)",
}


@st.cache_data(show_spinner=False)
def _renderizar_thumbnail(pdf_bytes: bytes, pagina_idx: int, rotacao: int = 0):
    try:
        import fitz
        from PIL import Image

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc[pagina_idx]
        mat = fitz.Matrix(0.3, 0.3)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img_bytes = pix.tobytes("png")
        doc.close()

        if rotacao != 0:
            img = Image.open(BytesIO(img_bytes))
            # PIL rotate é anti-horário; negativo = horário (igual ao pypdf)
            img = img.rotate(-rotacao, expand=True)
            buf = BytesIO()
            img.save(buf, format="PNG")
            img_bytes = buf.getvalue()

        return img_bytes
    except Exception:
        return None


def exibir_menu_organizar(coluna):
    with coluna:
        st.markdown("""
        # Organizar PDF

        Visualize e configure cada página: gire, exclua, reordene ou insira novas páginas.
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
        total_paginas = len(leitor.pages)

        st.info(f"PDF carregado: **{total_paginas} página(s)**")

        # ── Grade de páginas ──────────────────────────────────────────────────
        st.markdown("### Páginas")
        st.caption(
            "O thumbnail reflete a rotação selecionada. "
            "Marque 'Excluir' para remover uma página do resultado final."
        )

        NUM_COLUNAS = 4
        rotacoes: dict[int, int] = {}
        excluir: dict[int, bool] = {}

        for row_start in range(0, total_paginas, NUM_COLUNAS):
            cols = st.columns(NUM_COLUNAS)
            for col_offset in range(NUM_COLUNAS):
                page_idx = row_start + col_offset
                if page_idx >= total_paginas:
                    break
                with cols[col_offset]:
                    rot_atual = st.session_state.get(f"rot_{page_idx}", 0)
                    thumb = _renderizar_thumbnail(pdf_bytes, page_idx, rot_atual)
                    if thumb:
                        st.image(thumb, use_container_width=True)
                    else:
                        st.markdown("*(sem prévia)*")

                    st.markdown(f"**Pág. {page_idx + 1}**")

                    rot = st.selectbox(
                        label="Rotação",
                        options=[0, 90, 180, 270],
                        format_func=lambda x: _LABELS_ROTACAO[x],
                        index=0,
                        key=f"rot_{page_idx}",
                        label_visibility="collapsed",
                    )
                    rotacoes[page_idx] = rot

                    excluir[page_idx] = st.checkbox(
                        "Excluir",
                        key=f"del_{page_idx}",
                    )

        # ── Reordenar ─────────────────────────────────────────────────────────
        st.markdown("### Reordenar páginas")
        st.caption("Arraste os cards para definir a ordem final. Páginas marcadas para excluir não aparecem aqui.")

        paginas_ativas = [f"Pág. {i + 1}" for i in range(total_paginas) if not excluir.get(i, False)]

        nova_ordem = sort_items(paginas_ativas, direction="horizontal", key="sortable_paginas")

        # ── Inserir de outro PDF ──────────────────────────────────────────────
        st.markdown("### Inserir páginas de outro PDF *(opcional)*")

        arquivo_inserir = st.file_uploader(
            label="Selecione o PDF a inserir...",
            type="pdf",
            accept_multiple_files=False,
            key="pdf_inserir",
        )

        posicao_insercao: int | None = None
        if arquivo_inserir:
            leitor_ins_preview = pypdf.PdfReader(arquivo_inserir)
            st.caption(f"PDF a inserir: {len(leitor_ins_preview.pages)} página(s)")
            arquivo_inserir.seek(0)
            posicao_insercao = int(
                st.number_input(
                    "Inserir após a página de saída nº (0 = antes de tudo):",
                    min_value=0,
                    max_value=total_paginas,
                    value=total_paginas,
                    step=1,
                )
            )

        # ── Processar ────────────────────────────────────────────────────────
        st.markdown("---")
        nome_saida = st.text_input(
            "Nome do arquivo de saída (sem .pdf)", value="pdf_organizado"
        )

        if st.button("Processar PDF", use_container_width=True, type="primary"):
            # Extrai os números de página a partir dos labels do sortable ("Pág. 3" → 3)
            ordem_valida = [
                int(label.split(" ")[1])
                for label in nova_ordem
                if label.split(" ")[1].isdigit()
            ]

            if not ordem_valida and arquivo_inserir is None:
                st.error("Nenhuma página válida para processar.")
                return

            escritor = pypdf.PdfWriter()
            leitor_final = pypdf.PdfReader(BytesIO(pdf_bytes))

            paginas_inserir: list = []
            if arquivo_inserir:
                arquivo_inserir.seek(0)
                leitor_ins = pypdf.PdfReader(arquivo_inserir)
                paginas_inserir = list(leitor_ins.pages)

            # Inserção no início (posição 0)
            if posicao_insercao is not None and posicao_insercao == 0:
                for pg in paginas_inserir:
                    escritor.add_page(pg)
                paginas_inserir = []

            for i, num_pagina in enumerate(ordem_valida):
                page = leitor_final.pages[num_pagina - 1]
                rot = rotacoes.get(num_pagina - 1, 0)
                if rot != 0:
                    page.rotate(rot)
                escritor.add_page(page)

                # Inserção após i+1 páginas de saída
                if (
                    paginas_inserir
                    and posicao_insercao is not None
                    and (i + 1) == posicao_insercao
                ):
                    for pg in paginas_inserir:
                        escritor.add_page(pg)
                    paginas_inserir = []

            # Inserção no final (caso não tenha sido inserido ainda)
            for pg in paginas_inserir:
                escritor.add_page(pg)

            dados_pdf = pegar_dados_pdf(escritor)
            nome_base = nome_saida.strip().replace(" ", "_") or "pdf_organizado"
            total_saida = len(escritor.pages)

            st.success(
                f"PDF processado com sucesso! **{total_saida} página(s)** no arquivo final."
            )
            st.download_button(
                "Download do PDF organizado",
                type="primary",
                data=dados_pdf,
                file_name=f"{nome_base}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
