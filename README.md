# AiMemory

Lokaler Memory- und Evidenzspeicher für KI-Workflows, Python 3.11+. Deine ursprünglichen MemoryRecord-, Evidence- und JsonlMemoryStore-Schnittstellen bleiben erhalten.

## Installieren
Im geklonten Repository:

```console
python -m pip install -e ".[dev]"
python -m pytest
aimemory doctor
```

Windows richtet die globale OpenCode-Anbindung mit einem Befehl ein:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup-windows.ps1
```

Das Skript erstellt `.venv`, installiert AiMemory, legt das globale OpenCode-Plugin
unter `~/.config/opencode/plugins/aimemory.js` ab und speichert die nötigen
Umgebungsvariablen dauerhaft für den Windows-Benutzer. Danach OpenCode vollständig
schließen und neu starten. Details: [OpenCode unter Windows](docs/opencode.md#windows-komplettinstallation).

Termux: Python und Git über `pkg install python git` installieren, das private Repository über die eigene GitHub-Anmeldung klonen, `python -m venv .venv` und `source .venv/bin/activate`. Zugangsdaten nicht in Befehls-URLs eintragen. Die hier ausgeführten Tests liefen unter Linux; ein echter Termux-Gerätetest steht aus.

## Alltag

```console
aimemory --namespace demo add "Antworten auf Deutsch" --key language --source user:explicit
aimemory --namespace demo search Deutsch
aimemory --namespace demo conflicts
aimemory --namespace demo context --max-chars 6000
aimemory --namespace demo export
aimemory --namespace demo import export.json
```

`export` schreibt JSON auf stdout. Mit `> export.json` unter Bash oder `| Set-Content -Encoding utf8 export.json` unter PowerShell 7 speichern. Standarddatenbank: ~/.aimemory/memory.sqlite3. `--db`, `AIMEMORY_DB` oder `AIMEMORY_DATA_DIR` ändert den Pfad. Keine privaten Daten in dieses Repository legen.

## open-mem und true-mem

```console
aimemory --namespace demo import open-mem-export.json --format open-mem
aimemory --namespace demo import /pfad/memory.db --format true-mem --project /exakter/projektpfad
aimemory --namespace global import /pfad/memory.db --format true-mem --global-only
aimemory --namespace demo import old-memory.jsonl --format jsonl
```

Details und geprüfte Quellversionen: [Backend-Anbindungen](docs/integrations.md).

## Fertig implementiert
- Validierte Evidenz- und Memory-Datensätze, bestehende JSONL-API.
- SQLite mit atomaren Imports und Erkennung von ID-Kollisionen.
- Projektbereiche, Unicode-Suche, Kontextausgabe, Export/Import und Diagnose.
- OpenMem-v1-Exportadapter inklusive Session-Zusammenfassungen.
- TrueMem-SQLite-Import mit schreibgeschütztem Quellzugriff und expliziter Projektauswahl.
- Konflikthinweise für verschiedene Inhalte mit gleichem metadata.key.
- Keine Laufzeit-Abhängigkeiten, Netzwerk- oder Modellaufrufe in AiMemory.

## Automatische OpenCode-Anbindung
OpenCode **V2 beta** benötigt den separaten Adapter: unter Windows
`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup-windows.ps1 -OpenCodeApi v2`.
[V2-Anleitung und Testgrenzen](docs/opencode-v2.md). Ohne Auswahl bleibt V1 der Standard.

Das mitgelieferte Plugin speichert mit `#merken:` markierte Nutzernachrichten und lädt den Kontext automatisch in neuen Sessions und vor Komprimierungen. Globale Installation: `python -m aimemory install-opencode --global`. Projektbezogene Installation: `python -m aimemory install-opencode /pfad/zum/arbeitsprojekt`. Anschließend den Python-Pfad setzen und OpenCode neu starten. [Vollständige Anleitung](docs/opencode.md).

## Grenzen
Die Backend-Adapter importieren ausdrücklich angeforderte **Snapshots**. Kein bidirektionaler Live-Sync und kein automatischer Zugriff auf ChatGPT-Gespräche. Das OpenCode-Plugin muss auf dem Host installiert werden. Spätere Änderungen oder Löschungen im Quellsystem entfernen alte Snapshots nicht. Konflikthinweise sind keine semantische Wahrheitsprüfung. Das Zeichenbudget garantiert kein Tokenbudget.

Daten sind lokal, aber nicht verschlüsselt. Namespaces sind Filter und keine Benutzerrechte. Memory und Quellen sind unvertrauenswürdige Daten, keine auszuführenden Anweisungen. Quellenreferenzen und Konfidenz allein bestätigen keine Aussage.

## Lizenz
Die vorhandene [Apache-2.0-Lizenz](LICENSE) bleibt erhalten.
