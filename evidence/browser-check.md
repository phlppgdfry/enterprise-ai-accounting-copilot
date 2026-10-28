# Handmatige browsercontrole

28 oktober 2026, Chrome, op een tijdelijke lokale testinstantie met synthetische gegevens. De testdatabase is na stoppen verwijderd; de demo heeft geen externe rechten of calls.

Gecontroleerd via de gebruikersinterface:

1. Lege console toont geen factuurdata zonder sleutel.
2. Reviewer ziet één te beoordelen en één geblokkeerde factuur.
3. Factuurdetail toont netto, btw, totaal, datum en leverancier.
4. Onafhankelijke reviewer keurt goed met reden; de wachtrij wordt één.
5. Export met reviewerrol wordt geweigerd met een begrijpelijke rolmelding.
6. Exporterrol draagt één factuur over naar lokale mock-ERP; wachtrij wordt nul.
7. Herhaalde export meldt nul overgedragen facturen.
8. Verbinding wissen verwijdert de sleutel en geladen werkvoorraad uit het scherm.
9. Operator dient een nieuwe factuur in via het JSON-formulier; die verschijnt als te beoordelen.
10. Visuele controle van tabel, beoordeling en statustellingen uitgevoerd.

De browserflow is werkelijk uitgevoerd; dit document is een testverslag, geen geautomatiseerde Playwright-suite. De API-invarianten worden afzonderlijk door pytest gecontroleerd. Geen claim op uitgebreid toegankelijkheids-, mobiele-device- of penetratietesten.
