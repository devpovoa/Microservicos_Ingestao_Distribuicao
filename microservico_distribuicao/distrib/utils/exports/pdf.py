from io import BytesIO
from typing import Iterable, Sequence

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)


def build_pdf_vendas(
    title: str,
    subtitle: str,
    kpis: dict,
    headers: Sequence[str],
    rows: Iterable[Sequence],
) -> bytes:

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=24,
        rightMargin=24,
        topMargin=28,
        bottomMargin=28,
        title=title,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="H1", parent=styles["Heading1"], spaceAfter=6))
    styles.add(ParagraphStyle(
        name="H2", parent=styles["Heading2"], textColor=colors.grey, spaceAfter=12))
    styles.add(ParagraphStyle(
        name="KPI", parent=styles["Normal"], leading=14, spaceAfter=2))

    story = []
    story.append(Paragraph(title, styles["H1"]))
    if subtitle:
        story.append(Paragraph(subtitle, styles["H2"]))
    story.append(Spacer(1, 6))

    def _fmt_money(v):
        try:
            return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except Exception:
            return str(v)

    k_total = _fmt_money(kpis.get("total", 0))
    k_qtd = f"{int(kpis.get('qtd', 0))}"
    k_ticket = _fmt_money(kpis.get("ticket", 0))

    story.append(Paragraph(f"<b>Total:</b> {k_total}", styles["KPI"]))
    story.append(Paragraph(f"<b>Qtd. Vendas:</b> {k_qtd}", styles["KPI"]))
    story.append(Paragraph(f"<b>Ticket médio:</b> {k_ticket}", styles["KPI"]))
    story.append(Spacer(1, 10))

    data = [list(headers)]
    count = 0
    for r in rows:
        data.append(list(r))
        count += 1

    if count == 0:
        story.append(
            Paragraph("Nenhum registro para os filtros aplicados.", styles["Normal"]))
    else:
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f4f6f8")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111111")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),

            ("ALIGN", (-3, 1), (-1, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#dddddd")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.whitesmoke, colors.HexColor("#ffffff")]),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("TOPPADDING", (0, 0), (-1, 0), 6),
        ]))
        story.append(table)

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


def build_pdf_table(title: str, subtitle: str | None, headers, rows_iterable):
    """
    Gera um PDF com tabela:
      - A4 landscape
      - margens seguras
      - colWidths proporcionais
      - textos longos com wrap
      - números alinhados à direita
      - cabeçalho repetido
    """
    buf = BytesIO()

    # Página e margens
    page_size = landscape(A4)
    margin = 12 * mm
    doc = SimpleDocTemplate(
        buf,
        pagesize=page_size,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin,
        title=title or "Relatório"
    )

    # Estilos
    styles = getSampleStyleSheet()
    h1 = styles["Title"]
    h1.fontSize = 16
    h1.leading = 20

    h2 = styles["Heading2"]
    h2.fontSize = 10
    h2.leading = 13
    h2.spaceBefore = 0
    h2.spaceAfter = 6

    cell_style = ParagraphStyle(
        "cell",
        parent=styles["BodyText"],
        fontSize=8,
        leading=10,
        spaceBefore=0,
        spaceAfter=0,
        allowOrphans=1,
        allowWidows=1,
        wordWrap="CJK",  # quebra palavras longas (e.g. e-mails)
    )

    cell_style_right = ParagraphStyle(
        "cell_right",
        parent=cell_style,
        alignment=2,  # TA_RIGHT
    )

    # Constrói dados da tabela (com Paragraph para permitir wrap)
    data = []

    # Cabeçalho
    data.append([Paragraph(str(h), ParagraphStyle("th", parent=cell_style,
                fontSize=8, leading=10, textColor=colors.white)) for h in headers])

    numeric_cols_by_name = {"Compras", "Receita (R$)", "Ticket médio (R$)"}
    numeric_idx = {i for i, h in enumerate(
        headers) if str(h) in numeric_cols_by_name}

    for row in rows_iterable:
        cells = []
        for i, value in enumerate(row):
            txt = "" if value is None else str(value)
            if i in numeric_idx:
                cells.append(Paragraph(txt, cell_style_right))
            else:
                cells.append(Paragraph(txt, cell_style))
        data.append(cells)

    # Larguras proporcionais por coluna
    total_width = page_size[0] - (doc.leftMargin + doc.rightMargin)

    weights_by_header = {
        "Cliente": 1.6,
        "Documento": 1.1,
        "Email": 1.8,
        "Compras": 0.7,
        "Receita (R$)": 0.9,
        "Ticket médio (R$)": 0.9,
        "Última compra": 1.0,
        "Criado em": 0.9,
    }
    weights = [weights_by_header.get(str(h), 1.0) for h in headers]
    weight_sum = sum(weights) or 1.0
    col_widths = [total_width * (w / weight_sum) for w in weights]

    # Tabela
    table = Table(data, colWidths=col_widths, repeatRows=1)

    # Estilo da tabela
    table.setStyle(TableStyle([
        # Header
        ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.15, 0.15, 0.18)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),

        # Corpo
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("VALIGN", (0, 1), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.whitesmoke, colors.white]),

        # Bordas e grid suave
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),

        # Padding
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 1), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 3),
    ]))

    # Story (título + tabela)
    story = []
    if title:
        story.append(Paragraph(title, h1))
    if subtitle:
        story.append(Paragraph(subtitle, h2))
    story.append(Spacer(1, 4))
    story.append(table)

    doc.build(story)
    pdf = buf.getvalue()
    buf.close()
    return pdf
