# Runbook

## Gezonde toestand

`GET /health` geeft `ok` en maakt expliciet dat de ERP lokaal is. Deze livenessroute test geen Azure-bereikbaarheid. `GET /metrics` met een API key toont statusaantallen en pending exports van de eigen tenant. Swagger en OpenAPI zijn publiek in deze lokale demo; beperk dat bij deployment.

## Storingen

| Signaal | Diagnose | Actie |
|---|---|---|
| 401 | Geen key / key niet in huidige procesconfiguratie | Controleer rolkey in .env, herstart server na wijziging; log geen key |
| 403 | Verkeerde rol | Kies identiteit die bij handeling hoort; verhoog privileges niet willekeurig |
| 409 op submit | Idempotency key of leverancier/nummer bestaat | Lees bestaande factuur; nieuw key met gewijzigde body mag geen duplicate business key omzeilen |
| 409 op review | Eigen factuur / stale versie / reeds beslist / blokkade | Herlaad detail, controleer bron en rol; blokkerende signalen hebben geen override |
| Pending exports groeit | Worker niet aangeroepen of lokale writefout | Controleer volume/rechten en run `/exports/run` als exporter; herhaal veilig |
| Azure 502 | Providerconfiguratie, identiteit, schema of netwerk | Controleer resource/deployment, quota en gesaniteerde Azure-traces; behoud menselijke workflow |
| Database locked | Langdurige writer of te veel concurrency | Stop overtollige processen; geen locks verwijderen; schaal niet met meerdere replicas op dit bestand |

## Back-up en herstel

Gebruik SQLite's backup-API voor een consistente kopie. Voor de lokale demo:

```python
import sqlite3
from pathlib import Path

Path("data/backups").mkdir(parents=True, exist_ok=True)
with sqlite3.connect("data/accounting.sqlite3") as source:
    with sqlite3.connect("data/backups/accounting.sqlite3") as target:
        source.backup(target)
```

Bewaar een back-up buiten de applicatiedisk en beveilig die zoals de brondatabase. Test herstel in een aparte directory: stop alle processen, zet een kopie terug, start met `ACCOUNTING_DB` naar die kopie en vergelijk factuur-/outboxaantallen. Exporteer geen goedgekeurde records opnieuw naar een echte ERP zonder reconciliatie van de stabiele idempotency keys. Voor dit prototype is er alleen een lokale mock, dus externe reconciliatie is nog niet geïmplementeerd.

## Voor een echte pilot

1. Business owner kiest één proces, leveranciergroep en successcriteria; geen automatische betalingen.
2. Entra ID, HTTPS/gateway, requestlimieten, rate limiting, secretbeheer, netwerkafscherming en rolbeheer laten toetsen.
3. PostgreSQL/migraties en hersteltest; per-tenant datatoegang en back-upretentie vastleggen.
4. Echte ERP-adapter met sandbox, idempotencycontract, retry/backoff, dead letters en reconciliation bouwen.
5. Synthetische PDF-goldset labelen; Azure-extractie/LLM met echte deployment evalueren; kosten en latency meten.
6. Correctie/revisieproces, beheerde leveranciersstamgegevens en extra goedkeuring voor hoge bedragen ontwerpen.
7. Audit export, telemetry, alarmering en documentretentie implementeren; privacy/security en accountant laten beoordelen.
8. Beperkte gebruikerspilot met opleiding, feedback en rollback naar bestaand proces. Pas daarna scope uitbreiden.

## Rollback

Zet `ACCOUNTING_AI_MODE=disabled` en herstart om AI-routes te stoppen. De kernworkflow blijft handmatig met JSON invoer werken. Zet review/exportverkeer stil wanneer de integriteit twijfelachtig is. Een rollback van code maakt geboekte financiële acties niet ongedaan; dat vereist een gecontroleerd bedrijfsproces. Dit prototype heeft geen betaling of remote boeking.
