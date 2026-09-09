# Backend-Anbindungen

## Geprüfte Quellverträge
- OpenMem: https://github.com/clopca/open-mem/blob/main/src/tools/export.ts — Blob 042e381a78b8b1e65e7ef19d294bda06c76dccfb.
- TrueMem: https://github.com/rizal72/true-mem/blob/main/src/storage/database.ts — Blob 54c3063e8eb39185552b9f70fcaa7fab0567b047.

Die Adapter wurden mit synthetischen Fixtures der geprüften Quellformate getestet, nicht mit privaten Nutzerdaten oder einem laufenden OpenCode-Prozess.

## OpenMem
Das vorhandene Exportwerkzeug in OpenCode aufrufen und dessen Ergebnis als Datei speichern. Die Dokumentation nennt es mem-export; die README nennt auch memory.transfer.export. Die tatsächliche Werkzeugliste der installierten Version ist maßgeblich.

AiMemory akzeptiert das JSON-Objekt und die vom geprüften Tool vorangestellte Exported-Meldung. Version 1, observations und summaries werden übernommen; Originalfelder bleiben in metadata.original erhalten. Gelöschte oder überholte Observationen werden als inactive markiert und aus der Kontextausgabe ausgeschlossen.

## TrueMem
Die konkrete memory.db mit --format true-mem angeben. --project muss dem exakten gespeicherten project_scope entsprechen. --global-only importiert ausschließlich globale Erinnerungen. Beide Optionen dürfen nicht kombiniert werden.

Die Quelle wird über SQLite mode=ro und query_only gelesen. Nur aktive Datensätze werden übernommen. Quellenereignis-IDs bleiben erhalten; Rohereignisse, Embeddings und Laufzeitstatistiken werden nicht kopiert. Schemafehler stoppen den Import.

## Snapshot-Semantik
Identische Imports sind idempotent. Geänderte Quellaussagen erzeugen neue Snapshot-IDs. Vorhandene Snapshots bleiben erhalten, auch wenn die Quelle später etwas löscht. Daher keine automatische Aktualitätsgarantie. Importierte Belege bleiben unverified.

## OpenCode
config/opencode.example.jsonc enthält die dokumentierte Plugin-Liste. In bestehende Einstellungen einfügen, diese nicht überschreiben. Die Plugins übernehmen ihre eigene Erfassung; AiMemory ergänzt die explizite CLI-Schnittstelle. Kein neuer Modelldienst und kein automatischer Modellwechsel werden eingerichtet.

OpenMem kann selbst KI-Kompression und Provider-Fallbacks verwenden. AiMemory garantiert nicht die Kostenfreiheit fremder Plugins. Für eine laufende Gesamteinbindung fehlen noch die konkrete Host-Konfiguration und ein Ende-zu-Ende-Test in der tatsächlichen Installation. Ein Windows-PC ist keine Entwicklungsvoraussetzung.

