"use client";

export default function ImpressumPage() {
  return (
    <div className="sf-page sf-legal" data-testid="impressum-page">
      <div className="sf-page-hero">
        <div className="sf-section-tag" data-testid="impressum-tag">Rechtliches</div>
        <h1 className="sf-section-title" style={{ fontSize: 'clamp(2rem, 4vw, 3rem)' }}>
          Im<span className="gold">pressum</span>
        </h1>
        <p className="sf-page-hero-desc">
          Anbieterkennzeichnung gemäss Art. 322 StGB sowie nach den Bestimmungen des
          Bundesgesetzes über den unlauteren Wettbewerb (UWG).
        </p>
      </div>

      <section className="sf-section" style={{ paddingTop: '2rem' }}>
        <div className="sf-legal-content" data-testid="impressum-content">

          <h2>Anbieter</h2>
          <p>
            <strong>TRUCKSonROAD</strong><br />
            Bahnhofstrasse 75<br />
            8620 Wetzikon ZH<br />
            Schweiz
          </p>

          <h2>Kontakt</h2>
          <p>
            Telefon: +41 79 696 98 99<br />
            E-Mail: <a href="mailto:info@truckonroad.ch">info@truckonroad.ch</a><br />
            Web: www.trucksonroad.ch
          </p>

          <h2>Tätigkeit</h2>
          <p>
            Foodtruck-Catering, Eventverpflegung sowie damit verbundene Dienstleistungen für
            Firmen-, Privat- und Festivalveranstaltungen in der gesamten Schweiz.
          </p>

          <h2>Aufsichtsbehörde / Lebensmittelrecht</h2>
          <p>
            Wir arbeiten gemäss den Vorgaben des Schweizer Lebensmittelgesetzes (LMG) und der
            Lebensmittel- und Gebrauchsgegenständeverordnung (LGV). Zuständige Aufsicht:
            Kantonales Labor des Kantons Zürich.
          </p>

          <h2>Verantwortlich für den Inhalt</h2>
          <p>TRUCKSonROAD, Bahnhofstrasse 75, 8620 Wetzikon ZH</p>

          <h2>Streitbeilegung</h2>
          <p>
            Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer
            Verbraucherschlichtungsstelle teilzunehmen. Anwendbares Recht: Schweizer Recht.
            Gerichtsstand: Wetzikon ZH.
          </p>

          <h2>Haftungsausschluss</h2>
          <p>
            Der Anbieter übernimmt keinerlei Gewähr hinsichtlich der inhaltlichen Richtigkeit,
            Genauigkeit, Aktualität, Zuverlässigkeit und Vollständigkeit der Informationen.
            Haftungsansprüche gegen den Anbieter wegen Schäden materieller oder immaterieller
            Art, welche aus dem Zugriff oder der Nutzung bzw. Nichtnutzung der veröffentlichten
            Informationen, durch Missbrauch der Verbindung oder durch technische Störungen
            entstanden sind, werden ausgeschlossen.
          </p>
          <p>
            Sämtliche Angebote sind unverbindlich. Der Anbieter behält es sich ausdrücklich vor,
            Teile der Seiten oder das gesamte Angebot ohne gesonderte Ankündigung zu verändern,
            zu ergänzen, zu löschen oder die Veröffentlichung zeitweise oder endgültig
            einzustellen.
          </p>

          <h2>Haftung für Links</h2>
          <p>
            Verweise und Links auf Webseiten Dritter liegen ausserhalb unseres
            Verantwortungsbereichs. Es wird jegliche Verantwortung für solche Webseiten
            abgelehnt. Der Zugriff und die Nutzung solcher Webseiten erfolgen auf eigene Gefahr
            des Nutzers oder der Nutzerin.
          </p>

          <h2>Urheberrechte</h2>
          <p>
            Die Urheber- und alle anderen Rechte an Inhalten, Bildern, Fotos oder anderen
            Dateien auf der Website gehören ausschliesslich TRUCKSonROAD oder den speziell
            genannten Rechtsinhabern. Für die Reproduktion jeglicher Elemente ist die
            schriftliche Zustimmung der Urheberrechtsträger im Voraus einzuholen.
          </p>

          <h2>Datenschutz</h2>
          <p>
            Hinweise zur Verarbeitung personenbezogener Daten finden Sie in unserer separaten
            <a href="/datenschutz" className="sf-legal-link"> Datenschutzerklärung</a>.
          </p>

          <div className="sf-legal-meta">
            <p>Stand: Februar 2026</p>
          </div>
        </div>
      </section>
    </div>
  );
}
