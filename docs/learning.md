# Leerboek en eigenaarschapstoets

## Wat je moet kunnen uitleggen

Een LLM geeft een waarschijnlijk voorstel; een factuurgoedkeuring is een bedrijfsbeslissing. Het onderscheid zit hier in de API-grens: classificatie heeft geen referentie naar de store en kan geen status wijzigen. Een JSON-schema garandeert de vorm; een reviewer controleert de feiten aan de bron. Een key bepaalt de Principal; de client kiest geen tenant of rol.

`Decimal` voorkomt dat EUR 0,10 + EUR 0,20 door binaire floats subtiel afwijkt. De schema's beperken decimalen en controleren exact of net + btw = totaal. Dat bewijst geen fiscale juistheid van de toegepaste btw. De boekhoudkundige beoordeling blijft buiten deze technische controle.

Een idempotency key herkent een herhaald verzoek; een unieke leverancier/nummer-combinatie herkent hetzelfde bedrijfsdocument onder een nieuwe key. Je hebt beide nodig. De payloadhash voorkomt dat een key een gewijzigde body onzichtbaar vervangt. Een reviewversie voorkomt dat iemand een verouderd scherm goedkeurt.

De outbox wordt samen met approval opgeslagen. Zo bestaat er geen goedgekeurde factuur zonder exportopdracht. Een remote ERP kan toch ontvangen hebben terwijl de client een timeout zag. Daar heb je een externe idempotency key en reconciliatie voor nodig; de lokale mock maakt dit niet automatisch waar in het echt.

## Oefeningen, zelf uitvoeren

1. Run de demo en teken alle databasewrites zonder de code te bekijken. Leg uit op welk punt rollback mogelijk is.
2. Dien `examples/invoice.json` tweemaal met dezelfde key in. Verander dan de omschrijving en gebruik dezelfde key. Verklaar 201, 200 en 409.
3. Gebruik een nieuwe key voor hetzelfde leverancier/factuurnummer. Verklaar waarom dat toch 409 is.
4. Keur met dezelfde actor onder een reviewerkey goed. Toon de vier-ogencontrole en leg uit waarom verschillende keys alleen onvoldoende zijn.
5. Laat de exporter één keer falen via `Store.export_mock(..., fail=True)` in een eigen test. Herstart Store en herstel zonder dubbele boeking.
6. Voeg een regel voor te oude documenten toe met een door business gekozen grens. Schrijf een grensgevaltest en leg uit waarom een wettelijke bewaartermijn daar niet automatisch uit volgt.
7. Voeg een nieuwe categorie toe aan de enum. Onderzoek welke schema-, prompt- en evalwijzigingen nodig zijn. Pas geen productieprompt aan zonder regressie-evidence.
8. Vervang de mock in een ontwerp door een ERP HTTP-call. Teken de crash na ontvangst maar vóór acknowledgement en ontwerp reconciliation.
9. Diagnoseer een 404 met een andere tenant. Toon dat dit geen bewijs van ontbrekend record is.
10. Beoordeel de Azure-contracttests: welke claims kun je ermee verdedigen en welke heb je nog niet getest?

## Korte demo voor een gesprek

0:00 — leg het fictieve procesprobleem en de synthetische scope uit. 0:20 — submit en duplicate tonen. 0:45 — een onbekende leverancier blokkeren. 1:05 — rolgrens en onafhankelijke approval. 1:25 — export en lege retry. 1:45 — audit, testbewijs en één concrete beperking. Presenteer geen mock als echte ERP of Azure OCR als live getest wanneer dat nog niet zo is.

## Zelfbeoordeling

Noteer per oefening datum, eigen antwoord, gemaakte wijziging, mislukking en herstel. Niveau 1: kunnen volgen; niveau 2: zonder hulp uitleggen; niveau 3: zelfstandig aanpassen en testen; niveau 4: storingen diagnosticeren en afwegingen verdedigen. Laat iemand anders het scenario wijzigen. Een gegenereerde repo wordt pas geloofwaardig bewijs wanneer jij dat zelfstandig kunt.
