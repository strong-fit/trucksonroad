"use client";

export default function AgbPage() {
  return (
    <div className="sf-page sf-legal" data-testid="agb-page">
      <div className="sf-page-hero">
        <div className="sf-section-tag" data-testid="agb-tag">Rechtliches</div>
        <h1 className="sf-section-title" style={{ fontSize: 'clamp(2rem, 4vw, 3rem)' }}>
          Allgemeine <span className="gold">Geschäftsbedingungen</span>
        </h1>
        <p className="sf-page-hero-desc">
          Stand: Februar 2026 · Gültig für sämtliche Catering- und Foodtruck-Leistungen von TRUCKSonROAD.
        </p>
      </div>

      <section className="sf-section" style={{ paddingTop: '2rem' }}>
        <div className="sf-legal-content" data-testid="agb-content">

          <h2>§ 1 Geltungsbereich</h2>
          <p>
            Die nachfolgenden Allgemeinen Geschäftsbedingungen (nachfolgend «AGB») gelten für
            sämtliche Verträge, Leistungen und Angebote zwischen TRUCKSonROAD, Bahnhofstrasse 75,
            8620 Wetzikon, Schweiz (nachfolgend «Anbieter» oder «wir») und dem Kunden
            (nachfolgend «Auftraggeber» oder «Sie») im Bereich mobiles Foodtruck-Catering,
            Eventverpflegung sowie damit verbundener Dienstleistungen.
          </p>
          <p>
            Abweichende, entgegenstehende oder ergänzende Geschäftsbedingungen des
            Auftraggebers werden nur dann Vertragsbestandteil, wenn der Anbieter ihrer Geltung
            ausdrücklich schriftlich zugestimmt hat.
          </p>

          <h2>§ 2 Vertragsabschluss & Buchung</h2>
          <p>
            Sämtliche Angebote des Anbieters sind freibleibend und unverbindlich, sofern sie
            nicht ausdrücklich als verbindlich gekennzeichnet sind. Eine Anfrage über das
            Buchungsformular, per E-Mail, telefonisch oder über das WhatsApp-Kontaktangebot
            stellt keinen Vertragsabschluss dar.
          </p>
          <p>
            Der Vertrag kommt zustande, sobald der Anbieter die Buchung schriftlich (per E-Mail
            genügt) bestätigt oder eine vom Anbieter erstellte Offerte vom Auftraggeber
            schriftlich oder per Online-Bestätigungslink angenommen wurde. Massgebend für den
            Leistungsumfang ist die durch den Anbieter ausgestellte Offerte bzw.
            Auftragsbestätigung.
          </p>

          <h2>§ 3 Preise, Mehrwertsteuer & Nebenkosten</h2>
          <p>
            Sämtliche Preise verstehen sich in Schweizer Franken (CHF). Die gesetzliche
            Mehrwertsteuer ist – soweit anwendbar – im jeweiligen Angebot ausgewiesen oder wird
            zusätzlich verrechnet.
          </p>
          <p>
            Anfahrtskosten werden auf Basis der einfachen Distanz vom Standort des Anbieters
            (8620 Wetzikon) zum vereinbarten Veranstaltungsort berechnet und in der Offerte
            transparent ausgewiesen. Allfällige Übernachtungskosten, Park-/Standgebühren,
            Bewilligungen sowie Sondereinsatzzeiten (Nachtzuschläge, Sonn- und Feiertage) werden
            nach Aufwand zusätzlich verrechnet.
          </p>

          <h2>§ 4 Zahlungsbedingungen</h2>
          <p>
            Sofern nichts anderes vereinbart wurde, gelten folgende Zahlungsmodalitäten:
          </p>
          <ul>
            <li>
              <strong>Anzahlung:</strong> Bei Buchungen ab CHF 2&apos;000.– behält sich der Anbieter eine
              Anzahlung von 30 % des Auftragswerts vor, fällig innert 10 Tagen nach
              Auftragsbestätigung.
            </li>
            <li>
              <strong>Restzahlung:</strong> Die Schlussrechnung ist innert 14 Tagen nach
              Veranstaltungsdatum ohne Abzug zur Zahlung fällig.
            </li>
            <li>
              <strong>Zahlungsverzug:</strong> Bei Zahlungsverzug ist der Anbieter berechtigt,
              Verzugszinsen in Höhe von 5 % p.a. sowie eine angemessene Mahngebühr in Rechnung zu
              stellen.
            </li>
          </ul>

          <h2>§ 5 Leistungsumfang</h2>
          <p>
            Der Leistungsumfang ergibt sich abschliessend aus der schriftlichen
            Auftragsbestätigung / Offerte. Mündliche Nebenabreden bedürfen zu ihrer Wirksamkeit
            der schriftlichen Bestätigung durch den Anbieter.
          </p>
          <p>
            Geringfügige Abweichungen bei Menü-Komponenten (z.B. saisonale Zutaten,
            Lieferengpässe) bleiben vorbehalten, sofern dadurch die Qualität und der Charakter
            des vereinbarten Angebots nicht wesentlich beeinträchtigt werden.
          </p>

          <h2>§ 6 Anforderungen am Veranstaltungsort</h2>
          <p>
            Der Auftraggeber stellt dem Anbieter am Veranstaltungsort kostenfrei zur Verfügung:
          </p>
          <ul>
            <li>Eine ebene, befahrbare und tragfähige Standfläche entsprechend dem Platzbedarf des
              gebuchten Trucks (in der Regel min. 6 × 4 m, je nach Truck grösser).</li>
            <li>Einen funktionsfähigen Stromanschluss (in der Regel 230 V / 16 A, bei grösseren
              Einsätzen CEE 400 V / 16 A oder 32 A) in unmittelbarer Nähe (max. 25 m).</li>
            <li>Bei Bedarf Zugang zu Frischwasser sowie eine Möglichkeit zur Entsorgung von
              Abwasser im Rahmen geltender lebensmittelrechtlicher Vorschriften.</li>
            <li>Sämtliche notwendigen behördlichen Bewilligungen für die Durchführung des Events
              am Standort (z.B. Stand-, Strassen-, Patentbewilligung), sofern nicht ausdrücklich
              etwas anderes vereinbart wurde.</li>
          </ul>

          <h2>§ 7 Mitwirkungspflichten des Auftraggebers</h2>
          <p>
            Der Auftraggeber verpflichtet sich, alle für die ordnungsgemässe Leistungserbringung
            erforderlichen Informationen rechtzeitig (spätestens 7 Tage vor dem
            Veranstaltungstermin) zur Verfügung zu stellen, insbesondere:
          </p>
          <ul>
            <li>Anzahl Gäste (definitiv) sowie deren spezifische Anforderungen
              (Allergien, vegetarisch/vegan).</li>
            <li>Detaillierte Anfahrts- und Standortinformationen inkl. Kontaktperson vor Ort.</li>
            <li>Genauen Zeitplan mit Aufbau-, Service- und Abbauzeiten.</li>
          </ul>

          <h2>§ 8 Stornierung / Annullation</h2>
          <p>
            Der Auftraggeber kann den Auftrag schriftlich stornieren. Massgebend für die
            Berechnung der Stornogebühr ist das Eingangsdatum der Stornierung beim Anbieter:
          </p>
          <ul>
            <li>Bis 60 Tage vor Veranstaltungsdatum: 10 % des Auftragswerts.</li>
            <li>Bis 30 Tage vor Veranstaltungsdatum: 30 % des Auftragswerts.</li>
            <li>Bis 14 Tage vor Veranstaltungsdatum: 60 % des Auftragswerts.</li>
            <li>Bis 7 Tage vor Veranstaltungsdatum: 80 % des Auftragswerts.</li>
            <li>Weniger als 7 Tage vor Veranstaltungsdatum: 100 % des Auftragswerts.</li>
          </ul>
          <p>
            Bereits angefallene Drittkosten (z.B. Spezialeinkäufe, gebuchtes Personal) werden
            zusätzlich in voller Höhe in Rechnung gestellt.
          </p>

          <h2>§ 9 Höhere Gewalt / unvorhersehbare Ereignisse</h2>
          <p>
            Ereignisse höherer Gewalt – insbesondere Naturkatastrophen, behördliche
            Anordnungen, Pandemie-bedingte Versammlungsverbote, Krieg, Streik oder andere vom
            Anbieter nicht zu vertretende Umstände – berechtigen beide Parteien, vom Vertrag
            zurückzutreten. In diesem Fall werden die bis zum Zeitpunkt des Rücktritts
            tatsächlich angefallenen Aufwendungen verrechnet, weitergehende Ansprüche bestehen
            keine.
          </p>

          <h2>§ 10 Lebensmittelsicherheit & Allergene</h2>
          <p>
            Der Anbieter arbeitet nach dem HACCP-Konzept und den Vorgaben des Schweizer
            Lebensmittelgesetzes (LMG) sowie der Lebensmittel- und Gebrauchsgegenständeverordnung
            (LGV). Informationen zu Allergenen werden auf Anfrage zur Verfügung gestellt. Der
            Auftraggeber ist verpflichtet, besondere Allergien oder Unverträglichkeiten der
            Gäste rechtzeitig schriftlich zu melden.
          </p>

          <h2>§ 11 Haftung</h2>
          <p>
            Der Anbieter haftet für nachweislich verschuldete Schäden nur bei Vorsatz oder
            grober Fahrlässigkeit. Eine Haftung für Folgeschäden, entgangenen Gewinn oder
            Vermögensschäden ist – soweit gesetzlich zulässig – ausgeschlossen. Die Haftung pro
            Schadenereignis ist auf den jeweiligen Auftragswert begrenzt.
          </p>
          <p>
            Der Anbieter haftet nicht für Schäden, die durch Drittanbieter (z.B. vom Auftraggeber
            beigezogene Dienstleister, Eventlocations) verursacht wurden, sowie für Schäden, die
            aus mangelnder Mitwirkung des Auftraggebers entstehen.
          </p>

          <h2>§ 12 Datenschutz</h2>
          <p>
            Der Anbieter verarbeitet personenbezogene Daten ausschliesslich im Einklang mit dem
            Schweizer Datenschutzgesetz (DSG) sowie – soweit anwendbar – der EU-Datenschutz-
            Grundverordnung (DSGVO). Detaillierte Informationen zur Datenverarbeitung finden sich
            in der separaten <a href="/datenschutz" className="sf-legal-link">Datenschutzerklärung</a>.
          </p>

          <h2>§ 13 Bild- und Urheberrechte</h2>
          <p>
            Der Anbieter ist berechtigt, am Veranstaltungsort Foto- und Videoaufnahmen zu Werbe-
            und Dokumentationszwecken anzufertigen, sofern darauf keine Personen erkennbar sind
            oder eine entsprechende Einwilligung der abgebildeten Personen vorliegt. Der
            Auftraggeber wird vor dem Event darüber informiert. Eine ausdrückliche Untersagung
            ist möglich.
          </p>

          <h2>§ 14 Reklamationen & Mängelrüge</h2>
          <p>
            Reklamationen sind unverzüglich, spätestens jedoch innert 7 Tagen nach Beendigung
            der Veranstaltung schriftlich beim Anbieter geltend zu machen. Spätere Reklamationen
            können nicht mehr berücksichtigt werden.
          </p>

          <h2>§ 15 Salvatorische Klausel</h2>
          <p>
            Sollte eine Bestimmung dieser AGB ganz oder teilweise unwirksam sein oder werden, so
            wird die Wirksamkeit der übrigen Bestimmungen davon nicht berührt. Anstelle der
            unwirksamen Bestimmung gilt diejenige als vereinbart, welche dem wirtschaftlichen
            Zweck der unwirksamen Bestimmung am nächsten kommt.
          </p>

          <h2>§ 16 Anwendbares Recht & Gerichtsstand</h2>
          <p>
            Es gilt ausschliesslich Schweizer Recht unter Ausschluss des UN-Kaufrechts (CISG).
            Ausschliesslicher Gerichtsstand für sämtliche Streitigkeiten aus oder im Zusammenhang
            mit diesen AGB und den darauf basierenden Verträgen ist – soweit gesetzlich zulässig
            – der Sitz des Anbieters in Wetzikon ZH.
          </p>

          <div className="sf-legal-meta">
            <p>
              <strong>TRUCKSonROAD</strong><br />
              Bahnhofstrasse 75 · 8620 Wetzikon · Schweiz<br />
              <a href="mailto:info@truckonroad.ch">info@truckonroad.ch</a> · +41 79 696 98 99
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
