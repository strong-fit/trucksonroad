import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database import db

logger = logging.getLogger(__name__)

# --- MULTILINGUAL EMAIL/PDF TRANSLATIONS ---
EMAIL_I18N = {
    "de": {
        "thank_you": "Vielen Dank fuer Ihre Anfrage, {name}!",
        "inquiry_received": "Wir haben Ihre Anfrage erhalten und melden uns innerhalb von 24 Stunden mit einem individuellen Angebot.",
        "event_date": "Event-Datum", "location": "Ort", "guests": "Gaeste", "event_type": "Eventtyp",
        "trucks": "Trucks", "budget": "Budget", "questions_contact": "Bei Fragen erreichen Sie uns jederzeit unter info@trucksonroad.ch oder +41 79 696 98 99.",
        "greeting": "Herzliche Gruesse", "team": "TrucksOnRoad Team",
        "new_inquiry": "NEUE ANFRAGE", "new_inquiry_from": "Neue Anfrage von {name}",
        "name": "Name", "email": "E-Mail", "phone": "Telefon",
        "your_offer": "Ihr Angebot, {name}", "offer_intro": "Vielen Dank fuer Ihr Interesse! Basierend auf Ihrer Anfrage haben wir folgendes Angebot fuer Sie zusammengestellt:",
        "offer_follow_up": "Wir melden uns in Kuerze mit den detaillierten Konditionen. Bei Fragen stehen wir Ihnen gerne zur Verfuegung.",
        "status_update": "STATUS-UPDATE", "hello": "Hallo {name},",
        "status_in_review": "Ihre Anfrage wird aktuell von unserem Team geprueft. Wir melden uns in Kuerze bei Ihnen.",
        "status_offer_sent": "Wir haben ein Angebot fuer Sie erstellt. Bitte pruefen Sie die Details und melden Sie sich bei Fragen.",
        "status_confirmed": "Ihre Buchung ist bestaetigt! Wir freuen uns auf Ihren Event.",
        "status_completed": "Vielen Dank fuer Ihren Auftrag! Wir hoffen, der Event war ein voller Erfolg.",
        "status_cancelled": "Ihre Anfrage wurde leider storniert. Bei Fragen kontaktieren Sie uns gerne.",
        "status_default": "Der Status Ihrer Anfrage wurde aktualisiert: {status}",
        "event": "Event", "at": "am",
        "invoice_label": "RECHNUNG", "invoice_word": "Rechnung",
        "inv_pending": "Fuer Ihren Event wurde eine Rechnung erstellt.",
        "inv_sent": "Wir haben Ihnen eine Rechnung zugesendet. Bitte beachten Sie die Zahlungsfrist.",
        "inv_paid": "Vielen Dank! Ihre Zahlung ist bei uns eingegangen.",
        "inv_overdue": "Ihre Rechnung ist ueberfaellig. Bitte ueberpruefen Sie die Zahlung.",
        "inv_default": "Ihr Rechnungsstatus wurde aktualisiert: {status}",
        "new_file": "NEUE DATEI", "file_added": "Wir haben eine neue Datei zu Ihrer Anfrage hinzugefuegt:",
        "file_download": "Sie koennen diese Datei in Ihrem Kundenportal herunterladen.",
        "reminder": "ERINNERUNG", "days_until": "Nur noch {days} Tage bis zu Ihrem Event!",
        "ready_for_event": "Wir sind bereit und freuen uns auf Ihren Event! Bei letzten Fragen erreichen Sie uns unter info@trucksonroad.ch oder +41 79 696 98 99.",
        "subject_inquiry": "Anfrage erhalten", "subject_offer": "Ihr Angebot von TrucksOnRoad",
        "subject_confirmed": "Ihre Buchung ist bestaetigt!", "subject_completed": "Event abgeschlossen",
        "subject_cancelled": "Anfrage storniert", "subject_status": "Status-Update",
        "subject_inv_pending": "Rechnung erstellt", "subject_inv_sent": "Rechnung zugestellt",
        "subject_inv_paid": "Zahlung erhalten", "subject_inv_overdue": "Rechnung ueberfaellig",
        "subject_reminder": "Noch {days} Tage bis zu Ihrem Event!",
        "pdf_offer": "Angebot", "pdf_created": "Erstellt am", "pdf_inquiry_nr": "Anfrage-Nr.",
        "pdf_customer": "Kundendaten", "pdf_event_details": "Event-Details", "pdf_indoor": "Indoor/Outdoor",
        "pdf_remarks": "Bemerkungen", "pdf_disclaimer": "Dieses Angebot ist unverbindlich und 30 Tage gueltig. Fuer Fragen stehen wir Ihnen gerne zur Verfuegung.",
        "pdf_company": "Firma", "pdf_date": "Datum",
        "status_labels": {"new": "Neu", "in_review": "In Pruefung", "offer_sent": "Angebot gesendet", "confirmed": "Bestaetigt", "completed": "Abgeschlossen", "cancelled": "Storniert"},
        "invoice_labels": {"none": "Keine", "pending": "Offen", "sent": "Gesendet", "paid": "Bezahlt", "overdue": "Ueberfaellig"},
    },
    "en": {
        "thank_you": "Thank you for your inquiry, {name}!",
        "inquiry_received": "We have received your inquiry and will get back to you within 24 hours with a personalized offer.",
        "event_date": "Event Date", "location": "Location", "guests": "Guests", "event_type": "Event Type",
        "trucks": "Trucks", "budget": "Budget", "questions_contact": "For questions, reach us at info@trucksonroad.ch or +41 79 696 98 99.",
        "greeting": "Best regards", "team": "TrucksOnRoad Team",
        "new_inquiry": "NEW INQUIRY", "new_inquiry_from": "New inquiry from {name}",
        "name": "Name", "email": "Email", "phone": "Phone",
        "your_offer": "Your Offer, {name}", "offer_intro": "Thank you for your interest! Based on your inquiry, we have prepared the following offer:",
        "offer_follow_up": "We will get back to you shortly with detailed terms. Please don't hesitate to contact us with any questions.",
        "status_update": "STATUS UPDATE", "hello": "Hello {name},",
        "status_in_review": "Your inquiry is currently being reviewed by our team. We will contact you shortly.",
        "status_offer_sent": "We have prepared an offer for you. Please review the details and contact us with any questions.",
        "status_confirmed": "Your booking is confirmed! We look forward to your event.",
        "status_completed": "Thank you for your order! We hope the event was a great success.",
        "status_cancelled": "Your inquiry has been cancelled. Please contact us if you have any questions.",
        "status_default": "Your inquiry status has been updated: {status}",
        "event": "Event", "at": "on",
        "invoice_label": "INVOICE", "invoice_word": "Invoice",
        "inv_pending": "An invoice has been created for your event.",
        "inv_sent": "We have sent you an invoice. Please note the payment deadline.",
        "inv_paid": "Thank you! Your payment has been received.",
        "inv_overdue": "Your invoice is overdue. Please check the payment.",
        "inv_default": "Your invoice status has been updated: {status}",
        "new_file": "NEW FILE", "file_added": "A new file has been added to your inquiry:",
        "file_download": "You can download this file in your customer portal.",
        "reminder": "REMINDER", "days_until": "Only {days} days until your event!",
        "ready_for_event": "We are ready and looking forward to your event! For any last questions, reach us at info@trucksonroad.ch or +41 79 696 98 99.",
        "subject_inquiry": "Inquiry received", "subject_offer": "Your offer from TrucksOnRoad",
        "subject_confirmed": "Your booking is confirmed!", "subject_completed": "Event completed",
        "subject_cancelled": "Inquiry cancelled", "subject_status": "Status Update",
        "subject_inv_pending": "Invoice created", "subject_inv_sent": "Invoice sent",
        "subject_inv_paid": "Payment received", "subject_inv_overdue": "Invoice overdue",
        "subject_reminder": "{days} days until your event!",
        "pdf_offer": "Offer", "pdf_created": "Created on", "pdf_inquiry_nr": "Inquiry No.",
        "pdf_customer": "Customer Details", "pdf_event_details": "Event Details", "pdf_indoor": "Indoor/Outdoor",
        "pdf_remarks": "Remarks", "pdf_disclaimer": "This offer is non-binding and valid for 30 days. Please contact us with any questions.",
        "pdf_company": "Company", "pdf_date": "Date",
        "status_labels": {"new": "New", "in_review": "In Review", "offer_sent": "Offer Sent", "confirmed": "Confirmed", "completed": "Completed", "cancelled": "Cancelled"},
        "invoice_labels": {"none": "None", "pending": "Pending", "sent": "Sent", "paid": "Paid", "overdue": "Overdue"},
    },
    "fr": {
        "thank_you": "Merci pour votre demande, {name} !",
        "inquiry_received": "Nous avons recu votre demande et vous recontacterons dans les 24 heures avec une offre personnalisee.",
        "event_date": "Date", "location": "Lieu", "guests": "Invites", "event_type": "Type",
        "trucks": "Trucks", "budget": "Budget", "questions_contact": "Pour toute question, contactez-nous a info@trucksonroad.ch ou +41 79 696 98 99.",
        "greeting": "Cordialement", "team": "L'equipe TrucksOnRoad",
        "new_inquiry": "NOUVELLE DEMANDE", "new_inquiry_from": "Nouvelle demande de {name}",
        "name": "Nom", "email": "E-mail", "phone": "Telephone",
        "your_offer": "Votre offre, {name}", "offer_intro": "Merci pour votre interet ! Voici notre offre basee sur votre demande :",
        "offer_follow_up": "Nous reviendrons vers vous avec les conditions detaillees. N'hesitez pas a nous contacter.",
        "status_update": "MISE A JOUR", "hello": "Bonjour {name},",
        "status_in_review": "Votre demande est en cours d'examen. Nous vous contacterons prochainement.",
        "status_offer_sent": "Nous avons prepare une offre pour vous. Veuillez verifier les details.",
        "status_confirmed": "Votre reservation est confirmee ! Nous nous rejouissons de votre evenement.",
        "status_completed": "Merci pour votre commande ! Nous esperons que l'evenement a ete un succes.",
        "status_cancelled": "Votre demande a ete annulee. N'hesitez pas a nous contacter.",
        "status_default": "Le statut de votre demande a ete mis a jour : {status}",
        "event": "Evenement", "at": "le",
        "invoice_label": "FACTURE", "invoice_word": "Facture",
        "inv_pending": "Une facture a ete creee pour votre evenement.",
        "inv_sent": "Nous vous avons envoye une facture. Veuillez respecter le delai de paiement.",
        "inv_paid": "Merci ! Votre paiement a ete recu.",
        "inv_overdue": "Votre facture est en retard. Veuillez verifier le paiement.",
        "inv_default": "Le statut de votre facture a ete mis a jour : {status}",
        "new_file": "NOUVEAU FICHIER", "file_added": "Un nouveau fichier a ete ajoute a votre demande :",
        "file_download": "Vous pouvez telecharger ce fichier dans votre portail client.",
        "reminder": "RAPPEL", "days_until": "Plus que {days} jours avant votre evenement !",
        "ready_for_event": "Nous sommes prets ! Pour toute question, contactez-nous a info@trucksonroad.ch ou +41 79 696 98 99.",
        "subject_inquiry": "Demande recue", "subject_offer": "Votre offre de TrucksOnRoad",
        "subject_confirmed": "Reservation confirmee !", "subject_completed": "Evenement termine",
        "subject_cancelled": "Demande annulee", "subject_status": "Mise a jour du statut",
        "subject_inv_pending": "Facture creee", "subject_inv_sent": "Facture envoyee",
        "subject_inv_paid": "Paiement recu", "subject_inv_overdue": "Facture en retard",
        "subject_reminder": "Plus que {days} jours !",
        "pdf_offer": "Offre", "pdf_created": "Cree le", "pdf_inquiry_nr": "No. demande",
        "pdf_customer": "Donnees client", "pdf_event_details": "Details evenement", "pdf_indoor": "Interieur/Exterieur",
        "pdf_remarks": "Remarques", "pdf_disclaimer": "Cette offre est sans engagement et valable 30 jours.",
        "pdf_company": "Entreprise", "pdf_date": "Date",
        "status_labels": {"new": "Nouveau", "in_review": "En examen", "offer_sent": "Offre envoyee", "confirmed": "Confirme", "completed": "Termine", "cancelled": "Annule"},
        "invoice_labels": {"none": "Aucune", "pending": "Ouverte", "sent": "Envoyee", "paid": "Payee", "overdue": "En retard"},
    },
    "it": {
        "thank_you": "Grazie per la sua richiesta, {name}!",
        "inquiry_received": "Abbiamo ricevuto la sua richiesta e le risponderemo entro 24 ore con un'offerta personalizzata.",
        "event_date": "Data", "location": "Luogo", "guests": "Ospiti", "event_type": "Tipo",
        "trucks": "Trucks", "budget": "Budget", "questions_contact": "Per domande contattateci a info@trucksonroad.ch o +41 79 696 98 99.",
        "greeting": "Cordiali saluti", "team": "Il team TrucksOnRoad",
        "new_inquiry": "NUOVA RICHIESTA", "new_inquiry_from": "Nuova richiesta da {name}",
        "name": "Nome", "email": "E-mail", "phone": "Telefono",
        "your_offer": "La sua offerta, {name}", "offer_intro": "Grazie per il suo interesse! Ecco la nostra offerta basata sulla sua richiesta:",
        "offer_follow_up": "La contatteremo a breve con le condizioni dettagliate. Non esiti a contattarci.",
        "status_update": "AGGIORNAMENTO", "hello": "Salve {name},",
        "status_in_review": "La sua richiesta e in fase di revisione. La contatteremo a breve.",
        "status_offer_sent": "Abbiamo preparato un'offerta per lei. Verifichi i dettagli.",
        "status_confirmed": "La sua prenotazione e confermata! Non vediamo l'ora del suo evento.",
        "status_completed": "Grazie per il suo ordine! Speriamo che l'evento sia stato un successo.",
        "status_cancelled": "La sua richiesta e stata annullata. Non esiti a contattarci.",
        "status_default": "Lo stato della sua richiesta e stato aggiornato: {status}",
        "event": "Evento", "at": "il",
        "invoice_label": "FATTURA", "invoice_word": "Fattura",
        "inv_pending": "E stata creata una fattura per il suo evento.",
        "inv_sent": "Le abbiamo inviato una fattura. Rispetti il termine di pagamento.",
        "inv_paid": "Grazie! Il suo pagamento e stato ricevuto.",
        "inv_overdue": "La sua fattura e scaduta. Verifichi il pagamento.",
        "inv_default": "Lo stato della sua fattura e stato aggiornato: {status}",
        "new_file": "NUOVO FILE", "file_added": "Un nuovo file e stato aggiunto alla sua richiesta:",
        "file_download": "Puo scaricare questo file nel suo portale cliente.",
        "reminder": "PROMEMORIA", "days_until": "Mancano solo {days} giorni al suo evento!",
        "ready_for_event": "Siamo pronti! Per domande contattateci a info@trucksonroad.ch o +41 79 696 98 99.",
        "subject_inquiry": "Richiesta ricevuta", "subject_offer": "La sua offerta da TrucksOnRoad",
        "subject_confirmed": "Prenotazione confermata!", "subject_completed": "Evento completato",
        "subject_cancelled": "Richiesta annullata", "subject_status": "Aggiornamento stato",
        "subject_inv_pending": "Fattura creata", "subject_inv_sent": "Fattura inviata",
        "subject_inv_paid": "Pagamento ricevuto", "subject_inv_overdue": "Fattura scaduta",
        "subject_reminder": "Mancano {days} giorni!",
        "pdf_offer": "Offerta", "pdf_created": "Creata il", "pdf_inquiry_nr": "Nr. richiesta",
        "pdf_customer": "Dati cliente", "pdf_event_details": "Dettagli evento", "pdf_indoor": "Interno/Esterno",
        "pdf_remarks": "Osservazioni", "pdf_disclaimer": "Questa offerta e senza impegno e valida 30 giorni.",
        "pdf_company": "Azienda", "pdf_date": "Data",
        "status_labels": {"new": "Nuovo", "in_review": "In esame", "offer_sent": "Offerta inviata", "confirmed": "Confermato", "completed": "Completato", "cancelled": "Annullato"},
        "invoice_labels": {"none": "Nessuna", "pending": "Aperta", "sent": "Inviata", "paid": "Pagata", "overdue": "Scaduta"},
    },
}


def get_email_t(lang: str = "de"):
    return EMAIL_I18N.get(lang, EMAIL_I18N["de"])


async def get_email_settings():
    s = await db.settings.find_one({"type": "general"}, {"_id": 0})
    return s or {}


async def send_email_background(to: str, subject: str, html_body: str):
    try:
        settings = await get_email_settings()
        host = settings.get("smtp_host", "smtp.gmail.com")
        port = settings.get("smtp_port", 587)
        sender = settings.get("smtp_email", "")
        password = settings.get("smtp_password", "")
        if not sender or not password:
            logger.warning("SMTP not configured, skipping email")
            return
        msg = MIMEMultipart("alternative")
        msg["From"] = sender
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html"))
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, to, msg.as_string())
        logger.info(f"Email sent to {to}")
    except Exception as e:
        logger.error(f"Email sending failed: {e}")


def send_email_sync(to_email, subject, html_body, settings):
    smtp_user = settings.get("smtp_user", "")
    smtp_pass = settings.get("smtp_password", "")
    smtp_host = settings.get("smtp_host", "smtp.gmail.com")
    smtp_port = settings.get("smtp_port", 587)
    if not smtp_user or not smtp_pass:
        return
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, to_email, msg.as_string())


# --- EMAIL TEMPLATE BUILDERS ---

def build_confirmation_email(inquiry: dict, lang: str = "de") -> str:
    t = get_email_t(lang)
    name = f"{inquiry.get('first_name', '')} {inquiry.get('last_name', '')}".strip() or inquiry.get('name', '')
    return f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:600px;margin:0 auto;background:#fafaf8;border:1px solid #e8e7e3;border-radius:12px;overflow:hidden;">
      <div style="background:#1a1a18;padding:2rem;text-align:center;">
        <span style="font-family:'Bebas Neue',Arial,sans-serif;font-size:1.6rem;letter-spacing:0.08em;">
          <span style="color:#f5f0e8;">TRUCKS</span><span style="color:#4db6ac;">ON</span><span style="color:#f5f0e8;">ROAD</span>
        </span>
      </div>
      <div style="padding:2rem;">
        <h2 style="color:#1a1a18;margin:0 0 1rem;">{t['thank_you'].format(name=name)}</h2>
        <p style="color:#6b6b64;line-height:1.6;">{t['inquiry_received']}</p>
        <div style="background:#fff;border:1px solid #e8e7e3;border-radius:8px;padding:1.25rem;margin:1.5rem 0;">
          <p style="margin:0.3rem 0;"><strong>{t['event_date']}:</strong> {inquiry.get('event_date', '-')}</p>
          <p style="margin:0.3rem 0;"><strong>{t['location']}:</strong> {inquiry.get('location', '-')}</p>
          <p style="margin:0.3rem 0;"><strong>{t['guests']}:</strong> {inquiry.get('guest_count', '-')}</p>
          <p style="margin:0.3rem 0;"><strong>{t['event_type']}:</strong> {inquiry.get('event_type', inquiry.get('concept', '-'))}</p>
        </div>
        <p style="color:#6b6b64;font-size:0.85rem;">{t['questions_contact']}</p>
      </div>
      <div style="background:#f0efeb;padding:1rem 2rem;text-align:center;font-size:0.75rem;color:#9c9c94;">
        TrucksOnRoad &middot; Bahnhofstrasse 75 &middot; 8620 Wetzikon
      </div>
    </div>"""


def build_admin_notification_email(inquiry: dict, lang: str = "de") -> str:
    t = get_email_t(lang)
    name = f"{inquiry.get('first_name', '')} {inquiry.get('last_name', '')}".strip() or inquiry.get('name', '')
    trucks = ', '.join(inquiry.get('selected_trucks', [])) or '-'
    return f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:600px;margin:0 auto;background:#fafaf8;border:1px solid #e8e7e3;border-radius:12px;overflow:hidden;">
      <div style="background:#1a1a18;padding:1.5rem 2rem;text-align:center;">
        <span style="font-family:'Bebas Neue',Arial,sans-serif;font-size:1.4rem;letter-spacing:0.08em;">
          <span style="color:#f5f0e8;">TRUCKS</span><span style="color:#4db6ac;">ON</span><span style="color:#f5f0e8;">ROAD</span>
        </span>
        <span style="color:#4db6ac;font-size:0.7rem;margin-left:0.5rem;">{t['new_inquiry']}</span>
      </div>
      <div style="padding:1.5rem 2rem;">
        <h3 style="color:#1a1a18;margin:0 0 1rem;">{t['new_inquiry_from'].format(name=name)}</h3>
        <table style="width:100%;font-size:0.85rem;border-collapse:collapse;">
          <tr><td style="padding:0.4rem 0;color:#6b6b64;width:120px;">{t['name']}</td><td>{name}</td></tr>
          <tr><td style="padding:0.4rem 0;color:#6b6b64;">{t['email']}</td><td>{inquiry.get('email', '-')}</td></tr>
          <tr><td style="padding:0.4rem 0;color:#6b6b64;">{t['phone']}</td><td>{inquiry.get('phone', '-')}</td></tr>
          <tr><td style="padding:0.4rem 0;color:#6b6b64;">{t['event_date']}</td><td>{inquiry.get('event_date', '-')}</td></tr>
          <tr><td style="padding:0.4rem 0;color:#6b6b64;">{t['location']}</td><td>{inquiry.get('location', '-')}</td></tr>
          <tr><td style="padding:0.4rem 0;color:#6b6b64;">{t['guests']}</td><td>{inquiry.get('guest_count', '-')}</td></tr>
          <tr><td style="padding:0.4rem 0;color:#6b6b64;">{t['event_type']}</td><td>{inquiry.get('event_type', inquiry.get('concept', '-'))}</td></tr>
          <tr><td style="padding:0.4rem 0;color:#6b6b64;">{t['trucks']}</td><td>{trucks}</td></tr>
          <tr><td style="padding:0.4rem 0;color:#6b6b64;">{t['budget']}</td><td>{inquiry.get('budget', '-')}</td></tr>
        </table>
      </div>
    </div>"""


def build_offer_email(inquiry: dict, lang: str = "de", confirm_url: str = "") -> str:
    t = get_email_t(lang)
    name = f"{inquiry.get('first_name', '')} {inquiry.get('last_name', '')}".strip() or inquiry.get('name', '')
    trucks = ', '.join(inquiry.get('selected_trucks', [])) or '-'
    amount = inquiry.get('invoice_amount', 0)
    amount_html = f'<p style="margin:0.3rem 0;font-size:1.1rem;"><strong>Betrag: CHF {amount:,.2f}</strong></p>' if amount else ''
    confirm_btn = f'''
        <div style="text-align:center;margin:1.5rem 0;">
          <a href="{confirm_url}" style="display:inline-block;background:#4db6ac;color:#fff;padding:0.8rem 2rem;border-radius:6px;text-decoration:none;font-weight:600;font-size:1rem;">Offerte bestätigen</a>
          <p style="color:#9c9c94;font-size:0.8rem;margin-top:0.5rem;">Oder antworten Sie direkt auf diese Email</p>
        </div>''' if confirm_url else ''
    return f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:600px;margin:0 auto;background:#fafaf8;border:1px solid #e8e7e3;border-radius:12px;overflow:hidden;">
      <div style="background:#1a1a18;padding:2rem;text-align:center;">
        <span style="font-family:'Bebas Neue',Arial,sans-serif;font-size:1.6rem;letter-spacing:0.08em;">
          <span style="color:#f5f0e8;">TRUCKS</span><span style="color:#4db6ac;">on</span><span style="color:#f5f0e8;">ROAD</span>
        </span>
      </div>
      <div style="padding:2rem;">
        <h2 style="color:#1a1a18;margin:0 0 1rem;">{t['your_offer'].format(name=name)}</h2>
        <p style="color:#6b6b64;line-height:1.6;">{t['offer_intro']}</p>
        <div style="background:#fff;border:1px solid #e8e7e3;border-radius:8px;padding:1.25rem;margin:1.5rem 0;">
          <p style="margin:0.3rem 0;"><strong>{t['event_date']}:</strong> {inquiry.get('event_date', '-')}</p>
          <p style="margin:0.3rem 0;"><strong>{t['location']}:</strong> {inquiry.get('location', '-')}</p>
          <p style="margin:0.3rem 0;"><strong>{t['guests']}:</strong> {inquiry.get('guest_count', '-')}</p>
          <p style="margin:0.3rem 0;"><strong>{t['trucks']}:</strong> {trucks}</p>
          <p style="margin:0.3rem 0;"><strong>{t['event_type']}:</strong> {inquiry.get('event_type', inquiry.get('concept', '-'))}</p>
          {amount_html}
        </div>
        {confirm_btn}
        <p style="color:#6b6b64;line-height:1.6;">{t['offer_follow_up']}</p>
        <p style="color:#6b6b64;font-size:0.85rem;margin-top:1.5rem;">{t['greeting']},<br/><strong>{t['team']}</strong></p>
      </div>
      <div style="background:#f0efeb;padding:1rem 2rem;text-align:center;font-size:0.75rem;color:#9c9c94;">
        TrucksOnRoad &middot; Bahnhofstrasse 75 &middot; 8620 Wetzikon
      </div>
    </div>"""


def build_status_notification_email(inquiry: dict, new_status: str, lang: str = "de") -> str:
    t = get_email_t(lang)
    name = f"{inquiry.get('first_name', '')} {inquiry.get('last_name', '')}".strip() or "Kunde"
    status_label = t["status_labels"].get(new_status, new_status)
    status_color = {"confirmed": "#22c55e", "completed": "#6b7280", "cancelled": "#ef4444", "offer_sent": "#8b5cf6"}.get(new_status, "#4db6ac")
    msg_key = f"status_{new_status}"
    msg = t.get(msg_key, t["status_default"].format(status=status_label))
    return f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:600px;margin:0 auto;background:#fafaf8;border:1px solid #e8e7e3;border-radius:12px;overflow:hidden;">
      <div style="background:#1a1a18;padding:1.5rem 2rem;text-align:center;">
        <span style="font-family:'Bebas Neue',Arial,sans-serif;font-size:1.4rem;letter-spacing:0.08em;">
          <span style="color:#f5f0e8;">TRUCKS</span><span style="color:#4db6ac;">ON</span><span style="color:#f5f0e8;">ROAD</span>
        </span>
        <span style="color:#4db6ac;font-size:0.7rem;margin-left:0.5rem;">{t['status_update']}</span>
      </div>
      <div style="padding:2rem;">
        <h2 style="color:#1a1a18;margin:0 0 0.5rem;">{t['hello'].format(name=name)}</h2>
        <div style="display:inline-block;background:{status_color};color:#fff;padding:0.3rem 0.8rem;border-radius:20px;font-size:0.8rem;font-weight:600;margin:0.5rem 0 1rem;">
          {status_label}
        </div>
        <p style="color:#6b6b64;line-height:1.7;margin-top:0.5rem;">{msg}</p>
        <div style="background:#fff;border:1px solid #e8e7e3;border-radius:8px;padding:1rem;margin:1.5rem 0;">
          <p style="margin:0.3rem 0;font-size:0.88rem;"><strong>{t['event']}:</strong> {inquiry.get('event_type', '-')} {t['at']} {inquiry.get('event_date', '-')}</p>
          <p style="margin:0.3rem 0;font-size:0.88rem;"><strong>{t['location']}:</strong> {inquiry.get('location', '-')}</p>
          <p style="margin:0.3rem 0;font-size:0.88rem;"><strong>{t['guests']}:</strong> {inquiry.get('guest_count', '-')}</p>
        </div>
        <p style="color:#6b6b64;font-size:0.85rem;">{t['questions_contact']}</p>
        <p style="color:#6b6b64;font-size:0.85rem;margin-top:1rem;">{t['greeting']},<br/><strong>{t['team']}</strong></p>
      </div>
      <div style="background:#f0efeb;padding:1rem 2rem;text-align:center;font-size:0.75rem;color:#9c9c94;">
        TrucksOnRoad &middot; Bahnhofstrasse 75 &middot; 8620 Wetzikon
      </div>
    </div>"""


def build_invoice_notification_email(inquiry: dict, invoice_status: str, invoice_amount: float = 0, lang: str = "de") -> str:
    t = get_email_t(lang)
    name = f"{inquiry.get('first_name', '')} {inquiry.get('last_name', '')}".strip() or "Kunde"
    inv_label = t["invoice_labels"].get(invoice_status, invoice_status)
    inv_color = {"pending": "#e8b931", "sent": "#8b5cf6", "paid": "#22c55e", "overdue": "#ef4444"}.get(invoice_status, "#6b7280")
    msg_key = f"inv_{invoice_status}"
    msg = t.get(msg_key, t["inv_default"].format(status=inv_label))
    amount_line = f'<p style="font-size:1.3rem;font-weight:700;color:#1a1a18;margin:0.5rem 0;">CHF {invoice_amount:,.2f}</p>' if invoice_amount > 0 else ""
    return f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:600px;margin:0 auto;background:#fafaf8;border:1px solid #e8e7e3;border-radius:12px;overflow:hidden;">
      <div style="background:#1a1a18;padding:1.5rem 2rem;text-align:center;">
        <span style="font-family:'Bebas Neue',Arial,sans-serif;font-size:1.4rem;letter-spacing:0.08em;">
          <span style="color:#f5f0e8;">TRUCKS</span><span style="color:#4db6ac;">ON</span><span style="color:#f5f0e8;">ROAD</span>
        </span>
        <span style="color:#4db6ac;font-size:0.7rem;margin-left:0.5rem;">{t['invoice_label']}</span>
      </div>
      <div style="padding:2rem;">
        <h2 style="color:#1a1a18;margin:0 0 0.5rem;">{t['hello'].format(name=name)}</h2>
        <div style="display:inline-block;background:{inv_color};color:#fff;padding:0.3rem 0.8rem;border-radius:20px;font-size:0.8rem;font-weight:600;margin:0.5rem 0 1rem;">
          {t['invoice_word']}: {inv_label}
        </div>
        <p style="color:#6b6b64;line-height:1.7;margin-top:0.5rem;">{msg}</p>
        <div style="background:#fff;border:1px solid #e8e7e3;border-radius:8px;padding:1.25rem;margin:1.5rem 0;text-align:center;">
          {amount_line}
          <p style="margin:0.3rem 0;font-size:0.88rem;color:#6b6b64;"><strong>{t['event']}:</strong> {inquiry.get('event_type', '-')} {t['at']} {inquiry.get('event_date', '-')}</p>
          <p style="margin:0.3rem 0;font-size:0.88rem;color:#6b6b64;"><strong>{t['location']}:</strong> {inquiry.get('location', '-')}</p>
        </div>
        <p style="color:#6b6b64;font-size:0.85rem;">{t['questions_contact']}</p>
        <p style="color:#6b6b64;font-size:0.85rem;margin-top:1rem;">{t['greeting']},<br/><strong>{t['team']}</strong></p>
      </div>
      <div style="background:#f0efeb;padding:1rem 2rem;text-align:center;font-size:0.75rem;color:#9c9c94;">
        TrucksOnRoad &middot; Bahnhofstrasse 75 &middot; 8620 Wetzikon
      </div>
    </div>"""


def build_file_upload_notification_email(inquiry: dict, filename: str, lang: str = "de") -> str:
    t = get_email_t(lang)
    name = f"{inquiry.get('first_name', '')} {inquiry.get('last_name', '')}".strip() or "Kunde"
    return f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:600px;margin:0 auto;background:#fafaf8;border:1px solid #e8e7e3;border-radius:12px;overflow:hidden;">
      <div style="background:#1a1a18;padding:1.5rem 2rem;text-align:center;">
        <span style="font-family:'Bebas Neue',Arial,sans-serif;font-size:1.4rem;letter-spacing:0.08em;">
          <span style="color:#f5f0e8;">TRUCKS</span><span style="color:#4db6ac;">ON</span><span style="color:#f5f0e8;">ROAD</span>
        </span>
        <span style="color:#4db6ac;font-size:0.7rem;margin-left:0.5rem;">{t['new_file']}</span>
      </div>
      <div style="padding:2rem;">
        <h2 style="color:#1a1a18;margin:0 0 1rem;">{t['hello'].format(name=name)}</h2>
        <p style="color:#6b6b64;line-height:1.7;">{t['file_added']}</p>
        <div style="background:#fff;border:1px solid #e8e7e3;border-radius:8px;padding:1rem;margin:1rem 0;display:flex;align-items:center;gap:0.5rem;">
          <span style="font-weight:600;color:#1a1a18;">{filename}</span>
        </div>
        <p style="color:#6b6b64;font-size:0.88rem;">{t['file_download']}</p>
        <p style="color:#6b6b64;font-size:0.85rem;margin-top:1rem;">{t['greeting']},<br/><strong>{t['team']}</strong></p>
      </div>
      <div style="background:#f0efeb;padding:1rem 2rem;text-align:center;font-size:0.75rem;color:#9c9c94;">
        TrucksOnRoad &middot; Bahnhofstrasse 75 &middot; 8620 Wetzikon
      </div>
    </div>"""


def build_event_reminder_email(inquiry: dict, days_until: int, lang: str = "de") -> str:
    t = get_email_t(lang)
    name = f"{inquiry.get('first_name', '')} {inquiry.get('last_name', '')}".strip() or "Kunde"
    return f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:600px;margin:0 auto;background:#fafaf8;border:1px solid #e8e7e3;border-radius:12px;overflow:hidden;">
      <div style="background:#1a1a18;padding:1.5rem 2rem;text-align:center;">
        <span style="font-family:'Bebas Neue',Arial,sans-serif;font-size:1.4rem;letter-spacing:0.08em;">
          <span style="color:#f5f0e8;">TRUCKS</span><span style="color:#4db6ac;">ON</span><span style="color:#f5f0e8;">ROAD</span>
        </span>
        <span style="color:#4db6ac;font-size:0.7rem;margin-left:0.5rem;">{t['reminder']}</span>
      </div>
      <div style="padding:2rem;">
        <h2 style="color:#1a1a18;margin:0 0 1rem;">{t['hello'].format(name=name)}</h2>
        <p style="color:#6b6b64;line-height:1.7;"><strong>{t['days_until'].format(days=days_until)}</strong></p>
        <div style="background:#fff;border:1px solid #e8e7e3;border-radius:8px;padding:1rem;margin:1.5rem 0;">
          <p style="margin:0.3rem 0;font-size:0.88rem;"><strong>{t['event']}:</strong> {inquiry.get('event_type', '-')} {t['at']} {inquiry.get('event_date', '-')}</p>
          <p style="margin:0.3rem 0;font-size:0.88rem;"><strong>{t['location']}:</strong> {inquiry.get('location', '-')}</p>
          <p style="margin:0.3rem 0;font-size:0.88rem;"><strong>{t['guests']}:</strong> {inquiry.get('guest_count', '-')}</p>
          <p style="margin:0.3rem 0;font-size:0.88rem;"><strong>{t['trucks']}:</strong> {', '.join(inquiry.get('selected_trucks', []))}</p>
        </div>
        <p style="color:#6b6b64;font-size:0.88rem;">{t['ready_for_event']}</p>
        <p style="color:#6b6b64;font-size:0.85rem;margin-top:1rem;">{t['greeting']},<br/><strong>{t['team']}</strong></p>
      </div>
      <div style="background:#f0efeb;padding:1rem 2rem;text-align:center;font-size:0.75rem;color:#9c9c94;">
        TrucksOnRoad &middot; Bahnhofstrasse 75 &middot; 8620 Wetzikon
      </div>
    </div>"""


def build_event_application_email(event: dict, custom_message: str, settings: dict) -> str:
    company = settings.get("company_name", "TrucksOnRoad")
    phone = settings.get("company_phone", "")
    email = settings.get("company_email", "")
    address = settings.get("company_address", "")
    return f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:600px;margin:0 auto;background:#fafaf8;border:1px solid #e8e7e3;border-radius:12px;overflow:hidden;">
      <div style="background:#1a1a18;padding:2rem;text-align:center;">
        <span style="font-family:'Bebas Neue',Arial,sans-serif;font-size:1.6rem;letter-spacing:0.08em;">
          <span style="color:#f5f0e8;">TRUCKS</span><span style="color:#4db6ac;">ON</span><span style="color:#f5f0e8;">ROAD</span>
        </span>
      </div>
      <div style="padding:2rem;">
        <h2 style="color:#1a1a18;margin:0 0 1rem;">Bewerbung: {event.get('name', 'Event')}</h2>
        <p style="color:#6b6b64;line-height:1.6;">{custom_message if custom_message else f"Guten Tag, wir von {company} sind ein Premium-Foodtruck-Unternehmen und moechten uns fuer Ihr Event '{event.get('name', '')}' bewerben."}</p>
        <div style="background:#fff;border:1px solid #e8e7e3;border-radius:8px;padding:1.25rem;margin:1.5rem 0;">
          <h3 style="color:#1a1a18;margin:0 0 0.75rem;">Unser Angebot</h3>
          <p style="color:#6b6b64;line-height:1.6;">Wir bieten massgeschneiderte Foodtruck-Erlebnisse fuer Events jeder Groesse. Unsere Trucks sind spezialisiert auf verschiedene Kuechen und Konzepte – von Gourmet-Burgern ueber Asian Fusion bis hin zu Dessert-Trucks.</p>
          <ul style="color:#6b6b64;line-height:1.8;">
            <li>Professionelle Ausstattung &amp; Hygiene</li>
            <li>Flexible Menuezusammenstellung</li>
            <li>Erfahrung mit Grossevents (500+ Gaeste)</li>
            <li>Kompletter Service inkl. Auf-/Abbau</li>
          </ul>
        </div>
        <p style="color:#6b6b64;line-height:1.6;">Wir wuerden uns ueber ein Gespraech freuen. Kontaktieren Sie uns gerne!</p>
        <div style="margin-top:1.5rem;padding-top:1rem;border-top:1px solid #e8e7e3;">
          <p style="color:#1a1a18;font-weight:600;margin:0;">{company}</p>
          <p style="color:#6b6b64;margin:0.25rem 0;">{address}</p>
          <p style="color:#6b6b64;margin:0.25rem 0;">Tel: {phone} | E-Mail: {email}</p>
        </div>
      </div>
    </div>"""


def build_event_scan_notification_email(all_new_events: list) -> str:
    event_rows = ""
    for ev in all_new_events[:20]:
        event_rows += f"""<tr>
            <td style="padding:8px 12px;border-bottom:1px solid #e8e7e3;font-size:0.85rem;">{ev['name']}</td>
            <td style="padding:8px 12px;border-bottom:1px solid #e8e7e3;font-size:0.85rem;">{ev['date']}</td>
            <td style="padding:8px 12px;border-bottom:1px solid #e8e7e3;font-size:0.85rem;">{ev['location']}</td>
            <td style="padding:8px 12px;border-bottom:1px solid #e8e7e3;font-size:0.85rem;">{ev['type']}</td>
        </tr>"""
    return f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:650px;margin:0 auto;background:#fafaf8;border:1px solid #e8e7e3;border-radius:12px;overflow:hidden;">
      <div style="background:#1a1a18;padding:2rem;text-align:center;">
        <span style="font-family:'Bebas Neue',Arial,sans-serif;font-size:1.6rem;letter-spacing:0.08em;">
          <span style="color:#f5f0e8;">TRUCKS</span><span style="color:#4db6ac;">ON</span><span style="color:#f5f0e8;">ROAD</span>
        </span>
      </div>
      <div style="padding:2rem;">
        <h2 style="color:#1a1a18;margin:0 0 0.5rem;">Event-Scout: {len(all_new_events)} neue Events gefunden</h2>
        <p style="color:#6b6b64;margin:0 0 1.5rem;">Der automatische Event-Scanner hat neue Schweizer Events gefunden:</p>
        <table style="width:100%;border-collapse:collapse;background:#fff;border:1px solid #e8e7e3;border-radius:8px;overflow:hidden;">
          <thead>
            <tr style="background:#f5f5f2;">
              <th style="padding:10px 12px;text-align:left;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;color:#6b6b64;">Event</th>
              <th style="padding:10px 12px;text-align:left;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;color:#6b6b64;">Datum</th>
              <th style="padding:10px 12px;text-align:left;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;color:#6b6b64;">Ort</th>
              <th style="padding:10px 12px;text-align:left;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;color:#6b6b64;">Typ</th>
            </tr>
          </thead>
          <tbody>{event_rows}</tbody>
        </table>
        {f'<p style="color:#6b6b64;margin-top:1rem;font-size:0.82rem;">... und {len(all_new_events) - 20} weitere Events</p>' if len(all_new_events) > 20 else ''}
        <p style="color:#6b6b64;margin-top:1.5rem;">Melden Sie sich im <a href="#" style="color:#4db6ac;font-weight:600;">Admin-Dashboard</a> an, um die Events zu verwalten und Bewerbungen zu versenden.</p>
      </div>
    </div>"""
