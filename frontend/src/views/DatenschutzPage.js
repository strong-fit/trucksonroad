"use client";

export default function DatenschutzPage() {
  return (
    <div className="sf-page sf-legal" data-testid="datenschutz-page">
      <div className="sf-page-hero">
        <div className="sf-section-tag" data-testid="datenschutz-tag">Rechtliches</div>
        <h1 className="sf-section-title" style={{ fontSize: 'clamp(2rem, 4vw, 3rem)' }}>
          Daten<span className="gold">schutz&shy;erklärung</span>
        </h1>
        <p className="sf-page-hero-desc">
          Stand: Februar 2026 · DSGVO- und nDSG-konform · Schweizer Datenschutzgesetz (DSG/nDSG)
          sowie EU-Datenschutz-Grundverordnung (DSGVO).
        </p>
      </div>

      <section className="sf-section" style={{ paddingTop: '2rem' }}>
        <div className="sf-legal-content" data-testid="datenschutz-content">

          <h2>1. Verantwortliche Stelle</h2>
          <p>
            Verantwortlich für die Datenbearbeitung im Sinne des Schweizer Datenschutzgesetzes
            (DSG) sowie – soweit der sachliche Anwendungsbereich eröffnet ist – im Sinne von
            Art. 4 Nr. 7 DSGVO ist:
          </p>
          <p>
            <strong>TRUCKSonROAD</strong><br />
            Bahnhofstrasse 75<br />
            8620 Wetzikon ZH · Schweiz<br />
            <a href="mailto:info@truckonroad.ch">info@truckonroad.ch</a><br />
            Telefon: +41 79 696 98 99
          </p>

          <h2>2. Allgemeine Hinweise & Geltungsbereich</h2>
          <p>
            Wir nehmen den Schutz Ihrer persönlichen Daten ernst und behandeln Ihre
            personenbezogenen Daten vertraulich, in Übereinstimmung mit den gesetzlichen
            Datenschutzvorschriften sowie dieser Datenschutzerklärung. Diese Erklärung gilt für
            alle Funktionen unserer Website <strong>www.trucksonroad.ch</strong> sowie unserer
            angeschlossenen Services (Kundenkonto, Online-Buchung, Newsletter, Kontaktformulare).
          </p>

          <h2>3. Welche Daten wir erheben</h2>
          <p>
            Im Rahmen der Nutzung unserer Dienste verarbeiten wir folgende Kategorien
            personenbezogener Daten:
          </p>
          <ul>
            <li><strong>Stammdaten:</strong> Vor- und Nachname, Anrede, Firmenbezeichnung.</li>
            <li><strong>Kontaktdaten:</strong> E-Mail-Adresse, Telefonnummer, Postadresse.</li>
            <li><strong>Buchungs- und Vertragsdaten:</strong> Eventdatum, Eventort, Anzahl Gäste,
              gewählte Trucks/Menüs, Bemerkungen, Zahlungsstatus.</li>
            <li><strong>Login-/Authentifizierungsdaten:</strong> E-Mail-Adresse,
              6-stelliger Einmal-Verifizierungscode (OTP), Session-Token.</li>
            <li><strong>Technische Nutzungsdaten:</strong> IP-Adresse, Browser, Betriebssystem,
              Referrer-URL, Zugriffszeitpunkt (Server-Logfiles).</li>
            <li><strong>Kommunikationsdaten:</strong> Inhalt von Anfragen, E-Mail-Verkehr,
              hochgeladene Dateien (z.B. Eventpläne).</li>
          </ul>

          <h2>4. Zwecke der Datenverarbeitung</h2>
          <ul>
            <li>Bearbeitung von Anfragen, Erstellung von Offerten und Abwicklung von
              Catering-Aufträgen.</li>
            <li>Authentifizierung von Kunden im persönlichen Kundenbereich (passwortloses
              OTP-Login).</li>
            <li>Buchhalterische und steuerliche Pflichten (Aufbewahrungsfristen 10 Jahre gem.
              Schweizer OR Art. 958f).</li>
            <li>Bereitstellung, Sicherheit und Optimierung unserer Website.</li>
            <li>Marketing- und Informationszwecke, sofern eine Einwilligung vorliegt.</li>
          </ul>

          <h2>5. Rechtsgrundlagen der Verarbeitung</h2>
          <p>Die Verarbeitung Ihrer Daten stützen wir auf folgende Rechtsgrundlagen:</p>
          <ul>
            <li><strong>Art. 6 Abs. 1 lit. b DSGVO / Art. 31 Abs. 2 lit. a DSG:</strong>
              Vertragserfüllung und vorvertragliche Massnahmen (Buchungs- und Anfrageprozesse).</li>
            <li><strong>Art. 6 Abs. 1 lit. c DSGVO / Art. 31 Abs. 1 DSG:</strong> Erfüllung
              gesetzlicher Pflichten (z.B. Buchhaltung).</li>
            <li><strong>Art. 6 Abs. 1 lit. f DSGVO / Art. 31 Abs. 1 DSG:</strong> Berechtigtes
              Interesse (IT-Sicherheit, statistische Auswertung, Direktwerbung an Bestandskunden).</li>
            <li><strong>Art. 6 Abs. 1 lit. a DSGVO / Art. 6 DSG:</strong> Einwilligung (z.B.
              Newsletter, optionale Cookies).</li>
          </ul>

          <h2>6. Cookies & ähnliche Technologien</h2>
          <p>
            Unsere Website verwendet sogenannte Cookies. Cookies sind kleine Textdateien, die auf
            Ihrem Endgerät gespeichert werden. Wir unterscheiden:
          </p>
          <ul>
            <li><strong>Technisch notwendige Cookies:</strong> Erforderlich für den Betrieb der
              Website und für die Login-Funktion (Session-Cookies). Rechtsgrundlage: berechtigtes
              Interesse.</li>
            <li><strong>Funktionale Cookies:</strong> Speicherung Ihrer Spracheinstellung
              (DE/EN/FR/IT/ES). Rechtsgrundlage: berechtigtes Interesse.</li>
            <li><strong>Analyse- und Marketing-Cookies:</strong> Werden – soweit eingesetzt – nur
              mit Ihrer ausdrücklichen Einwilligung gesetzt.</li>
          </ul>
          <p>
            Sie können das Setzen von Cookies in Ihrem Browser jederzeit unterbinden bzw.
            gesetzte Cookies löschen. Dies kann jedoch die Funktionsfähigkeit der Website
            einschränken.
          </p>

          <h2>7. Server-Logfiles</h2>
          <p>
            Beim Aufruf unserer Website werden automatisch Daten an unseren Hosting-Provider
            übermittelt und in Server-Logfiles temporär gespeichert (IP-Adresse, Datum/Uhrzeit,
            Browsertyp, Betriebssystem, Referrer-URL). Eine Zusammenführung dieser Daten mit
            anderen Datenquellen erfolgt nicht. Die Logfiles werden nach max. 30 Tagen
            anonymisiert oder gelöscht. Rechtsgrundlage: berechtigtes Interesse an einem
            sicheren Betrieb.
          </p>

          <h2>8. Kontakt- und Buchungsformular</h2>
          <p>
            Wenn Sie uns über das Anfrageformular, das Buchungs-Tool oder per E-Mail
            kontaktieren, werden Ihre Angaben zur Bearbeitung der Anfrage und für allfällige
            Anschlussfragen bei uns gespeichert. Diese Daten geben wir nicht ohne Ihre
            Einwilligung weiter. Die Speicherung erfolgt für die Dauer der Bearbeitung sowie
            anschliessend im Rahmen der gesetzlichen Aufbewahrungspflichten.
          </p>

          <h2>9. Kundenkonto & passwortloser OTP-Login</h2>
          <p>
            Für die Nutzung des Kundenbereichs erstellen wir ein Konto auf Basis Ihrer
            E-Mail-Adresse. Die Anmeldung erfolgt passwortlos: Wir senden Ihnen einen
            6-stelligen Einmal-Code (OTP) per E-Mail, der nach Eingabe und maximal 10 Minuten
            seine Gültigkeit verliert. Es werden keine Passwörter gespeichert. Verifizierungscodes
            werden nach Verwendung oder Ablauf gelöscht.
          </p>

          <h2>10. E-Mail-Versand</h2>
          <p>
            Für den Versand von Bestätigungs-, Offert- und Service-E-Mails nutzen wir Gmail
            (Google) als SMTP-Provider. Die Verarbeitung erfolgt auf Grundlage unseres
            berechtigten Interesses an einer zuverlässigen Kommunikation. Eine Datenübermittlung
            in Drittstaaten kann erfolgen; wir stützen diese auf die Standardvertragsklauseln der
            EU-Kommission gemäss Art. 46 DSGVO.
          </p>

          <h2>11. Eingebundene Dienste Dritter</h2>
          <ul>
            <li><strong>Google Maps:</strong> Wir nutzen Google Maps zur Standortdarstellung und
              zur Berechnung der Anfahrtsdistanz. Anbieter: Google Ireland Limited, Gordon
              House, Barrow Street, Dublin 4, Irland.</li>
            <li><strong>WhatsApp Business:</strong> Auf unserer Seite verlinken wir einen
              WhatsApp-Kontakt. Sobald Sie diesen aktiv anklicken, gelten die Datenschutzregeln
              von WhatsApp Inc. / Meta Platforms Ireland Ltd.</li>
          </ul>

          <h2>12. Datenweitergabe an Dritte</h2>
          <p>
            Eine Übermittlung Ihrer Daten an Dritte findet nur statt, soweit dies
          </p>
          <ul>
            <li>zur Vertragserfüllung erforderlich ist (z.B. an Logistikpartner für die
              Anlieferung),</li>
            <li>aufgrund gesetzlicher Vorgaben oder behördlicher Anordnung erforderlich ist,</li>
            <li>für die Geltendmachung, Ausübung oder Verteidigung von Rechtsansprüchen
              notwendig ist,</li>
            <li>oder Sie ausdrücklich eingewilligt haben.</li>
          </ul>

          <h2>13. Speicherdauer</h2>
          <p>
            Wir speichern Ihre Daten nur so lange, wie es zur Erfüllung der genannten Zwecke
            erforderlich ist oder wie es gesetzliche Aufbewahrungspflichten vorschreiben
            (insbesondere 10 Jahre für Geschäftsunterlagen gemäss Schweizer
            Obligationenrecht). Anschliessend werden die Daten gelöscht oder anonymisiert.
          </p>

          <h2>14. Ihre Rechte</h2>
          <p>Sie haben jederzeit das Recht:</p>
          <ul>
            <li><strong>auf Auskunft</strong> (Art. 15 DSGVO / Art. 25 DSG) über die zu Ihrer
              Person gespeicherten Daten;</li>
            <li><strong>auf Berichtigung</strong> unrichtiger Daten (Art. 16 DSGVO / Art. 32 DSG);</li>
            <li><strong>auf Löschung</strong> (Art. 17 DSGVO);</li>
            <li><strong>auf Einschränkung der Verarbeitung</strong> (Art. 18 DSGVO);</li>
            <li><strong>auf Datenübertragbarkeit</strong> (Art. 20 DSGVO);</li>
            <li><strong>auf Widerspruch gegen die Verarbeitung</strong> (Art. 21 DSGVO);</li>
            <li><strong>auf Widerruf erteilter Einwilligungen</strong> mit Wirkung für die
              Zukunft (Art. 7 Abs. 3 DSGVO).</li>
          </ul>
          <p>
            Zur Ausübung Ihrer Rechte genügt eine formlose Mitteilung per E-Mail an
            <a href="mailto:info@truckonroad.ch"> info@truckonroad.ch</a>.
          </p>

          <h2>15. Beschwerderecht</h2>
          <p>
            Sie haben das Recht, sich bei einer zuständigen Datenschutzbehörde zu beschweren.
            Zuständige Aufsichtsbehörde in der Schweiz ist:
          </p>
          <p>
            <strong>Eidgenössischer Datenschutz- und Öffentlichkeitsbeauftragter (EDÖB)</strong><br />
            Feldeggweg 1, CH-3003 Bern<br />
            <a href="https://www.edoeb.admin.ch" target="_blank" rel="noopener noreferrer">www.edoeb.admin.ch</a>
          </p>
          <p>
            Für betroffene Personen mit Wohnsitz in der EU steht zusätzlich ein Beschwerderecht
            bei der jeweils zuständigen nationalen Aufsichtsbehörde gemäss Art. 77 DSGVO offen.
          </p>

          <h2>16. SSL-/TLS-Verschlüsselung</h2>
          <p>
            Aus Sicherheitsgründen und zum Schutz der Übertragung vertraulicher Inhalte verwendet
            unsere Website eine SSL- bzw. TLS-Verschlüsselung. Eine verschlüsselte Verbindung
            erkennen Sie an «https://» in der Adresszeile Ihres Browsers sowie am Schloss-Symbol.
          </p>

          <h2>17. Aktualität & Änderung dieser Datenschutzerklärung</h2>
          <p>
            Wir behalten uns vor, diese Datenschutzerklärung jederzeit anzupassen, um sie
            geänderten Rechtsvorschriften oder Änderungen unserer Leistungen anzupassen. Für den
            erneuten Besuch gilt dann die jeweils aktuelle Fassung.
          </p>

          <div className="sf-legal-meta">
            <p>
              Bei Fragen zum Datenschutz erreichen Sie uns unter
              <a href="mailto:info@truckonroad.ch"> info@truckonroad.ch</a>.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
