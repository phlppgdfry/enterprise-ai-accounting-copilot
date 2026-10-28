# Accounting Review Copilot

Een uitvoerbare portfolio-case voor een fictief Belgisch accountancykantoor: factuurgegevens controleren, een onafhankelijke medewerker laten beslissen en een goedgekeurde factuur via een persistente outbox naar een **lokale mock-ERP** overbrengen.

**Status:** lokaal geteste referentie-implementatie met uitsluitend synthetische gegevens. Azure-adapters zijn met gemockte HTTP-contracttests gecontroleerd; een echte Azure-resource, OCR-kwaliteit en Microsoft-tenant zijn nog niet gevalideerd. Geen productie- of GDPR-certificering, geen betalingen, geen koppeling met Titeca.

## Binnen drie minuten draaien

Python 3.11+; lokaal getest met Python 3.13. Gebruik een eigen virtualenv.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install --no-deps -e .
.venv/bin/python -m accounting_copilot.demo
.venv/bin/python -m pytest -q
```

De demo doorloopt de REST-interface, gebruikt een tijdelijke database, toont audit-events en bewijst dat een tweede export geen tweede boeking maakt. Er is geen account of model nodig voor deze deterministische workflowdemo. AI/OCR worden daarbij niet nagebootst als echte modelresultaten.

Voor een blijvende lokale API:

```bash
.venv/bin/python -m accounting_copilot.bootstrap
.venv/bin/uvicorn accounting_copilot.api:app --env-file .env --host 127.0.0.1 --port 8000
```

Open de [factuurwerkbank](http://127.0.0.1:8000/console) voor facturen, statustellingen, menselijke beoordeling, audit en mockexport. Wissel in het scherm naar de sleutel van de vereiste rol uit de gegenereerde `.env`; de server controleert alle rechten. De sleutel blijft alleen in het schermgeheugen en wordt bij vernieuwen of wissen verwijderd. Je kunt ook [Swagger](http://127.0.0.1:8000/docs) gebruiken. De vier sleutels horen bij afzonderlijke operator-, reviewer-, exporter- en auditor-identiteiten. De API start zonder sleutels met alleen publieke health/docs/lege console; beschermde routes geven 401. Bootstrap overschrijft nooit een bestaande `.env`.

## Wat werkt

- Exacte `Decimal`-bedragen, EUR-only, schema-validatie en sluitende net + btw = totaal-controle.
- Goedgekeurde synthetische leveranciers, blokkering van onbekende leveranciers, toekomstige datum en hoge bedragen.
- Persistente idempotency-sleutels én unieke leverancier/factuurnummer-combinaties, ook bij gelijktijdige verzoeken.
- Rollen uit serverconfiguratie, tenantfilters, vier-ogencontrole en versiecontrole bij beslissingen.
- Goedkeuring en outbox in één SQLite-transactie. Een lokale mock-ERP verwerkt idempotent; fouten blijven retrybaar.
- Audittrail en procesaantallen per tenant. Dit is geen onveranderbare auditopslag; een databasebeheerder kan wijzigen.
- Optioneel echte Azure Document Intelligence-extractie en Azure OpenAI-categorisatie. Uitvoer blijft een voorstel.

## API-routekaart

| Route | Rol | Gedrag |
|---|---|---|
| `POST /invoices` | operator | Valideer en sla op; header `Idempotency-Key` verplicht |
| `GET /invoices` | iedere ingelogde rol | Laatste maximaal 100 facturen van eigen tenant |
| `GET /invoices/{id}` | iedere ingelogde rol | Detail; andere tenant krijgt 404 |
| `POST /invoices/{id}/decision` | reviewer | Approve/reject met reden en `expected_version` |
| `POST /exports/run` | exporter | Verwerk maximaal 100 pending outbox-items naar lokale mock |
| `GET /invoices/{id}/audit` | reviewer/auditor | Audit-events van deze factuur |
| `GET /metrics` | iedere ingelogde rol | Statusaantallen en pending exports |
| `POST /documents/extract` | operator | Optionele Azure-extractie van PDF-bytes |
| `POST /ai/classify` | operator | Optioneel gestructureerd categorievoorstel |

Een voorbeeldfactuur staat in [examples/invoice.json](examples/invoice.json). Alle bedragen zijn strings om binaire floating-pointafronding bij invoer te vermijden. Een beslissing is bijvoorbeeld `{"approve":true,"reason":"Bron en bedragen gecontroleerd","expected_version":1}`. Bekijk het gegenereerde [OpenAPI-contract](docs/openapi.json).

## Azure activeren

Zie [Azure-integratie](docs/azure.md). Zonder `ACCOUNTING_AI_MODE=azure` geven AI-routes expliciet 503. Configuratiefouten, timeouts, modelweigeringen en ongeldige uitvoer geven een afgeschermde fout; er is geen stilzwijgende fallback naar verzonnen resultaten. AI mag nooit zelf goedkeuren of exporteren.

## Docker

Voer eerst de lokale bootstrap uit zodat `.env` en de synthetische leveranciersdatabase bestaan. Daarna `docker compose up --build`. De poort bindt aan loopback, de container draait als niet-root, met alleen de datamap schrijfbaar. Op Linux moet de gemounte datamap schrijfbaar zijn voor uid 10001; gebruik een passende volume-eigenaar. Docker-build/runtime is niet lokaal geverifieerd wanneer de daemon ontbreekt.

## Bewijs en leren

- [Architectuur en beslissingen](docs/architecture.md)
- [Beveiliging en gegevensbescherming](docs/security.md)
- [Runbook en storingsherstel](docs/runbook.md)
- [Businesscase en adoptie](docs/businesscase.md)
- [Evaluatieplan en echte testresultaten](docs/evaluation.md)
- [Zelf oefenen en eigenaarschap aantonen](docs/learning.md)

Geschreven met AI-ondersteuning. Een kandidaat kan dit project pas als eigen vaardigheid presenteren nadat die de scenario's in het leerboek zelf kan uitleggen, aanpassen en diagnosticeren. De code bewijst projectgedrag; ze bewijst geen professionele implementatie-ervaring.

## Grenzen

SQLite, API keys en een lokale mock zijn bewust klein gehouden. Er zijn nog geen Entra ID-validatie, echte ERP, mailbox/SharePoint-ingest, vectorzoekmachine, malware-scanner, PostgreSQL-migratie, automatische documentretentie of betaalde modelkwaliteitsmeting. Geblokkeerde documenten kunnen worden afgewezen; correcties met hetzelfde factuurnummer en wijzigbare leverancierstamgegevens hebben nog geen UI/API. Bewaar broncorrecties buiten dit prototype; wijzig geen reeds goedgekeurde factuur. [Productievoorwaarden](docs/runbook.md#voor-een-echte-pilot) maken die resterende stappen concreet.
