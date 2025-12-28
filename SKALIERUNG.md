Dieses Dokument dient als Warnsystem und Fahrplan für das technische Wachstum.

Stufe           	    Trigger	        Zeitaufwand	        Gefahren für Nicht-Coder	                                                        Mitigation (Schutz)
v0.2.x (JSON)   	    < 500 User	    0h (Status Quo)	    Datenverlust: Ein falscher Skript-Lauf überschreibt die profiles_db.json.           Tägliche automatisierte Backups der JSON-Datei auf einen externen Speicher.
v0.3.x (Vektor-DB)	    > 500 User	    4-6h (Migration)	Latenz: Die App wird quälend langsam, weil das Laden der JSON zu lange dauert.  	Umstieg auf ChromaDB oder Pinecone. Die Suche wird von O(n) auf O(logn) beschleunigt.
v1.0.x (Cloud-Auto)	    > 5.000 User	10-15h (Setup)	    Kosten-Explosion: Unbegrenzte API-Calls bei viralem Wachstum fressen das Budget.    Implementierung von Rate-Limiting (max. 3 Vibe-Checks pro User/Stunde).