# Optionele Azure-integraties

Gecontroleerde documentatie op 28 oktober 2026 via Context7:

- [Document Intelligence REST quickstart](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/quickstarts/get-started-sdks-rest-api)
- [Azure OpenAI structured outputs](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/structured-outputs)
- [Azure OpenAI chat REST](https://learn.microsoft.com/en-us/rest/api/microsoft-foundry/azureopenai/chat)

## Instellen

Maak resources en deployment expliciet in je eigen Azure-subscriptie. Dit project maakt geen resources aan en vraagt geen bestaande tokens op. Controleer regio, modelondersteuning voor structured outputs, quota, netwerktoegang, dataverwerking en kosten vóór je een pilot draait.

Zet in de genegeerde `.env`:

```dotenv
ACCOUNTING_AI_MODE=azure
AZURE_DOCUMENT_ENDPOINT=https://RESOURCE.cognitiveservices.azure.com
AZURE_OPENAI_ENDPOINT=https://RESOURCE.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=YOUR_DEPLOYMENT_NAME
```

Gebruik resource-roots zonder `/documentintelligence` of `/openai/v1`-suffix. Zonder optionele `AZURE_DOCUMENT_KEY`/`AZURE_OPENAI_KEY` gebruikt de adapter `DefaultAzureCredential`, met interactieve browser-login uitgeschakeld. In Azure hoort daar een toegewezen managed identity met passende data-plane rollen bij. Lokaal kan een door jou aangemelde Azure CLI-identiteit gebruikt worden. Niet alle netwerken/rollen zijn vanuit deze machine geverifieerd. Keys zijn alleen een expliciete lokale ontwikkeloptie; commit ze nooit.

## PDF-extractie

`POST /documents/extract` verwacht ruwe PDF-bytes met `Content-Type: application/pdf`. De adapter accepteert maximaal 5 MiB en controleert de `%PDF-`prefix; dat is geen malwaredetectie of volledige PDF-validatie. Een reverse proxy moet de requestbody begrenzen vóór de applicatie hem inleest.

REST-pad: `POST /documentintelligence/documentModels/prebuilt-invoice:analyze?api-version=2024-11-30`, gevolgd door polling op `Operation-Location`. De adapter accepteert alleen dezelfde HTTPS-origin voor polling, zodat credentials niet naar een andere host gaan. Hij volgt geen redirects. Polling is begrensd tot 30 requests met 1 seconde pauze; elke HTTP-call heeft een timeout van 30 seconden. Dit is geen totale 30-seconden deadline. Timeout betekent mogelijk dat de provideranalyse nog doorloopt; ondoordacht opnieuw posten kan opnieuw kosten veroorzaken.

De response bevat geëxtraheerde velden en confidences. Een medewerker controleert bedrag/datum/factuurnummer en koppelt de interne leverancier, en dient daarna expliciet `POST /invoices` in. Het systeem vertrouwt de OCR-leveranciersnaam niet als autorisatiebron. Er is geen automatische OCR-naar-boekingsketen.

## Modelclassificatie

`POST /ai/classify` met `{"description":"Synthetische kantoormaterialen"}` gebruikt `/openai/v1/chat/completions`. Het deployment moet structured outputs ondersteunen. Het model kiest uitsluitend `office`, `software`, `travel` of `other`, met korte toelichting. De API valideert ook de ontvangen JSON met Pydantic en wijst extra velden af. Weigering, ongeldige JSON of netwerkfout wordt 502; er volgt geen actie.

De response geeft de door Azure gerapporteerde tokenusage terug, maar schrijft die nog niet naar een centrale kostentabel. `GET /metrics` claimt daarom geen gemeten modelkosten. Voeg prijsconfiguratie per deployment, usage-ledger en spend-limieten toe voor een betaalde pilot. Proef niet met echte klantfacturen zonder afzonderlijk goedgekeurde gegevensafspraken.

## Acceptatiebewijs dat nog ontbreekt

Bewaar een gesaniteerd bewijs van endpoint/configuratie, deploymentversie, resource-regio, netwerkpad, tokenusage, latency, extractieresultaten tegenover handmatig gelabelde synthetische PDF's en foutscenario's (429/503/timeout). Laat een collega autorisaties en vier-ogenwerking testen. Contracttests bewijzen HTTP-vorm en foutafhandeling; ze bewijzen geen OCR-nauwkeurigheid of werking in jouw tenant.
