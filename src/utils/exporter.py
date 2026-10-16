"""
Report Exporter (Text & PDF) for UlasRasa AI Kitchen Action Checklist
"""

import io
from datetime import datetime
from typing import List, Dict, Any

def export_action_plan_text(
    overall_score: float,
    status: str,
    action_items: List[Dict[str, Any]],
    critical_alerts: List[Dict[str, Any]]
) -> str:
    """Menghasilkan teks berformat rapi untuk diunduh sebagai .txt."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M WIB")
    
    lines = [
        "============================================================",
        "          ULASRASA - AI KITCHEN ACTION PLAN REPORT          ",
        "============================================================",
        f"Waktu Generate : {now_str}",
        f"Health Score   : {overall_score}%",
        f"Status Dapur   : {status}",
        "============================================================",
        "",
        "--- CRITICAL KITCHEN ALERTS ---"
    ]
    
    if critical_alerts:
        for alert in critical_alerts:
            lines.append(f"[!] {alert['title']}")
            lines.append(f"    Aspek  : {alert['aspect']}")
            lines.append(f"    Detail : {alert['message']}")
            lines.append("")
    else:
        lines.append("Tidak ada alert kritis aktif. Dapur berjalan normal.")
        lines.append("")

    lines.append("--- REKOMENDASI TINDAKAN OPERASIONAL DAPUR ---")
    completed_count = sum(1 for item in action_items if item.get("checked", False))
    lines.append(f"Progress Penyelesaian: {completed_count}/{len(action_items)} Selesai\n")

    for idx, item in enumerate(action_items, 1):
        check_mark = "[v]" if item.get("checked", False) else "[ ]"
        lines.append(f"{idx}. {check_mark} [{item['aspect'].upper()}] - {item['title']}")
        lines.append(f"   Target: {item['target_pic']} | Deadline: {item['deadline']}")
        lines.append(f"   Instruksi: {item['instruction']}")
        lines.append("")

    lines.append("============================================================")
    lines.append("Dokumen ini dihasilkan secara otomatis oleh UlasRasa AI Engine.")
    lines.append("============================================================")
    
    return "\n".join(lines)

def export_action_plan_pdf(
    overall_score: float,
    status: str,
    action_items: List[Dict[str, Any]],
    critical_alerts: List[Dict[str, Any]]
) -> bytes:
    """Menghasilkan file PDF binary menggunakan ReportLab."""
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1e3a8a')
    )
    h2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0f172a')
    )
    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )
    alert_style = ParagraphStyle(
        'AlertCustom',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#b91c1c')
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("<b>UlasRasa - AI Kitchen Action Plan</b>", title_style))
    story.append(Spacer(1, 8))
    meta_text = f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M WIB')} | <b>Health Score:</b> {overall_score}% ({status})"
    story.append(Paragraph(meta_text, body_style))
    story.append(Spacer(1, 14))

    # Critical Alerts
    story.append(Paragraph("<b>Peringatan Kritis Dapur</b>", h2_style))
    story.append(Spacer(1, 6))
    if critical_alerts:
        for alert in critical_alerts:
            alert_p = Paragraph(f"<b>[ALERT] {alert['title']}</b> - {alert['message']}", alert_style)
            story.append(alert_p)
            story.append(Spacer(1, 4))
    else:
        story.append(Paragraph("Tidak ada peringatan kritis aktif. Kondisi dapur terjaga baik.", body_style))
    story.append(Spacer(1, 14))

    # Action Items Table
    story.append(Paragraph("<b>Checklist Tindakan Operasional Tim Dapur</b>", h2_style))
    story.append(Spacer(1, 8))

    table_data: List[List[Any]] = [["Status", "Aspek", "Tindakan & Instruksi", "PIC", "Deadline"]]
    for item in action_items:
        status_text = "SELESAI" if item.get("checked", False) else "PENDING"
        desc = f"<b>{item['title']}</b><br/>{item['instruction']}"
        table_data.append([
            status_text,
            item["aspect"],
            Paragraph(desc, body_style),
            item["target_pic"],
            item["deadline"]
        ])

    col_widths = [55, 65, 260, 80, 80]
    t = Table(table_data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
