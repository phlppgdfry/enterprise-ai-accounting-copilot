# Verificatie

Op 28 oktober 2026 opnieuw uitgevoerd met Python 3.13: **29 tests geslaagd** in `tests.xml`, Ruff zonder fouten. De CLI-demo doorloopt de API met een tijdelijke database; `demo.json` bevat de werkelijke synthetische uitvoer.

De Docker-image is gebouwd. De geïnstalleerde package bevat de console en geeft health=200, beschermd=401 en console=200 in `container-smoke.txt`. De standaard Uvicorn-CMD is in een tijdelijke container gestart en `/health` gaf 200, zie `container-runtime.txt`.

De [browsercontrole](browser-check.md) testte factuurindiening, onafhankelijke goedkeuring, rolweigering, export en een lege retry. Azure is uitsluitend met HTTP-contractfixtures getest. Geen echte ERP, providerkwaliteit, clouddeployment of GDPR-conformiteit geclaimd.
