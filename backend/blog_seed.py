import uuid
from datetime import datetime, timezone

BLOG_SEED = [
    {
        "id": str(uuid.uuid4()),
        "slug": "foodtruck-mieten-schweiz-guide",
        "title_de": "Foodtruck mieten in der Schweiz: Der komplette Guide 2026",
        "title_en": "Renting a Food Truck in Switzerland: The Complete 2026 Guide",
        "title_fr": "Louer un Food Truck en Suisse: Le guide complet 2026",
        "title_it": "Noleggiare un Food Truck in Svizzera: La guida completa 2026",
        "excerpt_de": "Alles, was du wissen musst, bevor du einen Foodtruck fuer dein Event in der Schweiz buchst: Kosten, Planung, Tipps und die besten Konzepte.",
        "excerpt_en": "Everything you need to know before booking a food truck for your event in Switzerland: costs, planning, tips and the best concepts.",
        "excerpt_fr": "Tout ce que vous devez savoir avant de louer un food truck pour votre evenement en Suisse: couts, planification, conseils et meilleurs concepts.",
        "excerpt_it": "Tutto cio che devi sapere prima di noleggiare un food truck per il tuo evento in Svizzera: costi, pianificazione, consigli e migliori concetti.",
        "content_de": """## Foodtruck mieten in der Schweiz – So geht's richtig

Ein Foodtruck bringt nicht nur leckeres Essen, sondern auch Atmosphaere und Unterhaltung auf euer Event. Doch worauf solltet ihr bei der Buchung achten?

### Was kostet ein Foodtruck?

Die Kosten haengen von mehreren Faktoren ab:
- **Gaestezahl**: 50-100 Gaeste ab CHF 1'500, 200+ Gaeste ab CHF 3'000
- **Konzept**: Burger, Bowls oder Empanadas – jedes Konzept hat seine eigene Kalkulation
- **Anfahrt**: Je weiter der Einsatzort, desto hoeher die Logistikkosten
- **Dauer**: Halbtags- oder Ganztageseinsatz

### Die richtige Planung

1. **Frueh buchen**: Mindestens 4-8 Wochen im Voraus, bei Grossevents noch frueher
2. **Gaestezahl schaetzen**: Lieber grosszuegig planen als zu knapp kalkulieren
3. **Platzbedarf pruefen**: Ein Foodtruck braucht ca. 6m x 3m Stellflaeche
4. **Strom und Wasser**: Die meisten Trucks benoetigen 230V/16A Stromanschluss

### Welcher Truck passt zu eurem Event?

- **Firmenanlass**: Burger Truck oder Bowl Truck – schnelle Ausgabe, vielfaeltig
- **Hochzeit**: Empanadas Truck oder Retro Trailer – elegant und besonders
- **Festival**: Mehrere Trucks kombiniert fuer maximale Vielfalt
- **Geburtstag**: Pocket Bowl Truck – kompakt und kreativ

### Unser Tipp

Fragt unverbindlich an und lasst euch ein massgeschneidertes Angebot erstellen. Bei TrucksOnRoad bekommt ihr innerhalb von 24 Stunden eine Antwort mit allen Details.""",
        "content_en": """## Renting a Food Truck in Switzerland – How to Do It Right

A food truck brings not only delicious food but also atmosphere and entertainment to your event. But what should you look out for when booking?

### How much does a food truck cost?

Costs depend on several factors:
- **Guest count**: 50-100 guests from CHF 1,500, 200+ guests from CHF 3,000
- **Concept**: Burgers, bowls or empanadas – each concept has its own pricing
- **Travel distance**: The further the location, the higher the logistics costs
- **Duration**: Half-day or full-day service

### The right planning

1. **Book early**: At least 4-8 weeks in advance, for large events even earlier
2. **Estimate guest count**: Better to plan generously than too tightly
3. **Check space requirements**: A food truck needs approx. 6m x 3m parking space
4. **Power and water**: Most trucks require 230V/16A power supply

### Which truck fits your event?

- **Corporate event**: Burger Truck or Bowl Truck – fast service, versatile
- **Wedding**: Empanadas Truck or Retro Trailer – elegant and special
- **Festival**: Multiple trucks combined for maximum variety
- **Birthday**: Pocket Bowl Truck – compact and creative

### Our tip

Submit a non-binding inquiry and get a tailored offer. At TrucksOnRoad, you'll receive a response within 24 hours with all the details.""",
        "content_fr": """## Louer un Food Truck en Suisse – Comment bien faire

Un food truck apporte non seulement de la bonne cuisine, mais aussi de l'ambiance et du divertissement a votre evenement. Mais a quoi faut-il faire attention lors de la reservation?

### Combien coute un food truck?

Les couts dependent de plusieurs facteurs:
- **Nombre d'invites**: 50-100 invites a partir de CHF 1'500, 200+ invites a partir de CHF 3'000
- **Concept**: Burgers, bowls ou empanadas
- **Distance**: Plus le lieu est eloigne, plus les frais de logistique sont eleves
- **Duree**: Service a la demi-journee ou a la journee complete

### La bonne planification

1. **Reservez tot**: Au moins 4 a 8 semaines a l'avance
2. **Estimez le nombre d'invites**: Mieux vaut planifier largement
3. **Verifiez l'espace necessaire**: Un food truck a besoin d'environ 6m x 3m
4. **Electricite et eau**: La plupart des trucks necessitent 230V/16A

### Notre conseil

Faites une demande sans engagement et recevez une offre sur mesure. Chez TrucksOnRoad, vous obtiendrez une reponse dans les 24 heures.""",
        "content_it": """## Noleggiare un Food Truck in Svizzera – Come fare bene

Un food truck porta non solo cibo delizioso, ma anche atmosfera e intrattenimento al vostro evento. Ma a cosa bisogna fare attenzione quando si prenota?

### Quanto costa un food truck?

I costi dipendono da diversi fattori:
- **Numero di ospiti**: 50-100 ospiti da CHF 1'500, 200+ ospiti da CHF 3'000
- **Concetto**: Burger, bowl o empanadas
- **Distanza**: Piu lontano e il luogo, piu alti sono i costi logistici
- **Durata**: Servizio mezza giornata o giornata intera

### La pianificazione giusta

1. **Prenotate in anticipo**: Almeno 4-8 settimane prima
2. **Stimate il numero di ospiti**: Meglio pianificare generosamente
3. **Controllate lo spazio necessario**: Un food truck ha bisogno di circa 6m x 3m
4. **Elettricita e acqua**: La maggior parte dei truck necessita di 230V/16A

### Il nostro consiglio

Fate una richiesta senza impegno e ricevete un'offerta su misura. Con TrucksOnRoad riceverete una risposta entro 24 ore.""",
        "category": "guide",
        "image": "https://images.unsplash.com/photo-1565123409695-7b5ef63a2efb?w=800&q=80",
        "tags": ["Foodtruck", "Schweiz", "Mieten", "Event", "Catering"],
        "author": "TrucksOnRoad Team",
        "is_published": True,
        "created_at": "2026-01-15T10:00:00+00:00",
        "updated_at": "2026-01-15T10:00:00+00:00"
    },
    {
        "id": str(uuid.uuid4()),
        "slug": "beste-foodtruck-locations-zuerich",
        "title_de": "Die 5 besten Foodtruck-Locations in Zuerich",
        "title_en": "The 5 Best Food Truck Locations in Zurich",
        "title_fr": "Les 5 meilleurs emplacements pour food trucks a Zurich",
        "title_it": "Le 5 migliori posizioni per food truck a Zurigo",
        "excerpt_de": "Wo stehen Foodtrucks in Zuerich am besten? Wir zeigen euch die Top-Standorte fuer Events, Mittagessen und Strassenfeste.",
        "excerpt_en": "Where do food trucks work best in Zurich? We show you the top locations for events, lunch and street festivals.",
        "excerpt_fr": "Ou les food trucks fonctionnent-ils le mieux a Zurich? Nous vous montrons les meilleurs emplacements.",
        "excerpt_it": "Dove funzionano meglio i food truck a Zurigo? Vi mostriamo le migliori posizioni.",
        "content_de": """## Die besten Foodtruck-Standorte in Zuerich

Zuerich ist eine der foodtruck-freundlichsten Staedte der Schweiz. Ob am See, im Park oder auf dem Firmengelaende – es gibt zahlreiche grossartige Locations.

### 1. Buerkliplatz / Seeufer

Der Klassiker fuer Open-Air-Events direkt am Zuerichsee. Perfekt fuer Sommerevents, Firmenfeiern und Festivals. Viel Laufkundschaft und traumhafte Kulisse.

### 2. Europaallee / HB-Areal

Modernes Umfeld direkt beim Hauptbahnhof. Ideal fuer Lunch-Catering, After-Work-Events und Firmenapereos. Hohe Frequenz und gut erreichbar.

### 3. Josefwiese

Der beliebte Park im Kreis 5 ist perfekt fuer entspannte Events, Quartierfeste und Familienaenlaesse. Gruene Umgebung und viel Platz.

### 4. Kaserne / Kulturquartier

Kreatives Umfeld fuer Food-Markets, kulturelle Veranstaltungen und Nachtmaerkte. Die Mischung aus Kultur und Kulinarik zieht ein junges Publikum an.

### 5. Firmengelaende im Glattal

Die Businessparks in Wallisellen, Opfikon und Kloten bieten viel Platz fuer Foodtruck-Events. Ideal fuer Teambuilding, Sommerfeste und Mitarbeiterevents.

### Tipps fuer Veranstalter

- **Bewilligungen frueh einholen**: Die Stadt Zuerich hat klare Vorschriften fuer Foodtruck-Standplaetze
- **Strom organisieren**: Nicht ueberall gibt es 230V-Anschluesse – plant voraus
- **Kombination ist King**: Mehrere Trucks an einem Standort bieten mehr Auswahl und ziehen mehr Besucher an""",
        "content_en": """## The Best Food Truck Locations in Zurich

Zurich is one of the most food truck-friendly cities in Switzerland. Whether by the lake, in the park or on company premises – there are numerous great locations.

### 1. Buerkliplatz / Lakefront

The classic for open-air events right on Lake Zurich. Perfect for summer events, corporate celebrations and festivals.

### 2. Europaallee / Main Station Area

Modern environment right next to the main station. Ideal for lunch catering, after-work events and corporate aperitifs.

### 3. Josefwiese

The popular park in District 5 is perfect for relaxed events, neighborhood festivals and family gatherings.

### 4. Kaserne / Cultural Quarter

Creative environment for food markets, cultural events and night markets.

### 5. Business Parks in Glattal

Business parks in Wallisellen, Opfikon and Kloten offer plenty of space for food truck events.""",
        "content_fr": """## Les meilleurs emplacements pour food trucks a Zurich

Zurich est l'une des villes les plus accueillantes pour les food trucks en Suisse.

### 1. Buerkliplatz / Bord du lac
### 2. Europaallee / Gare centrale
### 3. Josefwiese
### 4. Kaserne / Quartier culturel
### 5. Parcs d'affaires dans le Glattal

Chaque emplacement a ses avantages uniques pour differents types d'evenements.""",
        "content_it": """## Le migliori posizioni per food truck a Zurigo

Zurigo e una delle citta piu accoglienti per i food truck in Svizzera.

### 1. Buerkliplatz / Lungolago
### 2. Europaallee / Stazione centrale
### 3. Josefwiese
### 4. Kaserne / Quartiere culturale
### 5. Parchi commerciali nel Glattal

Ogni posizione ha i suoi vantaggi unici per diversi tipi di eventi.""",
        "category": "locations",
        "image": "https://images.unsplash.com/photo-1515542622106-78bda8ba0e5b?w=800&q=80",
        "tags": ["Zuerich", "Locations", "Foodtruck", "Standorte", "Events"],
        "author": "TrucksOnRoad Team",
        "is_published": True,
        "created_at": "2026-02-01T10:00:00+00:00",
        "updated_at": "2026-02-01T10:00:00+00:00"
    },
    {
        "id": str(uuid.uuid4()),
        "slug": "firmenanlass-catering-tipps",
        "title_de": "Firmenanlass planen: 7 Tipps fuer unvergessliches Foodtruck-Catering",
        "title_en": "Planning a Corporate Event: 7 Tips for Unforgettable Food Truck Catering",
        "title_fr": "Planifier un evenement d'entreprise: 7 conseils pour un catering food truck inoubliable",
        "title_it": "Pianificare un evento aziendale: 7 consigli per un catering food truck indimenticabile",
        "excerpt_de": "Vom Teambuilding bis zur Weihnachtsfeier: So wird euer Firmenanlass mit Foodtruck-Catering zum vollen Erfolg.",
        "excerpt_en": "From team building to Christmas parties: How to make your corporate event a complete success with food truck catering.",
        "excerpt_fr": "Du team building a la fete de Noel: Comment faire de votre evenement d'entreprise un succes total avec le catering food truck.",
        "excerpt_it": "Dal team building alla festa di Natale: Come rendere il vostro evento aziendale un successo totale con il catering food truck.",
        "content_de": """## 7 Tipps fuer perfektes Foodtruck-Catering beim Firmenanlass

Foodtrucks sind die moderne Alternative zum klassischen Catering – und bei Mitarbeitenden extrem beliebt. Hier sind unsere Tipps aus ueber 500 Events.

### 1. Fruehzeitig planen
Je beliebter der Termin (Sommer, Weihnachtszeit), desto frueher solltet ihr buchen. Unsere Empfehlung: mindestens 6 Wochen vorher.

### 2. Die richtige Truck-Kombination waehlen
Fuer 100-200 Gaeste empfehlen wir 2 Trucks mit unterschiedlichen Konzepten. So ist fuer jeden Geschmack etwas dabei.

### 3. Vegetarische/Vegane Optionen einplanen
Immer mehr Mitarbeitende ernaehren sich vegetarisch oder vegan. Unsere Bowl Trucks und Pocket Bowls bieten vielfaeltige Optionen.

### 4. Zeitplan abstimmen
Legt fest, wann gegessen wird. Bei einem 3-Stunden-Event reicht oft ein Truck, bei einem Ganztagesevent empfehlen wir Schichten.

### 5. Platzbedarf beachten
Ein Foodtruck braucht ca. 6m x 3m. Plant genuegend Platz fuer Schlangen und Stehtische ein.

### 6. Firmenbranding nutzen
Bei TrucksOnRoad koennt ihr eure Firma auf dem Truck-Branding integrieren – ideal fuer Teambuilding und PR-Events.

### 7. Budget realistisch kalkulieren
Rechnet mit CHF 25-45 pro Person, je nach Konzept und Zusatzwuenschen. Bei uns bekommt ihr ein transparentes Angebot ohne versteckte Kosten.""",
        "content_en": """## 7 Tips for Perfect Food Truck Catering at Corporate Events

Food trucks are the modern alternative to classic catering – and extremely popular with employees. Here are our tips from over 500 events.

### 1. Plan early
### 2. Choose the right truck combination
### 3. Include vegetarian/vegan options
### 4. Coordinate the schedule
### 5. Consider space requirements
### 6. Use company branding
### 7. Calculate budget realistically

Expect CHF 25-45 per person, depending on the concept and extras.""",
        "content_fr": """## 7 conseils pour un catering food truck parfait lors d'evenements d'entreprise

Les food trucks sont l'alternative moderne au catering classique. Voici nos conseils tires de plus de 500 evenements.

### 1. Planifiez tot
### 2. Choisissez la bonne combinaison de trucks
### 3. Incluez des options vegetariennes/veganes
### 4. Coordonnez l'horaire
### 5. Considerez l'espace necessaire
### 6. Utilisez le branding de l'entreprise
### 7. Calculez le budget de maniere realiste""",
        "content_it": """## 7 consigli per un catering food truck perfetto agli eventi aziendali

I food truck sono l'alternativa moderna al catering classico. Ecco i nostri consigli da oltre 500 eventi.

### 1. Pianificate in anticipo
### 2. Scegliete la giusta combinazione di truck
### 3. Includete opzioni vegetariane/vegane
### 4. Coordinate l'orario
### 5. Considerate lo spazio necessario
### 6. Utilizzate il branding aziendale
### 7. Calcolate il budget in modo realistico""",
        "category": "tipps",
        "image": "https://images.unsplash.com/photo-1540914124281-342587941389?w=800&q=80",
        "tags": ["Firmenanlass", "Catering", "Tipps", "Teambuilding", "Corporate"],
        "author": "TrucksOnRoad Team",
        "is_published": True,
        "created_at": "2026-02-15T10:00:00+00:00",
        "updated_at": "2026-02-15T10:00:00+00:00"
    },
    {
        "id": str(uuid.uuid4()),
        "slug": "hochzeit-foodtruck-catering",
        "title_de": "Hochzeit mit Foodtruck: So wird eure Feier unvergesslich",
        "title_en": "Wedding with Food Truck: How to Make Your Celebration Unforgettable",
        "title_fr": "Mariage avec food truck: Comment rendre votre fete inoubliable",
        "title_it": "Matrimonio con food truck: Come rendere la vostra festa indimenticabile",
        "excerpt_de": "Foodtrucks auf Hochzeiten sind der Trend 2026. Wir zeigen, warum immer mehr Paare auf Streetfood statt klassisches Bankett setzen.",
        "excerpt_en": "Food trucks at weddings are the 2026 trend. We show why more and more couples are choosing street food over classic banquets.",
        "excerpt_fr": "Les food trucks aux mariages sont la tendance 2026. Nous montrons pourquoi de plus en plus de couples choisissent le street food.",
        "excerpt_it": "I food truck ai matrimoni sono la tendenza 2026. Mostriamo perche sempre piu coppie scelgono lo street food.",
        "content_de": """## Hochzeit mit Foodtruck – Der Trend 2026

Immer mehr Brautpaare in der Schweiz entscheiden sich fuer Foodtruck-Catering statt klassischem Hochzeitsbankett. Und das aus guten Gruenden!

### Warum Foodtrucks auf Hochzeiten?

- **Lockere Atmosphaere**: Kein steifes Sitzen am Tisch – Gaeste bewegen sich frei und kommen ins Gespraech
- **Vielfalt**: Mit 2-3 Trucks bietet ihr euren Gaesten eine grosse Auswahl
- **Wow-Faktor**: Ein Retro Trailer oder eleganter Foodtruck ist ein echter Hingucker
- **Flexibilitaet**: Essen wird serviert, wann ihr es wollt – kein starrer Zeitplan

### Die beliebtesten Trucks fuer Hochzeiten

1. **Retro Trailer**: Der elegante Vintage-Look passt perfekt zu romantischen Hochzeiten
2. **Empanadas Truck**: Handgemachte Empanadas als besonderes Highlight
3. **Bowl Truck**: Frische, leichte Bowls fuer gesundheitsbewusste Paare
4. **Burger Truck**: Der Klassiker, der immer funktioniert

### Kosten und Planung

- Budget: ca. CHF 35-50 pro Person
- Frueh buchen: Beliebte Sommerdaten sind schnell vergeben
- Location pruefen: Ist genug Platz fuer den Truck vorhanden?
- Stromanschluss: Klaert das mit der Event-Location ab

### Unser Hochzeits-Tipp

Kombiniert den Empanadas Truck mit dem Retro Trailer fuer eine perfekte Mischung aus Eleganz und Street Food. Dazu ein Dessert-Angebot – und eure Gaeste werden begeistert sein!""",
        "content_en": """## Wedding with Food Truck – The 2026 Trend

More and more couples in Switzerland are choosing food truck catering over traditional wedding banquets. And for good reasons!

### Why food trucks at weddings?

- **Relaxed atmosphere**: No stiff table seating – guests move freely
- **Variety**: With 2-3 trucks, you offer your guests a wide selection
- **Wow factor**: A retro trailer or elegant food truck is a real eye-catcher
- **Flexibility**: Food is served when you want it

### Most popular trucks for weddings

1. **Retro Trailer**: Elegant vintage look
2. **Empanadas Truck**: Handmade empanadas as a special highlight
3. **Bowl Truck**: Fresh, light bowls
4. **Burger Truck**: The classic that always works""",
        "content_fr": """## Mariage avec Food Truck – La tendance 2026

De plus en plus de couples en Suisse choisissent le catering food truck au lieu du banquet de mariage traditionnel.

### Pourquoi des food trucks au mariage?
- Ambiance decontractee
- Variete avec 2-3 trucks
- Effet wow garanti
- Flexibilite totale

### Les trucks les plus populaires pour les mariages
1. **Retro Trailer**: Look vintage elegant
2. **Empanadas Truck**: Empanadas faites main
3. **Bowl Truck**: Bowls fraiches et legeres
4. **Burger Truck**: Le classique qui fonctionne toujours""",
        "content_it": """## Matrimonio con Food Truck – La tendenza 2026

Sempre piu coppie in Svizzera scelgono il catering food truck al posto del banchetto nuziale tradizionale.

### Perche food truck al matrimonio?
- Atmosfera rilassata
- Varieta con 2-3 truck
- Effetto wow garantito
- Flessibilita totale

### I truck piu popolari per i matrimoni
1. **Retro Trailer**: Look vintage elegante
2. **Empanadas Truck**: Empanadas fatte a mano
3. **Bowl Truck**: Bowl fresche e leggere
4. **Burger Truck**: Il classico che funziona sempre""",
        "category": "events",
        "image": "https://images.unsplash.com/photo-1519741497674-611481863552?w=800&q=80",
        "tags": ["Hochzeit", "Wedding", "Foodtruck", "Catering", "Trend"],
        "author": "TrucksOnRoad Team",
        "is_published": True,
        "created_at": "2026-03-01T10:00:00+00:00",
        "updated_at": "2026-03-01T10:00:00+00:00"
    },
    {
        "id": str(uuid.uuid4()),
        "slug": "foodtruck-catering-bern-basel-luzern",
        "title_de": "Foodtruck-Catering in Bern, Basel & Luzern: Schweizweit unterwegs",
        "title_en": "Food Truck Catering in Bern, Basel & Lucerne: Across Switzerland",
        "title_fr": "Catering food truck a Berne, Bale et Lucerne: Dans toute la Suisse",
        "title_it": "Catering food truck a Berna, Basilea e Lucerna: In tutta la Svizzera",
        "excerpt_de": "TrucksOnRoad ist nicht nur in Zuerich unterwegs – wir bringen unsere Foodtrucks in die ganze Schweiz. Von Bern bis Basel, von Luzern bis Genf.",
        "excerpt_en": "TrucksOnRoad isn't just in Zurich – we bring our food trucks across Switzerland. From Bern to Basel, from Lucerne to Geneva.",
        "excerpt_fr": "TrucksOnRoad n'est pas seulement a Zurich – nous apportons nos food trucks dans toute la Suisse.",
        "excerpt_it": "TrucksOnRoad non e solo a Zurigo – portiamo i nostri food truck in tutta la Svizzera.",
        "content_de": """## Foodtruck-Catering schweizweit: Von Bern bis Genf

TrucksOnRoad ist in der ganzen Schweiz unterwegs. Egal ob Firmenevent in Bern, Festival in Basel oder Hochzeit am Vierwaldstaettersee – wir sind dabei!

### Bern & Mittelland

Die Bundesstadt bietet zahlreiche Moeglichkeiten fuer Foodtruck-Events:
- **Bundesplatz**: Fuer grosse Public Events
- **Wankdorf-Areal**: Sportevents und Firmenfeiern
- **Gurten**: Das legendaere Festival-Gelaende
- **Berner Altstadt**: Strassenfeste und Maerkte

### Basel

Die Kulturhauptstadt der Schweiz liebt Street Food:
- **Rheinknie**: Open-Air-Events mit Flussblick
- **Messe Basel**: Firmenevents und Kongresse
- **Kaserne**: Kulturelle Veranstaltungen
- **St. Jakobs-Park**: Sportevents und Konzerte

### Luzern & Zentralschweiz

Die malerische Region am Vierwaldstaettersee:
- **Seeufer Luzern**: Traumhafte Event-Kulisse
- **Pilatus-Arena**: Firmenevents und Messen
- **Luzerner Fest**: Eines der groessten Stadtfeste der Schweiz

### Westschweiz: Genf, Lausanne, Fribourg

Auch in der Romandie sind wir zuhause:
- **Geneve**: Internationale Events und Firmenapereos
- **Lausanne**: Festivals und Uni-Events
- **Montreux**: Das legendaere Jazz Festival

### Unsere Logistik

- Einsatzgebiet: Ganze Schweiz
- Anfahrt: Im Angebot enthalten
- Aufbauzeit: 30-60 Minuten
- Flexibel: Indoor und Outdoor moeglich

Egal wo in der Schweiz euer Event stattfindet – TrucksOnRoad ist fuer euch unterwegs!""",
        "content_en": """## Food Truck Catering Across Switzerland: From Bern to Geneva

TrucksOnRoad operates throughout Switzerland. Whether it's a corporate event in Bern, a festival in Basel, or a wedding at Lake Lucerne – we're there!

### Bern & Central Switzerland
### Basel
### Lucerne & Central Switzerland
### Western Switzerland: Geneva, Lausanne, Fribourg

No matter where in Switzerland your event takes place – TrucksOnRoad is on the road for you!""",
        "content_fr": """## Catering food truck dans toute la Suisse: De Berne a Geneve

TrucksOnRoad est present dans toute la Suisse. Que ce soit un evenement d'entreprise a Berne, un festival a Bale ou un mariage au lac des Quatre-Cantons – nous sommes la!

### Berne & Plateau
### Bale
### Lucerne & Suisse centrale
### Suisse romande: Geneve, Lausanne, Fribourg

Peu importe ou en Suisse se deroule votre evenement – TrucksOnRoad est en route pour vous!""",
        "content_it": """## Catering food truck in tutta la Svizzera: Da Berna a Ginevra

TrucksOnRoad opera in tutta la Svizzera. Che si tratti di un evento aziendale a Berna, un festival a Basilea o un matrimonio al Lago dei Quattro Cantoni – ci siamo!

### Berna & Altopiano
### Basilea
### Lucerna & Svizzera centrale
### Svizzera romanda: Ginevra, Losanna, Friburgo

Non importa dove in Svizzera si svolge il vostro evento – TrucksOnRoad e in viaggio per voi!""",
        "category": "regionen",
        "image": "https://images.unsplash.com/photo-1527668752968-14dc70a27c95?w=800&q=80",
        "tags": ["Schweiz", "Bern", "Basel", "Luzern", "Genf", "Catering", "Foodtruck"],
        "author": "TrucksOnRoad Team",
        "is_published": True,
        "created_at": "2026-03-15T10:00:00+00:00",
        "updated_at": "2026-03-15T10:00:00+00:00"
    },
    {
        "id": str(uuid.uuid4()),
        "slug": "perfekter-smash-burger-rezept",
        "title_de": "Was macht den perfekten Smash Burger aus? Unser Geheimnis",
        "title_en": "What Makes the Perfect Smash Burger? Our Secret",
        "title_fr": "Qu'est-ce qui fait le smash burger parfait? Notre secret",
        "title_it": "Cosa rende perfetto lo smash burger? Il nostro segreto",
        "excerpt_de": "Der Smash Burger ist unser Bestseller. Hier verraten wir, was ihn so besonders macht – und warum er am besten vom Foodtruck schmeckt.",
        "excerpt_en": "The smash burger is our bestseller. Here we reveal what makes it so special – and why it tastes best from a food truck.",
        "excerpt_fr": "Le smash burger est notre best-seller. Nous revelons ce qui le rend si special.",
        "excerpt_it": "Lo smash burger e il nostro bestseller. Ecco cosa lo rende cosi speciale.",
        "content_de": """## Das Geheimnis des perfekten Smash Burgers

Bei TrucksOnRoad sind wir stolz auf unsere Smash Burger. Ueber Jahre haben wir das Rezept perfektioniert. Hier ein Blick hinter die Kulissen.

### Was ist ein Smash Burger?

Anders als ein klassischer Burger wird der Smash Burger nicht geformt, sondern als Kugel auf die heisse Grillplatte gelegt und dann mit einem Spatel plattgedrueckt ("gesmasht"). Das Ergebnis: eine knusprige, karamellisierte Kruste aussen und saftiges Fleisch innen.

### Die 5 Geheimnisse

#### 1. Das richtige Fleisch
Wir verwenden ausschliesslich Schweizer Rindfleisch mit einem Fettanteil von ca. 20%. Das Fett sorgt fuer den Geschmack und die Saftigkeit.

#### 2. Extreme Hitze
Unsere Grillplatten sind auf ueber 250 Grad erhitzt. So entsteht die legendaere Maillard-Reaktion – die Kruste wird knusprig und aromatisch.

#### 3. Der perfekte Smash
Timing ist alles. Wir smashen das Patty in den ersten 10 Sekunden und druecken dann nicht mehr nach. So bleibt der Saft im Fleisch.

#### 4. Frische Zutaten
Unser Brioche-Bun wird taeglich frisch geliefert. Tomaten, Salat und Zwiebeln kommen von regionalen Lieferanten.

#### 5. Die Sauce
Unsere Signature Sauce ist das Herzstuck. Das Rezept ist geheim – aber sie kombiniert suesse, saure und wuerzige Noten perfekt.

### Warum vom Foodtruck?

Ein Smash Burger schmeckt am besten, wenn er direkt vor euren Augen zubereitet wird. Der Duft, das Brutzeln auf der Platte, die frische Zubereitung – das ist Streetfood-Erlebnis pur.

**Probiert es selbst – bei eurem naechsten Event mit TrucksOnRoad!**""",
        "content_en": """## The Secret of the Perfect Smash Burger

At TrucksOnRoad, we're proud of our smash burgers. Over the years, we've perfected the recipe.

### What is a Smash Burger?

Unlike a classic burger, the smash burger is placed as a ball on the hot grill and pressed flat. The result: a crispy, caramelized crust outside and juicy meat inside.

### The 5 Secrets
1. **The right meat**: Swiss beef with approx. 20% fat content
2. **Extreme heat**: Our grills are heated to over 250 degrees
3. **The perfect smash**: Timing is everything
4. **Fresh ingredients**: Daily fresh buns and regional produce
5. **The sauce**: Our secret signature sauce

**Try it yourself – at your next event with TrucksOnRoad!**""",
        "content_fr": """## Le secret du smash burger parfait

Chez TrucksOnRoad, nous sommes fiers de nos smash burgers. Au fil des annees, nous avons perfectionne la recette.

### Les 5 secrets
1. La bonne viande
2. Chaleur extreme
3. Le smash parfait
4. Ingredients frais
5. La sauce signature

**Essayez-le vous-meme lors de votre prochain evenement avec TrucksOnRoad!**""",
        "content_it": """## Il segreto dello smash burger perfetto

Da TrucksOnRoad, siamo orgogliosi dei nostri smash burger. Nel corso degli anni, abbiamo perfezionato la ricetta.

### I 5 segreti
1. La carne giusta
2. Calore estremo
3. Lo smash perfetto
4. Ingredienti freschi
5. La salsa signature

**Provatelo voi stessi al vostro prossimo evento con TrucksOnRoad!**""",
        "category": "rezepte",
        "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800&q=80",
        "tags": ["Burger", "Rezept", "Smash Burger", "Streetfood", "Food"],
        "author": "TrucksOnRoad Team",
        "is_published": True,
        "created_at": "2026-03-25T10:00:00+00:00",
        "updated_at": "2026-03-25T10:00:00+00:00"
    }
]
