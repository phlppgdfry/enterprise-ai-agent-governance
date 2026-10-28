# Bewijsmatrix

Validatiedatum: 28 oktober 2026. Lokale deterministische referentie, geen LLM-run.

| Claim | Reproduceerbaar bewijs | Grens |
|---|---|---|
| Antwoord gebruikt een gepubliceerde bron | `agent.py ask`, bronpaden en contentchecks | Keywordmatching, geen semantische RAG |
| Rolfilter gaat vóór retrieval | Employee/approver-test en drafttest | CLI-rol is geen login; publieke repo bevat alle fixtures |
| 30 ontwerpvragen passen bij de regels | `python3 agent.py evaluate --summary` | Geen onafhankelijke holdout en geen Copilot-score |
| Actie vraagt bevestiging | Unit-test controleert dat netwerk niet wordt aangeroepen zonder bevestiging | Geen volledige conversatie-engine |
| Tool gebruikt medewerkeridentiteit | Header-/key-test, vaste loopbackbestemming | Publieke demo-identiteit, geen Entra-token |
| Echte koppeling naar .NET | `python3 scripts/verify_hub.py` met sibling Hub | Geen cloudconnector |
| Governance is overdraagbaar | Threat model, releasegate en bouwgids | Geen toegepaste DLP-policy of compliancecertificaat |

`make verify` draait 9 unit-tests, de 30-case-evaluatie en documentchecks.
Het optionele stackscript start een echte geïsoleerde .NET-API, dient via de
agenttool in, controleert retry en eigenaarsisolatie en laat de menselijke
demo-identiteit beslissen. Daarvoor moet de sibling Hub eerst in Release zijn gebouwd.

De evalset is ontwerp- en regressiemateriaal, niet onafhankelijk onderzoek naar
modelkwaliteit. Dezelfde bronwoorden komen in implementatie en vragen terug.
Een echte release vereist onbekende parafrases en adversarial tests in de tenant.
