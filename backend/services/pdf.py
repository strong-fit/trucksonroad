from fpdf import FPDF
from services.email import format_swiss_date as _fmt_date
from datetime import datetime, timezone
import io
from services.email import get_email_t
from database import db


def generate_offer_pdf(inquiry: dict, lang: str = "de") -> bytes:
    t = get_email_t(lang)
    name = f"{inquiry.get('first_name', '')} {inquiry.get('last_name', '')}".strip() or inquiry.get('name', '')
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 12, "TRUCKSONROAD", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "TRUCKSonROAD | Bahnhofstrasse 75, 8620 Wetzikon | +41 79 696 98 99 | info@trucksonroad.ch", ln=True, align="C")
    pdf.ln(8)
    pdf.set_draw_color(77, 182, 172)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, t["pdf_offer"], ln=True)
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, f"{t['pdf_created']}: {datetime.now(timezone.utc).strftime('%d.%m.%Y')}", ln=True)
    pdf.cell(0, 7, f"{t['pdf_inquiry_nr']}: {inquiry.get('id', '-')[:8]}", ln=True)
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(77, 182, 172)
    pdf.cell(0, 8, t["pdf_customer"], ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    fields = [
        (t["name"], name), (t["email"], inquiry.get("email", "-")), (t["phone"], inquiry.get("phone", "-")),
        (t["pdf_company"], inquiry.get("company", "-")),
    ]
    for label, val in fields:
        if val and val != "-":
            pdf.cell(50, 7, label + ":", 0)
            pdf.cell(0, 7, str(val), ln=True)
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(77, 182, 172)
    pdf.cell(0, 8, t["pdf_event_details"], ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    event_fields = [
        (t["pdf_date"], _fmt_date(inquiry.get("event_date"))), (t["location"], inquiry.get("location", "-")),
        (t["guests"], str(inquiry.get("guest_count", "-"))), (t["event_type"], inquiry.get("event_type", inquiry.get("concept", "-"))),
        (t["pdf_indoor"], inquiry.get("indoor_outdoor", "-")), (t["budget"], inquiry.get("budget", "-")),
    ]
    for label, val in event_fields:
        if val and val != "-":
            pdf.cell(50, 7, label + ":", 0)
            pdf.cell(0, 7, str(val), ln=True)
    trucks = inquiry.get("selected_trucks", [])
    if trucks:
        pdf.cell(50, 7, "Trucks:", 0)
        pdf.cell(0, 7, ", ".join(trucks), ln=True)
    extras = inquiry.get("extras", [])
    if extras:
        pdf.cell(50, 7, "Extras:", 0)
        pdf.cell(0, 7, ", ".join(extras), ln=True)
    if inquiry.get("remarks"):
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, t["pdf_remarks"] + ":", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, inquiry["remarks"])
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(0, 5, t["pdf_disclaimer"])
    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf.getvalue()


async def generate_veranstalter_pdf() -> bytes:
    trucks = await db.trucks.find({"is_active": True}, {"_id": 0}).sort("order", 1).to_list(100)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 28)
    pdf.cell(0, 15, "TRUCKSONROAD", ln=True, align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, "Premium Foodtrucks fuer jeden Anlass", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "TRUCKSonROAD | Bahnhofstrasse 75, 8620 Wetzikon  |  +41 79 696 98 99  |  info@trucksonroad.ch", ln=True, align="C")
    pdf.ln(10)
    pdf.set_draw_color(77, 182, 172)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Unsere Truck-Konzepte", ln=True)
    pdf.ln(3)
    for t in trucks:
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(77, 182, 172)
        pdf.cell(0, 8, t.get("name_de", ""), ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 9)
        desc = t.get("desc_de", "")
        if desc:
            pdf.multi_cell(0, 5, desc)
        pdf.ln(2)
        menu = t.get("menu_de", [])
        if menu:
            pdf.set_font("Helvetica", "I", 9)
            pdf.cell(0, 5, "Menu: " + ", ".join(menu), ln=True)
        cap = t.get("capacity", "")
        if cap:
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(0, 5, f"Kapazitaet: {cap}", ln=True)
        space = t.get("space_required", "")
        if space:
            pdf.cell(0, 5, f"Platzbedarf: {space}", ln=True)
        pdf.ln(5)
        pdf.set_draw_color(220, 220, 220)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(5)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Warum TRUCKSonROAD?", ln=True)
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 10)
    reasons = [
        ("Schnelle Ausgabe", "Bis zu 300 Gaeste pro Stunde - auch bei Grossevents kein Stau."),
        ("Mehrere Trucks gleichzeitig", "Koordinierte Logistik und Personal fuer parallelen Einsatz."),
        ("Professioneller Auftritt", "Einheitliches Branding, klare Ablaeufe, erfahrenes Team."),
        ("Auffaelliges Design", "Unsere Trucks sind Hingucker und machen Events unvergesslich."),
    ]
    for title, text in reasons:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(77, 182, 172)
        pdf.cell(0, 7, title, ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, text)
        pdf.ln(3)
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Kontakt & Anfrage", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "TRUCKSonROAD", ln=True)
    pdf.cell(0, 6, "Bahnhofstrasse 75, 8620 Wetzikon", ln=True)
    pdf.cell(0, 6, "+41 79 696 98 99", ln=True)
    pdf.cell(0, 6, "info@trucksonroad.ch", ln=True)
    pdf.cell(0, 6, "www.trucksonroad.ch", ln=True)
    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf.getvalue()


def generate_export_pdf(data_type: str, docs: list, fields: list) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page("L")
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, f"TrucksOnRoad - {data_type.title()} Export", ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(0, 5, f"Erstellt: {datetime.now(timezone.utc).strftime('%d.%m.%Y %H:%M')}", ln=True)
    pdf.ln(5)
    col_w = 277 / min(len(fields), 7)
    display_fields = fields[:7]
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_fill_color(240, 240, 240)
    for f in display_fields:
        pdf.cell(col_w, 6, f.replace("_", " ").title(), 1, 0, "C", True)
    pdf.ln()
    pdf.set_font("Helvetica", "", 7)
    for doc in docs[:200]:
        for f in display_fields:
            val = doc.get(f, "")
            if isinstance(val, list):
                val = ", ".join(str(v) for v in val)
            pdf.cell(col_w, 5, str(val)[:40], 1, 0)
        pdf.ln()
    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf.getvalue()
