# Inrim Controllo Accessi Provisioning Lettori

Procedura per **installare** [I] un nuovo lettore badge o **sostituire** [S] un
lettore danneggiato, dato un lettore raggiungibile in rete. Ogni procedura è un
record `ca.provisioning_lettore` con uno stato: i passi si eseguono via API
(anche da Ansible, vedi `ansible/README.md` nel repo Controllo-Accessi) e
si può riprendere dopo le attese. Ogni passo resta nel log della procedura.

Accesso: gruppo **Technician** (`controllo_accessi.ca_tech`), utente con API
abilitata. Token da `POST /token/authenticate`, header `token`.

## Passi

| # | Passo API | I | S | Cosa fa |
|---|---|---|---|---|
| 1 | `POST /api/provisioning_lettore` `{operation, typology}` | ✓ | ✓ | Avvia: `install`/`replace`, `stamping`/`local_access` |
| 2, 2.1 | `check_ip` `{ip, setup_ip, final_ip?, ente_azienda_id?}` | ✓ | ✓ | IP non usato da altri lettori (anche archiviati), poi `/info` + `/status`: se il lettore non risponde non si procede. `setup_ip` Y/N: l'IP è solo di setup |
| 3, 3.1.i | `set_group` `{ca_category_id}` o `{new_category: {name, code?}}` | ✓ | ✓ | Gruppo punti accesso di destinazione; in installazione si può crearne uno nuovo |
| 4.s | `set_replace` `{old_punto_accesso_id}` | | ✓ | Punto accesso del gruppo da sostituire: crea il lettore `<nome>.replace` e un nuovo punto accesso con la stessa configurazione (posizione, GRUM, referente, utenti abilitati). In laboratorio copia i badge autorizzati |
| 4.i | `set_access_point` `{reader_name, direction, codice_lettore_grum, ca_persona_id?}` | ✓ | | Dati del punto accesso; GRUM obbligatorio per stamping (20-999, non già usato) |
| 5.i | `set_position` `{ca_spazio_id}` o `{name, ente_azienda_id, codice_locale?, tipo_spazio_id}` | ✓ | | Posizione con codice e sede, creata se non esiste; crea lettore e punto accesso (disabilitato) |
| 6 | `activate` | ✓ | ✓ | Check del lettore, attiva il punto accesso; per stamping collega tutti i badge validi |
| 7, 7.1.s | `verify` | ✓ | ✓ | Stamping: dopo `provisioning_lettore.stamping_wait_minutes` (10), sync eseguito e stesso numero di badge del vecchio punto (o di un punto stamping attivo). Laboratorio in sostituzione: stessi utenti autorizzati del vecchio |
| 8.s | `disable_old` | | ✓ | Disabilita il vecchio punto accesso e il suo lettore; il nuovo lettore prende il nome del vecchio. Se l'IP non era di setup: fine |
| 9, 10 | `final_check` `{final_ip?}` | ✓ | ✓ | Solo con IP di setup: dopo il cambio IP sul dispositivo, check sull'IP definitivo (in sostituzione, di default quello del vecchio lettore) e aggiornamento del lettore |
| | `cancel` | ✓ | ✓ | Annulla; i record già creati vanno sistemati a mano |

I passi sono `POST /api/provisioning_lettore/<id>/<passo>`. Inoltre:

- `GET /api/provisioning_lettore/<id>`: stato e `next_step`
- `GET /api/provisioning_lettore/<id>/options`: scelte per il prossimo passo (gruppi, punti accesso sostituibili, sedi, tipi spazio)
- `GET /api/provisioning_lettore?domain=[...]`: elenco procedure

## Risposte

- `200` con `{ok, step, message, retry_after, data, record}`. Con `ok: false`
  il passo non è riuscito, lo stato non cambia e si può ripetere;
  `retry_after > 0` vuol dire che basta riprovare dopo quei secondi (attesa sync,
  dispositivo non ancora sul nuovo IP).
- `400 {"error": ...}`: input non valido o passo fuori sequenza.
- `404`: procedura non trovata.

## Check lettore

`POST /api/provisioning_lettore/check` con `{ip}`, `{lettore_id}` o
`{punto_accesso_id}` (e `ente_azienda_id` opzionale per il gateway): chiama
`/info` e `/status` del gateway e restituisce device id, tipo, modalità,
eventi in memoria, orologio del lettore e scarto rispetto al server, avvisi
(eventi da scaricare prima della scrittura tag, orologio fuori tolleranza:
`provisioning_lettore.max_clock_drift_seconds`) e i lettori che usano già
quell'IP. Usa il gateway della sede se configurato, altrimenti
`service_reader.url` / `service_reader.jwt`.
