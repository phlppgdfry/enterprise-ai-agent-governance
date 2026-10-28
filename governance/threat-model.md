# Dreigingsmodel

Assets: aanvraagmetadata, kennisdocumenten, beslissingen, credentials, audit events.
Trust boundaries: CLI/demo-gebruiker → agent; agent → API; API → lokale opslag.
Er zijn geen echte persoonsgegevens in fixtures.

| Dreiging | Maatregel | Bewijs / resterend risico |
|---|---|---|
| Andere medewerker leest aanvraag | API bepaalt owner uit identiteit | HTTP-test met Alice/Bob; demo-identiteiten zijn publiek |
| Agent gebruikt makerrechten | Tool stuurt medewerkeridentiteit door | Unit-test; productie vereist gedelegeerde Entra-identiteit |
| Prompt vraagt om goedkeuring | Geen decision-tool; server eist approver | Agent-handoff en HTTP-403; menselijke fixture kan lokaal worden gekozen |
| Niet-gepubliceerde bron lekt | Published + ACL vóór matching | ACL- en draft-tests; repo-assets zijn openbaar voor GitHub-lezers |
| Document bevat kwaadaardige instructies | Geen instructie-executie; beperkte acties | Deterministische demo; echte LLM heeft aparte adversarial eval nodig |
| Dubbele actie na timeout | Stabiele idempotency key per aanvraag | Hub retry-/concurrencytest |
| Externe bestemming/SSRF | Tool beperkt tot vaste loopbackbestemming | Unit-tests; geen dynamische URL uit modeloutput |
| Onbekend antwoord wordt verzonnen | Abstain of verduidelijking | Evalset; keywordmatching kan relevante vragen missen |
| Gevoelige data in logging | Geen conversatielog of telemetry in agent | Productie vereist redactie, retentie en toegangsbeheer |

De map `knowledge` simuleert restricted content. Iedereen die deze publieke repo
kan lezen ziet de bestanden; alleen antwoordselectie wordt met de rol getest.
Gebruik dit mechanisme nooit om echte geheimen in een publieke repo te beveiligen.
