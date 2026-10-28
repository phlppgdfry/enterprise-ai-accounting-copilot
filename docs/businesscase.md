# Businesscase en adoptie

## Probleem en gewenste verbetering

Een fictief accountancyteam typt factuurgegevens over en zoekt ontbrekende leveranciergegevens op. Een medewerker blijft eindverantwoordelijk voor de beoordeling. Het project toont hoe deterministische controles en een reviewqueue voorbereidend werk kunnen verminderen. Er zijn geen echte Titeca-processen onderzocht en geen klantresultaten gemeten.

## Huidig en voorgesteld proces

Huidig: document ontvangen → gegevens overtypen → bron controleren → goedkeuring vragen → ERP overnemen.

Voorgesteld: document ontvangen → optionele extractie → medewerker bevestigt velden/leverancier → regels blokkeren afwijkingen → onafhankelijke review → outbox → integratie → reconciliatie. In deze uitvoering is ontvangst handmatig, extractie optioneel en integratie een lokale mock.

## Rekenvoorbeeld, geen gerealiseerde besparing

Aannames: 1.000 facturen/maand, 8 minuten voorbereiding per factuur, met de oplossing 5 minuten inclusief correcties, EUR 45 per uur geladen personeelskost. Potentiële bruto tijdwinst = 1.000 × 3 / 60 = 50 uur/maand, of EUR 2.250. Trek model/OCR-kosten, platform, onderhoud, opleiding en extra kwaliteitscontrole af. Bij EUR 500 operationele kosten is het rekenvoorbeeld EUR 1.750 netto/maand. Bij 2 minuten correctie bovenop de 5 resteert slechts EUR 250 netto/maand. Geen aanname is gevalideerd.

Voer een tijdmeting uit op vergelijkbare documenten vóór/na, inclusief afgewezen items, wachttijd en uitzonderingen. Verwar touch time niet met doorlooptijd. Automatiseer geen fout die door meer rework duurder wordt.

## KPI's

| KPI | Definitie | Huidig meetbaar? |
|---|---|---|
| Pending review/export | Aantal records per status | Ja via /metrics |
| Dubbele mockboekingen | Meerdere mockboekingen voor één factuur | Unieke constraint + regressietest |
| Touch time | Actieve behandeltijd per factuur | Nee, gebruikersstudie nodig |
| Extractie-accuratesse | Correcte velden / gelabelde velden | Nee, echte Azure-goldset-run nodig |
| Correctie-/afwijzingspercentage | Gevalideerde wijzigingen / alle voorstellen | Afwijzingsaantallen aanwezig; wijzigingsproces ontbreekt |
| Kosten per document | OCR + model + platform / documenten | Tokenusage response aanwezig; financieel ledger ontbreekt |

## Adoptieplan

Proceseigenaar: accountant/teamlead. Integratie-eigenaar: IT. Data/privacy-eigenaar: bevoegde organisatiefunctionaris. Pilotgebruikers: twee operators en één onafhankelijke reviewer. Start met uitsluitend synthetische data, laat gebruikers fouten zoeken, oefen correctie buiten dit prototype en bespreek wanneer de bron voorgaat op het model. Houd een wekelijkse feedbacksessie en spreek een stopcriterium af bij onverklaarde verschillen of privacyproblemen.

Train niet alleen de knoppen: toon een foutief modelantwoord, een duplicaat, een onbekende leverancier en een uitgestelde export. Meet of medewerkers de juiste bron controleren en afwijkingen herkennen. Go/no-go is een gezamenlijke beslissing van business, IT, security/privacy; de maker keurt zichzelf niet goed.
