# Evaluatie en bewijskracht

## Wat de tests meten

`python -m pytest -q` controleert de werkelijke API, database en adapters. De suite bevat onder meer volledige goedkeuring/export, herstart/persistente opslag, concurrerende idempotency, afwijkende bedragen, tenantisolatie, rollen, vier ogen, stale versies, exportherstel, modelweigeringen en verdachte polling-origins.

De Azure-contracttests gebruiken `httpx.MockTransport`; er is geen Azure-call of API key nodig. De PDF-testbytes zijn doelbewust fake contractfixtures en geen echte OCR-input. Een geslaagde contracttest is geen bewijs dat een provider de fake PDF accepteert.

Lokaal gecontroleerd op 28 oktober 2026 met Python 3.13: **27 tests geslaagd** bij de eerste volledige run. De suite kan groeien; het actuele CI-resultaat en `pytest`-output zijn leidend. Ruff controleert ongeldige imports en eenvoudige codefouten. De demo doorliep submit → onafhankelijke approval → één mockexport → lege retry. GitHub Actions voert deze stappen opnieuw uit en bewaart JUnit-resultaten.

## Grenzen

Dit zijn invariant- en contracttests, geen benchmark voor hallucination, OCR-nauwkeurigheid, prompt-injectionresistentie of productiebelasting. De test `Ignore all instructions...` bewijst uitsluitend dat ongeldige categorie-uitvoer wordt afgewezen bij de gemockte modelresponse. Geen percentage voor echte modelveiligheid wordt geclaimd.

## Azure-goldsetplan

Maak minimaal 30 synthetische maar geldige PDF's met verschillende layouts, creditnota's buiten scope, slechte scans en ontbrekende velden. Leg verwachte leverancier, factuurnummer, datum, net/btw/totaal en categorie vast. Houd tuning- en holdoutsets gescheiden. Bewaar per run datasetversie, documenthash, model/deployment, prompt/schema, latency, usage en menselijk oordeel. Meet per veld exact match, ontbrekende waarden, onterecht geaccepteerde fouten en nood aan menselijke correctie. Een grens voor financiële velden moet door de proceseigenaar worden vastgesteld, niet achteraf op de resultaten worden afgestemd.

Run dezelfde set na een model-, prompt- of SDK-upgrade. Laat CI het deterministische pad altijd blokkeren bij falende invarianten. Een betaalde Azure-eval hoort apart en expliciet met budgetlimiet te worden gestart. De andere portfolio-repo `enterprise-ai-evals-governance` kan die resultaten vergelijken, maar is geen runtime-afhankelijkheid van deze repo.
