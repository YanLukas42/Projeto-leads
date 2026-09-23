"""
Disparador de Abordagem para Influenciadores de Conteúdo (E-mail / WhatsApp).
Conecta via SMTP do Gmail, aplica delays humanos de proteção e registra histórico.
"""

import os
import sys
import csv
import json
import time
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from influencers.config import TRACKER_FILE, LOG_FILE
from influencers.copy_influencers import gerar_email_influencer, gerar_whatsapp_influencer


def carregar_credenciais_smtp() -> tuple:
    """Lê o arquivo .env diretamente na raiz do projeto."""
    env_file = BASE_DIR / ".env"
    user = ""
    password = ""
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip().upper()
                    v = v.strip()
                    if k == "SMTP_USER":
                        user = v
                    elif k in ["SMTP_PASSWORD", "SMTP_PASS"]:
                        password = v
    if not user:
        user = os.getenv("SMTP_USER", "")
    if not password:
        password = os.getenv("SMTP_PASSWORD", "") or os.getenv("SMTP_PASS", "")
    return user, password


def carregar_historico() -> set:
    if not TRACKER_FILE.exists():
        return set()
    try:
        with open(TRACKER_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data.get("enviados", []))
    except Exception:
        return set()


def salvar_historico(identificador: str):
    historico = carregar_historico()
    historico.add(identificador)
    with open(TRACKER_FILE, "w", encoding="utf-8") as f:
        json.dump({"enviados": list(historico), "total": len(historico)}, f, indent=2)


def registrar_log(mensagem: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha = f"[{timestamp}] {mensagem}\n"
    print(linha.strip())
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(linha)


def enviar_email_influencer(destinatario_email: str, assunto: str, corpo: str) -> bool:
    """Envia o e-mail via servidor SMTP do Gmail."""
    user, password = carregar_credenciais_smtp()

    if not user or not password:
        registrar_log("[ERRO] SMTP_USER ou SMTP_PASSWORD não encontrados no .env")
        return False

    msg = MIMEMultipart()
    msg["From"] = f"Lukas <{user}>"
    msg["To"] = destinatario_email
    msg["Subject"] = assunto
    msg.attach(MIMEText(corpo, "plain", "utf-8"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.login(user, password)
            server.sendmail(user, destinatario_email, msg.as_string())
        return True
    except Exception as err:
        registrar_log(f"[FALHA SMTP] Erro ao enviar para {destinatario_email}: {err}")
        return False


def disparar_campanha_influencers(caminho_csv: str, meta_envios: int = 15):
    """Executa a campanha de e-mail para a lista minerada."""
    path = Path(caminho_csv)
    if not path.exists():
        print(f"Arquivo não encontrado: {caminho_csv}")
        return

    historico = carregar_historico()
    leads = []

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = (row.get("Email") or "").strip()
            canal = (row.get("Canal") or "").strip()
            if email and email != "X" and email not in historico:
                leads.append(row)

    registrar_log(f"=== INÍCIO DA CAMPANHA INFLUENCERS ===")
    registrar_log(f"Arquivo alvo: {path.name} | Leads inéditos aptos: {len(leads)} | Meta: {meta_envios}")

    if not leads:
        registrar_log("Nenhum influenciador inédito com e-mail encontrado no arquivo.")
        return

    enviados = 0
    for i, lead in enumerate(leads[:meta_envios], 1):
        canal = lead["Canal"]
        email = lead["Email"]
        copy = gerar_email_influencer(lead)

        registrar_log(f"[{i}/{min(meta_envios, len(leads))}] Enviando para: {canal} <{email}>")
        registrar_log(f"    Assunto: '{copy['assunto']}'")

        sucesso = enviar_email_influencer(email, copy["assunto"], copy["corpo"])
        if sucesso:
            registrar_log(f"    [SUCESSO] Entregue ao servidor de e-mail.")
            salvar_historico(email)
            enviados += 1
        else:
            registrar_log(f"    [FALHA] Falha no envio.")

        # Pausa humana anti-spam
        if i < min(meta_envios, len(leads)):
            pausa = random.randint(12, 22)
            registrar_log(f"    [PAUSA] Aguardando {pausa}s antes do próximo canal...")
            time.sleep(pausa)

    registrar_log(f"=== CAMPANHA FINALIZADA: {enviados} envios com sucesso! ===")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 influencers/disparador_influencers.py <caminho_csv> [meta]")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    meta = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    disparar_campanha_influencers(csv_file, meta)
