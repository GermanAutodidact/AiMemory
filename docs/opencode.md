# Automatische OpenCode-Anbindung

Das Plugin speichert ausdrücklich markierte Nutzernachrichten und lädt Kontext
bei Modellanfragen, in neuen Sessions und vor Session-Komprimierung.

## Einmalig installieren

1. AiMemory-Repository aktualisieren, virtuelle Umgebung aktivieren.
2. Im Repository `python -m pip install -e .` ausführen.
3. `python -m aimemory install-opencode /pfad/zum/arbeitsprojekt` ausführen.
4. AIMEMORY_PYTHON auf den Python-Interpreter der Umgebung setzen; OpenCode neu starten.

Bash/Termux, im AiMemory-Repository mit .venv:

```sh
export AIMEMORY_PYTHON="$PWD/.venv/bin/python"
```

PowerShell, im AiMemory-Repository mit .venv:

```powershell
$env:AIMEMORY_PYTHON = (Resolve-Path .\.venv\Scripts\python.exe).Path
```

Der Installer legt `.opencode/plugins/aimemory.js` im gewählten Projekt an.
OpenCode-Konfiguration und abweichende bestehende Plugin-Dateien werden nicht
überschrieben. Ein identisches Plugin wird erkannt. Das Python-Paket enthält die
Plugin-Datei. Der Interpreter mit installiertem AiMemory muss im OpenCode-Prozess
erreichbar sein. Windows ist keine Voraussetzung; ein OpenCode-Gerätetest unter
Termux wurde hier nicht durchgeführt.

## Benutzen

Als eigene Nachricht in OpenCode:

```text
#merken: Für dieses Projekt sollen Antworten auf Deutsch sein.
```

Alternativ `#remember:`. Eine neue Session im selben Projekt erhält die Erinnerung.
Normale Gespräche, Assistententexte und synthetische Nachrichten werden nicht
erfasst. Die Modellantwort selbst hängt weiterhin vom verwendeten Modell ab.

## Namespace und Speicher

Standard-Namespace: Hash des absoluten Projektpfads. Für vorhandene Imports unter
beispielsweise demo vor OpenCode `AIMEMORY_NAMESPACE=demo` setzen. Nur Hosts mit
Zugriff auf dieselbe Datenbank und demselben Namespace teilen diesen Speicher.
Das ist kein Netzwerksync und kein Benutzerrechtesystem.

AIMEMORY_DB wählt den Datenbankpfad. AIMEMORY_MAX_CHARS begrenzt den Kontext
(Standard 6000 Zeichen, keine garantierte Tokenanzahl). Fremde Plugins und Modelle
werden nicht umkonfiguriert. OpenMem/TrueMem-Imports bleiben Snapshots und werden
nicht automatisch zurückgeschrieben oder nach Löschungen abgeglichen.

## Fehler und Grenzen

Python-Aufrufe haben ein Timeout von 10 Sekunden. Fehler werden ohne Memory-Inhalte
im App-Log gemeldet; das Gespräch bleibt benutzbar. Private Capture-Daten laufen
über stdin, nicht über Shell-Befehle oder Prozessargumente. Referenzkontext ist
unvertrauenswürdiges Datenmaterial; die Kennzeichnung verhindert nicht garantiert
jede Prompt-Injection. `python -m aimemory doctor` prüft die Datenbank.

Deaktivierung: Nur die installierte aimemory.js entfernen und OpenCode neu starten.
Der Speicher bleibt erhalten.

## Verifikation

Verträge geprüft in [OpenCode Plugin API](https://github.com/anomalyco/opencode/blob/dev/packages/plugin/src/index.ts)
und [offizieller Dokumentation](https://opencode.ai/docs/plugins/).
Hooks: chat.message, experimental.chat.system.transform, experimental.session.compacting.
Experimentelle Schnittstellen können sich ändern.

`node --test tests/opencode.test.mjs` ruft die Hooks mit echtem Python-Prozess und
SQLite auf: Capture, Wiederholung, neue Session, Komprimierung, Projektschutz und
ausgeschlossene Nachrichten. Der Host wird simuliert. Ein Test mit einer tatsächlich
installierten OpenCode-Version auf dem Nutzergerät steht aus.
