# Enterprise AI Agent & Governance

**Een toetsbare agentreferentie met gepubliceerde bronnen, rolfiltering, menselijke overdracht en een bevestigde actie naar de .NET Hub.**

Fictieve klant: Noordwerk. Dit is een deterministische Python-simulator en een
Copilot Studio-bouwspecificatie. Er wordt geen LLM aangeroepen. Testresultaten
zeggen iets over regels en regressies, niet over de kwaliteit van een echte AI-agent.

## Proberen

Python 3.11+, geen externe packages.

```bash
make verify
python3 agent.py ask 'Wat is het onkostenbeleid?'
python3 agent.py ask 'Wat is het salaris van Jan?'
python3 agent.py ask 'Keur deze aanvraag goed'
python3 agent.py ask 'escalatie' --role approver
```

De eerste vraag geeft een antwoord met een lokaal bronpad. Persoonlijke dossiers
worden geweigerd, beslissingen naar een mens overgedragen. Onbekende onderwerpen
geven geen verzonnen antwoord. Alleen gepubliceerde bronnen met de passende rol
worden vóór het zoeken geselecteerd.

## Werkende integratie

Start eerst de [Hub](https://github.com/phlppgdfry/enterprise-ai-automation-hub)
op `127.0.0.1:5088`. Dien vervolgens expliciet een aanvraag in:

```bash
python3 agent.py submit --title 'Werkmateriaal' --category materials --amount 75 --key interview-demo-01 --confirm
```

Herhaal dezelfde opdracht met dezelfde key: hetzelfde ID. Zonder `--confirm`
wordt geen netwerkverzoek gedaan. De tool kan alleen een lokale medewerkeridentiteit
doorgeven en heeft geen besluitfunctie. De API bepaalt eigenaar en rechten.
Maak voor een nieuwe aanvraag een nieuwe key.

## Bewijs voor de consultantrol

| Onderwerp | Artefact |
|---|---|
| Agentontwerp en grenzen | [Ontwerp en Copilot-instructies](copilot-studio/build-guide.md) |
| Bronkwaliteit en autorisaties | [Kennisbronnen](knowledge/policies.json), ACL-tests |
| Evaluaties | [30 scenario's](eval/cases.json), `python3 agent.py evaluate` |
| Security en governance | [Threat model](governance/threat-model.md), [releasebeleid](governance/release-policy.md) |
| Levenscyclus en overdracht | [Copilot-bouwgids](copilot-studio/build-guide.md), CI en [bewijsmatrix](EVIDENCE.md) |

## Wat de veiligheid niet bewijst

De CLI-rol is een testfixture, geen login. Regexregels vangen slechts enkele
instructieaanvallen af; ze zijn geen volledige prompt-injectionbescherming. Een
echt model kan deze regels niet als beveiligingsgrens gebruiken. Serverrechten,
beperkte tools en een menselijke beslissing blijven noodzakelijk. Bronbestanden
zijn vertrouwde repository-assets; er is geen upload van externe documenten.

De testset bevat Nederlandse en eenvoudige Engelse voorbeelden, geen volledige
meertaligheidstest. Spelfouten, synoniemen en samengestelde vragen zijn beperkt.
Er is geen echte Copilot Studio-evaluatie of tenantdeployment van deze case.

Samenhang: [Hub](https://github.com/phlppgdfry/enterprise-ai-automation-hub) ·
[Consulting Playbook](https://github.com/phlppgdfry/ai-transformation-consulting-playbook)
· [MIT](LICENSE)
