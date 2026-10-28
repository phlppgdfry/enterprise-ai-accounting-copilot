# Beveiliging, risico's en gegevensbescherming

Alle meegeleverde data is fictief. De applicatie verwerkt geen echte rekeningnummers, persoonsgegevens of betalingen. Dit ontwerp ondersteunt bespreking van controles; het is geen verklaring van GDPR- of AI Act-conformiteit.

| Dreiging | Aanwezige controle | Resterend risico / pilotactie |
|---|---|---|
| Client vervalst rol of tenant | API key koppelt server-side aan Principal; payload heeft geen autorisatievelden | API keys vervangen door Entra ID met issuer/audience/signaturevalidatie en centrale lifecycle |
| Data van ander dossier bekijken | Tenant op elke query, ook audit/export/metrics | Databasetoegang heeft alle tenants; overweeg RLS en onafhankelijke penetratietest |
| Medewerker keurt eigen factuur goed | Vergelijking stabiele actor bij review | Beheerder kan sleutels verkeerd toewijzen; identity governance en access reviews nodig |
| Dubbele boeking door retry | Idempotency key + payloadhash + business key + unieke outbox/ERP-id | Externe ERP moet een idempotencycontract hebben |
| Prompt injection in document | Model alleen categorievoorstel; geen review/exporttools | Inhoud kan nog verkeerd zijn; menselijke broncontrole en gerichte adversarial evals |
| Credentiallek via polling | Zelfde origin, redirects uit, gesaniteerde providerfout | Gecompromitteerde geconfigureerde endpoint/host blijft risico; egress allowlist nodig |
| Manipulatie na besluit | API laat geen update van goedgekeurde data toe; audit bij statuswijziging | Audit is niet tamperproof; export naar afgeschermde opslag/SIEM |
| Kwaadaardige PDF / te grote request | Prefix- en 5 MiB-check in adapter | Body al ingelezen; gatewaylimiet, malware-scan en parserisolatie vóór productie |
| Onbedoelde datalek via validatiefout | 422-responses bevatten alleen veldlocatie en fouttype | Gebruikers kunnen gevoelige gegevens in reden/omschrijving zetten; logging- en retentiebeleid nodig |
| Secrets in Git/image | .env genegeerd, .dockerignore, geen echte sleutels in voorbeelden | Secret scanning aanzetten, sleutelrotatie oefenen; lokale .env is plaintext |

## Datastroom en eigenaarschap

Factuur-JSON → SQLite op lokale disk. Approvalreden → audit. Exportpayload → lokale mocktabel. PDF-bytes worden bij opt-in naar de geconfigureerde Azure DI gestuurd; classificatietekst naar Azure OpenAI. Geen PDF-bestanden worden door dit prototype opgeslagen. Azure-providerverwerking/retentie en regio hangen van jouw resourceconfiguratie en contract af.

Voor een echte pilot bepaalt de verwerkingsverantwoordelijke het doel, de rechtsgrond, noodzakelijke velden, toegangsrollen, verwerkersafspraken, bewaartermijnen en een eventuele DPIA met privacy/securityverantwoordelijken. Stel een gegevensregister op; dat kan niet door een README automatisch worden opgelost. Voeg verwijdering, exportverzoeken en back-upretentie toe en test deze. Er is nog geen automatische retentietaak.

## Incidentoefening

Bij vermoeden van lek: stop de API/worker, revoke betrokken credentials en isoleer de volume. Bewaar gesaniteerde tijdlijn, relevante outbox-id's en audit-events. Raadpleeg je eigen incidentprocedure voor melding en beoordeling. Maak geen willekeurige exports met klantgegevens voor debugging. Herstart pas na herstel en dubbele-boekingsreconciliatie.
