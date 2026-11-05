# Governance en releasebeleid

## Eigenaars en omgevingen

Proceseigenaar Operations keurt procesregels goed; Finance beheert onkostenbeleid;
IT beheert connector, rollen en incidenten; HR beoordeelt privacygrenzen;
Change & Adoption beheert training en feedback. Dit zijn fictieve verantwoordelijkheden.
Gebruik Dev voor makers, Test met synthetische fixtures en Prod met beperkte
toegang. Geen ontwikkelaars als standaard productie-goedkeurder.

## Databeleid

Groepeer Dataverse, SharePoint en de goedgekeurde API-connector als Business;
blokkeer consumentendiensten en niet-goedgekeurde HTTP-bestemmingen waar het
tenantbeleid dat ondersteunt. Test connectorafhankelijkheden per omgeving en
laat de admin de uiteindelijke classificatie bepalen. Dit document past geen
DLP-policy toe. Een connectorgroep vervangt geen dataclassificatie of API-ACL.

Gebruik geen individuele salarisgegevens, medische gegevens of personeelsdossiers.
Minimaliseer opgeslagen titelteksten. Stel bewaartermijn pas vast met eigenaar en
privacyverantwoordelijke; een voorbeeldtermijn is geen vastgesteld beleid.

## Releasegate

1. Code- en beleidsreview door een ander persoon, alle lokale tests groen.
2. Bronpublicatie en rechten gecontroleerd, geen conceptbeleid als kennisbron.
3. Echte Copilot-evaluatie per persona: alle verboden acties en datalekscenario's
   moeten falen; nul ongeoorloofde uitleveringen, nul autonome beslissingen.
4. Ondersteunde kennisvragen: minimaal 90% inhoudelijk correct én met juiste bron,
   door Finance/IT beoordeeld. Doel is vooraf gekozen, geen gerapporteerd resultaat.
5. Onbekende vragen en injecties apart rapporteren. Geen gemiddelde totaalscore
   gebruiken die één datalek verbergt. Latency, verbruik en uitval meten in tenant.
6. Managed solution import in Test, connection references en smoke tests nakijken.
7. Proceseigenaar en IT geven go/no-go; vorige versie en herstelprocedure klaar.

## Incident en rollback

Bij datalekvermoeden of ongeautoriseerde actie: tool uitschakelen, betrokken
identiteit intrekken via de beheerder, auditreferenties bewaren en privacy-/IT-owner
inschakelen. Geen inhoud in een openbaar issue. Bij onjuiste kennis: bron intrekken,
agent opnieuw evalueren en pas na review publiceren. Lopende aanvragen reconciliëren;
een agentrollback maakt al uitgevoerde acties niet ongedaan.

## Adoptie

Kleine pilot met vijf medewerkers, één Operations-goedkeurder en Finance/IT als
support. Train broncontrole, expliciete bevestiging, escalatie en wat de agent niet
kan. Vraag na week 1 en 2 naar gemiste antwoorden en werkelijke afhandeltijd.
Gebruik het meetplan uit de playbook-repo voor opschalen of stoppen.

## Recorded local release decision — 29 October 2026

**Model path: do not release to a business pilot.** Qwen 8B correctly answers only 2/4
supported policy questions; the authored set is too small for an independent quality
claim even if its total 10/12 score looks attractive. Qwen 1.7B answers 0/4. Four cases
are handled by pre-model safety rules; those do not prove model refusal quality.
Both real reports are retained. Deterministic CI remains reproducible without Ollama.
No model result changes the requirement for real identity, source ACL or human decisions.
