"""Initial content for legal documents (AGB, Datenschutz, Impressum) — seeded as version 1."""

LEGAL_SEED = {
    "agb": {
        "type": "agb",
        "title": "Allgemeine Geschäftsbedingungen",
        "subtitle": "Stand: Februar 2026 · Gültig für sämtliche Catering- und Foodtruck-Leistungen von TRUCKSonROAD.",
        "sections": [
            {
                "heading": "§ 1 Geltungsbereich",
                "content": (
                    "Die nachfolgenden Allgemeinen Geschäftsbedingungen (nachfolgend «AGB») gelten für sämtliche "
                    "Verträge, Leistungen und Angebote zwischen TRUCKSonROAD, Bahnhofstrasse 75, 8620 Wetzikon, "
                    "Schweiz (nachfolgend «Anbieter» oder «wir») und dem Kunden (nachfolgend «Auftraggeber» oder «Sie») "
                    "im Bereich mobiles Foodtruck-Catering, Eventverpflegung sowie damit verbundener Dienstleistungen.\n\n"
                    "Abweichende, entgegenstehende oder ergänzende Geschäftsbedingungen des Auftraggebers werden nur "
                    "dann Vertragsbestandteil, wenn der Anbieter ihrer Geltung ausdrücklich schriftlich zugestimmt hat."
                ),
            },
            {
                "heading": "§ 2 Vertragsabschluss & Buchung",
                "content": (
                    "Sämtliche Angebote des Anbieters sind freibleibend und unverbindlich, sofern sie nicht ausdrücklich "
                    "als verbindlich gekennzeichnet sind. Eine Anfrage über das Buchungsformular, per E-Mail, telefonisch "
                    "oder über das WhatsApp-Kontaktangebot stellt keinen Vertragsabschluss dar.\n\n"
                    "Der Vertrag kommt zustande, sobald der Anbieter die Buchung schriftlich (per E-Mail genügt) bestätigt "
                    "oder eine vom Anbieter erstellte Offerte vom Auftraggeber schriftlich oder per Online-Bestätigungslink "
                    "angenommen wurde. Massgebend für den Leistungsumfang ist die durch den Anbieter ausgestellte Offerte "
                    "bzw. Auftragsbestätigung."
                ),
            },
            {
                "heading": "§ 3 Preise, Mehrwertsteuer & Nebenkosten",
                "content": (
                    "Sämtliche Preise verstehen sich in Schweizer Franken (CHF). Die gesetzliche Mehrwertsteuer ist – "
                    "soweit anwendbar – im jeweiligen Angebot ausgewiesen oder wird zusätzlich verrechnet.\n\n"
                    "Anfahrtskosten werden auf Basis der einfachen Distanz vom Standort des Anbieters (8620 Wetzikon) zum "
                    "vereinbarten Veranstaltungsort berechnet und in der Offerte transparent ausgewiesen. Allfällige "
                    "Übernachtungskosten, Park-/Standgebühren, Bewilligungen sowie Sondereinsatzzeiten (Nachtzuschläge, "
                    "Sonn- und Feiertage) werden nach Aufwand zusätzlich verrechnet."
                ),
            },
            {
                "heading": "§ 4 Zahlungsbedingungen",
                "content": (
                    "Sofern nichts anderes vereinbart wurde, gelten folgende Zahlungsmodalitäten:\n\n"
                    "- **Anzahlung:** Bei Buchungen ab CHF 2'000.– behält sich der Anbieter eine Anzahlung von 30 % des "
                    "Auftragswerts vor, fällig innert 10 Tagen nach Auftragsbestätigung.\n"
                    "- **Restzahlung:** Die Schlussrechnung ist innert 14 Tagen nach Veranstaltungsdatum ohne Abzug zur "
                    "Zahlung fällig.\n"
                    "- **Zahlungsverzug:** Bei Zahlungsverzug ist der Anbieter berechtigt, Verzugszinsen in Höhe von 5 % "
                    "p.a. sowie eine angemessene Mahngebühr in Rechnung zu stellen."
                ),
            },
            {
                "heading": "§ 5 Leistungsumfang",
                "content": (
                    "Der Leistungsumfang ergibt sich abschliessend aus der schriftlichen Auftragsbestätigung / Offerte. "
                    "Mündliche Nebenabreden bedürfen zu ihrer Wirksamkeit der schriftlichen Bestätigung durch den Anbieter.\n\n"
                    "Geringfügige Abweichungen bei Menü-Komponenten (z.B. saisonale Zutaten, Lieferengpässe) bleiben "
                    "vorbehalten, sofern dadurch die Qualität und der Charakter des vereinbarten Angebots nicht "
                    "wesentlich beeinträchtigt werden."
                ),
            },
            {
                "heading": "§ 6 Anforderungen am Veranstaltungsort",
                "content": (
                    "Der Auftraggeber stellt dem Anbieter am Veranstaltungsort kostenfrei zur Verfügung:\n\n"
                    "- Eine ebene, befahrbare und tragfähige Standfläche entsprechend dem Platzbedarf des gebuchten "
                    "Trucks (in der Regel min. 6 × 4 m, je nach Truck grösser).\n"
                    "- Einen funktionsfähigen Stromanschluss (in der Regel 230 V / 16 A, bei grösseren Einsätzen "
                    "CEE 400 V / 16 A oder 32 A) in unmittelbarer Nähe (max. 25 m).\n"
                    "- Bei Bedarf Zugang zu Frischwasser sowie eine Möglichkeit zur Entsorgung von Abwasser im Rahmen "
                    "geltender lebensmittelrechtlicher Vorschriften.\n"
                    "- Sämtliche notwendigen behördlichen Bewilligungen für die Durchführung des Events am Standort "
                    "(z.B. Stand-, Strassen-, Patentbewilligung), sofern nicht ausdrücklich etwas anderes vereinbart wurde."
                ),
            },
            {
                "heading": "§ 7 Mitwirkungspflichten des Auftraggebers",
                "content": (
                    "Der Auftraggeber verpflichtet sich, alle für die ordnungsgemässe Leistungserbringung erforderlichen "
                    "Informationen rechtzeitig (spätestens 7 Tage vor dem Veranstaltungstermin) zur Verfügung zu stellen, "
                    "insbesondere:\n\n"
                    "- Anzahl Gäste (definitiv) sowie deren spezifische Anforderungen (Allergien, vegetarisch/vegan).\n"
                    "- Detaillierte Anfahrts- und Standortinformationen inkl. Kontaktperson vor Ort.\n"
                    "- Genauen Zeitplan mit Aufbau-, Service- und Abbauzeiten."
                ),
            },
            {
                "heading": "§ 8 Stornierung / Annullation",
                "content": (
                    "Der Auftraggeber kann den Auftrag schriftlich stornieren. Massgebend für die Berechnung der "
                    "Stornogebühr ist das Eingangsdatum der Stornierung beim Anbieter:\n\n"
                    "- Bis 60 Tage vor Veranstaltungsdatum: 10 % des Auftragswerts.\n"
                    "- Bis 30 Tage vor Veranstaltungsdatum: 30 % des Auftragswerts.\n"
                    "- Bis 14 Tage vor Veranstaltungsdatum: 60 % des Auftragswerts.\n"
                    "- Bis 7 Tage vor Veranstaltungsdatum: 80 % des Auftragswerts.\n"
                    "- Weniger als 7 Tage vor Veranstaltungsdatum: 100 % des Auftragswerts.\n\n"
                    "Bereits angefallene Drittkosten (z.B. Spezialeinkäufe, gebuchtes Personal) werden zusätzlich in voller "
                    "Höhe in Rechnung gestellt."
                ),
            },
            {
                "heading": "§ 9 Höhere Gewalt / unvorhersehbare Ereignisse",
                "content": (
                    "Ereignisse höherer Gewalt – insbesondere Naturkatastrophen, behördliche Anordnungen, Pandemie-"
                    "bedingte Versammlungsverbote, Krieg, Streik oder andere vom Anbieter nicht zu vertretende Umstände – "
                    "berechtigen beide Parteien, vom Vertrag zurückzutreten. In diesem Fall werden die bis zum Zeitpunkt "
                    "des Rücktritts tatsächlich angefallenen Aufwendungen verrechnet, weitergehende Ansprüche bestehen keine."
                ),
            },
            {
                "heading": "§ 10 Lebensmittelsicherheit & Allergene",
                "content": (
                    "Der Anbieter arbeitet nach dem HACCP-Konzept und den Vorgaben des Schweizer Lebensmittelgesetzes "
                    "(LMG) sowie der Lebensmittel- und Gebrauchsgegenständeverordnung (LGV). Informationen zu Allergenen "
                    "werden auf Anfrage zur Verfügung gestellt. Der Auftraggeber ist verpflichtet, besondere Allergien "
                    "oder Unverträglichkeiten der Gäste rechtzeitig schriftlich zu melden."
                ),
            },
            {
                "heading": "§ 11 Haftung",
                "content": (
                    "Der Anbieter haftet für nachweislich verschuldete Schäden nur bei Vorsatz oder grober Fahrlässigkeit. "
                    "Eine Haftung für Folgeschäden, entgangenen Gewinn oder Vermögensschäden ist – soweit gesetzlich "
                    "zulässig – ausgeschlossen. Die Haftung pro Schadenereignis ist auf den jeweiligen Auftragswert begrenzt.\n\n"
                    "Der Anbieter haftet nicht für Schäden, die durch Drittanbieter (z.B. vom Auftraggeber beigezogene "
                    "Dienstleister, Eventlocations) verursacht wurden, sowie für Schäden, die aus mangelnder Mitwirkung "
                    "des Auftraggebers entstehen."
                ),
            },
            {
                "heading": "§ 12 Datenschutz",
                "content": (
                    "Der Anbieter verarbeitet personenbezogene Daten ausschliesslich im Einklang mit dem Schweizer "
                    "Datenschutzgesetz (DSG) sowie – soweit anwendbar – der EU-Datenschutz-Grundverordnung (DSGVO). "
                    "Detaillierte Informationen zur Datenverarbeitung finden sich in der separaten "
                    "[Datenschutzerklärung](/datenschutz)."
                ),
            },
            {
                "heading": "§ 13 Bild- und Urheberrechte",
                "content": (
                    "Der Anbieter ist berechtigt, am Veranstaltungsort Foto- und Videoaufnahmen zu Werbe- und "
                    "Dokumentationszwecken anzufertigen, sofern darauf keine Personen erkennbar sind oder eine "
                    "entsprechende Einwilligung der abgebildeten Personen vorliegt. Der Auftraggeber wird vor dem Event "
                    "darüber informiert. Eine ausdrückliche Untersagung ist möglich."
                ),
            },
            {
                "heading": "§ 14 Reklamationen & Mängelrüge",
                "content": (
                    "Reklamationen sind unverzüglich, spätestens jedoch innert 7 Tagen nach Beendigung der Veranstaltung "
                    "schriftlich beim Anbieter geltend zu machen. Spätere Reklamationen können nicht mehr berücksichtigt "
                    "werden."
                ),
            },
            {
                "heading": "§ 15 Salvatorische Klausel",
                "content": (
                    "Sollte eine Bestimmung dieser AGB ganz oder teilweise unwirksam sein oder werden, so wird die "
                    "Wirksamkeit der übrigen Bestimmungen davon nicht berührt. Anstelle der unwirksamen Bestimmung gilt "
                    "diejenige als vereinbart, welche dem wirtschaftlichen Zweck der unwirksamen Bestimmung am nächsten kommt."
                ),
            },
            {
                "heading": "§ 16 Anwendbares Recht & Gerichtsstand",
                "content": (
                    "Es gilt ausschliesslich Schweizer Recht unter Ausschluss des UN-Kaufrechts (CISG). Ausschliesslicher "
                    "Gerichtsstand für sämtliche Streitigkeiten aus oder im Zusammenhang mit diesen AGB und den darauf "
                    "basierenden Verträgen ist – soweit gesetzlich zulässig – der Sitz des Anbieters in Wetzikon ZH.\n\n"
                    "**TRUCKSonROAD**\n"
                    "Bahnhofstrasse 75 · 8620 Wetzikon · Schweiz\n"
                    "info@truckonroad.ch · +41 79 696 98 99"
                ),
            },
        ],
    },
    "datenschutz": {
        "type": "datenschutz",
        "title": "Datenschutzerklärung",
        "subtitle": "Stand: Februar 2026 · DSGVO- und nDSG-konform · Schweizer Datenschutzgesetz (DSG/nDSG) sowie EU-Datenschutz-Grundverordnung (DSGVO).",
        "sections": [
            {
                "heading": "1. Verantwortliche Stelle",
                "content": (
                    "Verantwortlich für die Datenbearbeitung im Sinne des Schweizer Datenschutzgesetzes (DSG) sowie – "
                    "soweit der sachliche Anwendungsbereich eröffnet ist – im Sinne von Art. 4 Nr. 7 DSGVO ist:\n\n"
                    "**TRUCKSonROAD**\n"
                    "Bahnhofstrasse 75\n"
                    "8620 Wetzikon ZH · Schweiz\n"
                    "info@truckonroad.ch\n"
                    "Telefon: +41 79 696 98 99"
                ),
            },
            {
                "heading": "2. Allgemeine Hinweise & Geltungsbereich",
                "content": (
                    "Wir nehmen den Schutz Ihrer persönlichen Daten ernst und behandeln Ihre personenbezogenen Daten "
                    "vertraulich, in Übereinstimmung mit den gesetzlichen Datenschutzvorschriften sowie dieser "
                    "Datenschutzerklärung. Diese Erklärung gilt für alle Funktionen unserer Website "
                    "**www.trucksonroad.ch** sowie unserer angeschlossenen Services (Kundenkonto, Online-Buchung, "
                    "Newsletter, Kontaktformulare)."
                ),
            },
            {
                "heading": "3. Welche Daten wir erheben",
                "content": (
                    "Im Rahmen der Nutzung unserer Dienste verarbeiten wir folgende Kategorien personenbezogener Daten:\n\n"
                    "- **Stammdaten:** Vor- und Nachname, Anrede, Firmenbezeichnung.\n"
                    "- **Kontaktdaten:** E-Mail-Adresse, Telefonnummer, Postadresse.\n"
                    "- **Buchungs- und Vertragsdaten:** Eventdatum, Eventort, Anzahl Gäste, gewählte Trucks/Menüs, "
                    "Bemerkungen, Zahlungsstatus.\n"
                    "- **Login-/Authentifizierungsdaten:** E-Mail-Adresse, 6-stelliger Einmal-Verifizierungscode (OTP), "
                    "Session-Token.\n"
                    "- **Technische Nutzungsdaten:** IP-Adresse, Browser, Betriebssystem, Referrer-URL, Zugriffszeitpunkt "
                    "(Server-Logfiles).\n"
                    "- **Kommunikationsdaten:** Inhalt von Anfragen, E-Mail-Verkehr, hochgeladene Dateien (z.B. Eventpläne)."
                ),
            },
            {
                "heading": "4. Zwecke der Datenverarbeitung",
                "content": (
                    "- Bearbeitung von Anfragen, Erstellung von Offerten und Abwicklung von Catering-Aufträgen.\n"
                    "- Authentifizierung von Kunden im persönlichen Kundenbereich (passwortloses OTP-Login).\n"
                    "- Buchhalterische und steuerliche Pflichten (Aufbewahrungsfristen 10 Jahre gem. Schweizer OR Art. 958f).\n"
                    "- Bereitstellung, Sicherheit und Optimierung unserer Website.\n"
                    "- Marketing- und Informationszwecke, sofern eine Einwilligung vorliegt."
                ),
            },
            {
                "heading": "5. Rechtsgrundlagen der Verarbeitung",
                "content": (
                    "Die Verarbeitung Ihrer Daten stützen wir auf folgende Rechtsgrundlagen:\n\n"
                    "- **Art. 6 Abs. 1 lit. b DSGVO / Art. 31 Abs. 2 lit. a DSG:** Vertragserfüllung und vorvertragliche "
                    "Massnahmen (Buchungs- und Anfrageprozesse).\n"
                    "- **Art. 6 Abs. 1 lit. c DSGVO / Art. 31 Abs. 1 DSG:** Erfüllung gesetzlicher Pflichten (z.B. "
                    "Buchhaltung).\n"
                    "- **Art. 6 Abs. 1 lit. f DSGVO / Art. 31 Abs. 1 DSG:** Berechtigtes Interesse (IT-Sicherheit, "
                    "statistische Auswertung, Direktwerbung an Bestandskunden).\n"
                    "- **Art. 6 Abs. 1 lit. a DSGVO / Art. 6 DSG:** Einwilligung (z.B. Newsletter, optionale Cookies)."
                ),
            },
            {
                "heading": "6. Cookies & ähnliche Technologien",
                "content": (
                    "Unsere Website verwendet sogenannte Cookies. Cookies sind kleine Textdateien, die auf Ihrem Endgerät "
                    "gespeichert werden. Wir unterscheiden:\n\n"
                    "- **Technisch notwendige Cookies:** Erforderlich für den Betrieb der Website und für die "
                    "Login-Funktion (Session-Cookies). Rechtsgrundlage: berechtigtes Interesse.\n"
                    "- **Funktionale Cookies:** Speicherung Ihrer Spracheinstellung (DE/EN/FR/IT/ES). Rechtsgrundlage: "
                    "berechtigtes Interesse.\n"
                    "- **Analyse- und Marketing-Cookies:** Werden – soweit eingesetzt – nur mit Ihrer ausdrücklichen "
                    "Einwilligung gesetzt.\n\n"
                    "Sie können das Setzen von Cookies in Ihrem Browser jederzeit unterbinden bzw. gesetzte Cookies "
                    "löschen. Dies kann jedoch die Funktionsfähigkeit der Website einschränken."
                ),
            },
            {
                "heading": "7. Server-Logfiles",
                "content": (
                    "Beim Aufruf unserer Website werden automatisch Daten an unseren Hosting-Provider übermittelt und in "
                    "Server-Logfiles temporär gespeichert (IP-Adresse, Datum/Uhrzeit, Browsertyp, Betriebssystem, "
                    "Referrer-URL). Eine Zusammenführung dieser Daten mit anderen Datenquellen erfolgt nicht. Die Logfiles "
                    "werden nach max. 30 Tagen anonymisiert oder gelöscht. Rechtsgrundlage: berechtigtes Interesse an "
                    "einem sicheren Betrieb."
                ),
            },
            {
                "heading": "8. Kontakt- und Buchungsformular",
                "content": (
                    "Wenn Sie uns über das Anfrageformular, das Buchungs-Tool oder per E-Mail kontaktieren, werden Ihre "
                    "Angaben zur Bearbeitung der Anfrage und für allfällige Anschlussfragen bei uns gespeichert. Diese "
                    "Daten geben wir nicht ohne Ihre Einwilligung weiter. Die Speicherung erfolgt für die Dauer der "
                    "Bearbeitung sowie anschliessend im Rahmen der gesetzlichen Aufbewahrungspflichten."
                ),
            },
            {
                "heading": "9. Kundenkonto & passwortloser OTP-Login",
                "content": (
                    "Für die Nutzung des Kundenbereichs erstellen wir ein Konto auf Basis Ihrer E-Mail-Adresse. Die "
                    "Anmeldung erfolgt passwortlos: Wir senden Ihnen einen 6-stelligen Einmal-Code (OTP) per E-Mail, der "
                    "nach Eingabe und maximal 10 Minuten seine Gültigkeit verliert. Es werden keine Passwörter "
                    "gespeichert. Verifizierungscodes werden nach Verwendung oder Ablauf gelöscht."
                ),
            },
            {
                "heading": "10. E-Mail-Versand",
                "content": (
                    "Für den Versand von Bestätigungs-, Offert- und Service-E-Mails nutzen wir Gmail (Google) als "
                    "SMTP-Provider. Die Verarbeitung erfolgt auf Grundlage unseres berechtigten Interesses an einer "
                    "zuverlässigen Kommunikation. Eine Datenübermittlung in Drittstaaten kann erfolgen; wir stützen diese "
                    "auf die Standardvertragsklauseln der EU-Kommission gemäss Art. 46 DSGVO."
                ),
            },
            {
                "heading": "11. Eingebundene Dienste Dritter",
                "content": (
                    "- **Google Maps:** Wir nutzen Google Maps zur Standortdarstellung und zur Berechnung der "
                    "Anfahrtsdistanz. Anbieter: Google Ireland Limited, Gordon House, Barrow Street, Dublin 4, Irland.\n"
                    "- **WhatsApp Business:** Auf unserer Seite verlinken wir einen WhatsApp-Kontakt. Sobald Sie diesen "
                    "aktiv anklicken, gelten die Datenschutzregeln von WhatsApp Inc. / Meta Platforms Ireland Ltd."
                ),
            },
            {
                "heading": "12. Datenweitergabe an Dritte",
                "content": (
                    "Eine Übermittlung Ihrer Daten an Dritte findet nur statt, soweit dies\n\n"
                    "- zur Vertragserfüllung erforderlich ist (z.B. an Logistikpartner für die Anlieferung),\n"
                    "- aufgrund gesetzlicher Vorgaben oder behördlicher Anordnung erforderlich ist,\n"
                    "- für die Geltendmachung, Ausübung oder Verteidigung von Rechtsansprüchen notwendig ist,\n"
                    "- oder Sie ausdrücklich eingewilligt haben."
                ),
            },
            {
                "heading": "13. Speicherdauer",
                "content": (
                    "Wir speichern Ihre Daten nur so lange, wie es zur Erfüllung der genannten Zwecke erforderlich ist "
                    "oder wie es gesetzliche Aufbewahrungspflichten vorschreiben (insbesondere 10 Jahre für "
                    "Geschäftsunterlagen gemäss Schweizer Obligationenrecht). Anschliessend werden die Daten gelöscht "
                    "oder anonymisiert."
                ),
            },
            {
                "heading": "14. Ihre Rechte",
                "content": (
                    "Sie haben jederzeit das Recht:\n\n"
                    "- **auf Auskunft** (Art. 15 DSGVO / Art. 25 DSG) über die zu Ihrer Person gespeicherten Daten;\n"
                    "- **auf Berichtigung** unrichtiger Daten (Art. 16 DSGVO / Art. 32 DSG);\n"
                    "- **auf Löschung** (Art. 17 DSGVO);\n"
                    "- **auf Einschränkung der Verarbeitung** (Art. 18 DSGVO);\n"
                    "- **auf Datenübertragbarkeit** (Art. 20 DSGVO);\n"
                    "- **auf Widerspruch gegen die Verarbeitung** (Art. 21 DSGVO);\n"
                    "- **auf Widerruf erteilter Einwilligungen** mit Wirkung für die Zukunft (Art. 7 Abs. 3 DSGVO).\n\n"
                    "Zur Ausübung Ihrer Rechte genügt eine formlose Mitteilung per E-Mail an info@truckonroad.ch."
                ),
            },
            {
                "heading": "15. Beschwerderecht",
                "content": (
                    "Sie haben das Recht, sich bei einer zuständigen Datenschutzbehörde zu beschweren. Zuständige "
                    "Aufsichtsbehörde in der Schweiz ist:\n\n"
                    "**Eidgenössischer Datenschutz- und Öffentlichkeitsbeauftragter (EDÖB)**\n"
                    "Feldeggweg 1, CH-3003 Bern\n"
                    "www.edoeb.admin.ch\n\n"
                    "Für betroffene Personen mit Wohnsitz in der EU steht zusätzlich ein Beschwerderecht bei der jeweils "
                    "zuständigen nationalen Aufsichtsbehörde gemäss Art. 77 DSGVO offen."
                ),
            },
            {
                "heading": "16. SSL-/TLS-Verschlüsselung",
                "content": (
                    "Aus Sicherheitsgründen und zum Schutz der Übertragung vertraulicher Inhalte verwendet unsere Website "
                    "eine SSL- bzw. TLS-Verschlüsselung. Eine verschlüsselte Verbindung erkennen Sie an «https://» in der "
                    "Adresszeile Ihres Browsers sowie am Schloss-Symbol."
                ),
            },
            {
                "heading": "17. Aktualität & Änderung dieser Datenschutzerklärung",
                "content": (
                    "Wir behalten uns vor, diese Datenschutzerklärung jederzeit anzupassen, um sie geänderten "
                    "Rechtsvorschriften oder Änderungen unserer Leistungen anzupassen. Für den erneuten Besuch gilt dann "
                    "die jeweils aktuelle Fassung.\n\n"
                    "Bei Fragen zum Datenschutz erreichen Sie uns unter info@truckonroad.ch."
                ),
            },
        ],
    },
    "impressum": {
        "type": "impressum",
        "title": "Impressum",
        "subtitle": "Anbieterkennzeichnung gemäss Art. 322 StGB sowie nach den Bestimmungen des Bundesgesetzes über den unlauteren Wettbewerb (UWG).",
        "sections": [
            {
                "heading": "Anbieter",
                "content": (
                    "**TRUCKSonROAD**\n"
                    "Bahnhofstrasse 75\n"
                    "8620 Wetzikon ZH\n"
                    "Schweiz"
                ),
            },
            {
                "heading": "Kontakt",
                "content": (
                    "Telefon: +41 79 696 98 99\n"
                    "E-Mail: info@truckonroad.ch\n"
                    "Web: www.trucksonroad.ch"
                ),
            },
            {
                "heading": "Tätigkeit",
                "content": (
                    "Foodtruck-Catering, Eventverpflegung sowie damit verbundene Dienstleistungen für Firmen-, Privat- "
                    "und Festivalveranstaltungen in der gesamten Schweiz."
                ),
            },
            {
                "heading": "Aufsichtsbehörde / Lebensmittelrecht",
                "content": (
                    "Wir arbeiten gemäss den Vorgaben des Schweizer Lebensmittelgesetzes (LMG) und der Lebensmittel- "
                    "und Gebrauchsgegenständeverordnung (LGV). Zuständige Aufsicht: Kantonales Labor des Kantons Zürich."
                ),
            },
            {
                "heading": "Verantwortlich für den Inhalt",
                "content": "TRUCKSonROAD, Bahnhofstrasse 75, 8620 Wetzikon ZH",
            },
            {
                "heading": "Streitbeilegung",
                "content": (
                    "Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer "
                    "Verbraucherschlichtungsstelle teilzunehmen. Anwendbares Recht: Schweizer Recht. Gerichtsstand: "
                    "Wetzikon ZH."
                ),
            },
            {
                "heading": "Haftungsausschluss",
                "content": (
                    "Der Anbieter übernimmt keinerlei Gewähr hinsichtlich der inhaltlichen Richtigkeit, Genauigkeit, "
                    "Aktualität, Zuverlässigkeit und Vollständigkeit der Informationen. Haftungsansprüche gegen den "
                    "Anbieter wegen Schäden materieller oder immaterieller Art, welche aus dem Zugriff oder der Nutzung "
                    "bzw. Nichtnutzung der veröffentlichten Informationen, durch Missbrauch der Verbindung oder durch "
                    "technische Störungen entstanden sind, werden ausgeschlossen.\n\n"
                    "Sämtliche Angebote sind unverbindlich. Der Anbieter behält es sich ausdrücklich vor, Teile der "
                    "Seiten oder das gesamte Angebot ohne gesonderte Ankündigung zu verändern, zu ergänzen, zu löschen "
                    "oder die Veröffentlichung zeitweise oder endgültig einzustellen."
                ),
            },
            {
                "heading": "Haftung für Links",
                "content": (
                    "Verweise und Links auf Webseiten Dritter liegen ausserhalb unseres Verantwortungsbereichs. Es wird "
                    "jegliche Verantwortung für solche Webseiten abgelehnt. Der Zugriff und die Nutzung solcher Webseiten "
                    "erfolgen auf eigene Gefahr des Nutzers oder der Nutzerin."
                ),
            },
            {
                "heading": "Urheberrechte",
                "content": (
                    "Die Urheber- und alle anderen Rechte an Inhalten, Bildern, Fotos oder anderen Dateien auf der "
                    "Website gehören ausschliesslich TRUCKSonROAD oder den speziell genannten Rechtsinhabern. Für die "
                    "Reproduktion jeglicher Elemente ist die schriftliche Zustimmung der Urheberrechtsträger im Voraus "
                    "einzuholen."
                ),
            },
            {
                "heading": "Datenschutz",
                "content": (
                    "Hinweise zur Verarbeitung personenbezogener Daten finden Sie in unserer separaten "
                    "[Datenschutzerklärung](/datenschutz)."
                ),
            },
        ],
    },
}
