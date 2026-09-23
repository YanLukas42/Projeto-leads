"""
Módulo de disparo de e-mails B2B (Cold Mail).
Suporta modo simulação (Dry-Run) e envio real via servidor SMTP do Gmail.
Aplica intervalo de segurança de 5 a 10 segundos entre mensagens.
"""

import os
import time
import random
import smtplib
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any

from abordagem.tracker import foi_abordado, registrar_envio
from abordagem.gerador_copy import gerar_email_abordagem


DELAY_EMAIL_MIN = 5
DELAY_EMAIL_MAX = 10


def carregar_config_smtp() -> Dict[str, str]:
    """Carrega as credenciais SMTP do arquivo .env ou variáveis de ambiente."""
    env_file = Path(__file__).resolve().parent.parent / ".env"
    config = {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": "587",
        "smtp_user": "",
        "smtp_password": ""
    }

    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    k = key.strip().lower()
                    v = val.strip()
                    if k == "smtp_user":
                        config["smtp_user"] = v
                    elif k == "smtp_password":
                        config["smtp_password"] = v
                    elif k == "smtp_server":
                        config["smtp_server"] = v
                    elif k == "smtp_port":
                        config["smtp_port"] = v

    # Fallback para variáveis de ambiente
    config["smtp_user"] = os.environ.get("SMTP_USER", config["smtp_user"])
    config["smtp_password"] = os.environ.get("SMTP_PASSWORD", config["smtp_password"])
    return config


def enviar_email_smtp(destinatario: str, assunto: str, corpo: str, config: Dict[str, str]) -> bool:
    """Envia um e-mail individual via conexão SMTP."""
    servidor = config.get("smtp_server", "smtp.gmail.com")
    porta = int(config.get("smtp_port", 587))
    usuario = config.get("smtp_user", "")
    senha = config.get("smtp_password", "")

    if not usuario or not senha:
        print("[!] Credenciais SMTP não encontradas.")
        return False

    msg = MIMEMultipart()
    msg["From"] = f"Lukas <{usuario}>"
    msg["To"] = destinatario
    msg["Subject"] = assunto
    msg.attach(MIMEText(corpo, "plain", "utf-8"))

    try:
        with smtplib.SMTP(servidor, porta, timeout=12) as server:
            server.starttls()
            server.login(usuario, senha)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"[!] Erro ao enviar para {destinatario}: {e}")
        return False


def processar_campanha_email(leads: List[Dict[str, Any]], config_smtp: Dict[str, str] = None, modo_simulacao: bool = False, limite: int = 10):
    """
    Executa a campanha de e-mail marketing B2B.
    Se modo_simulacao for True, exibe as mensagens sem fazer o envio real.
    """
    if config_smtp is None:
        config_smtp = carregar_config_smtp()

    print("\n" + "=" * 60)
    print("           DISPARADOR B2B DE E-MAIL")
    print(f"[*] Remetente: {config_smtp.get('smtp_user')}")
    print(f"[*] Modo: {'SIMULAÇÃO (Prévia)' if modo_simulacao else 'DISPARO REAL (Via Gmail SMTP)'}")
    print(f"[*] Limite desta sessão: {limite}")
    print("=" * 60)

    leads_aptos = []
    for l in leads:
        email = l.get("Email") or l.get("email") or ""
        if email and email != "X" and "@" in email and not foi_abordado(email):
            leads_aptos.append(l)

    print(f"[+] Leads com e-mail válido e pendente: {len(leads_aptos)}")
    if not leads_aptos:
        print("[!] Nenhum lead com e-mail pendente encontrado.")
        return

    alvos = leads_aptos[:limite]
    sucessos = 0

    for idx, lead in enumerate(alvos, start=1):
        nome = lead.get("Nome") or lead.get("nome") or "Empresa"
        email = (lead.get("Email") or lead.get("email")).strip().lower()

        conteudo = gerar_email_abordagem(lead)
        assunto = conteudo["assunto"]
        corpo = conteudo["corpo"]

        print(f"\n[{idx}/{len(alvos)}] 🏢 {nome} | 📧 {email}")
        print(f"   Assunto: {assunto}")

        if not modo_simulacao:
            print("   [⏳] Enviando e-mail via Gmail...", end=" ", flush=True)
            ok = enviar_email_smtp(email, assunto, corpo, config_smtp)
            if ok:
                registrar_envio(email, "email_real", nome)
                sucessos += 1
                print("-> [ENVIADO COM SUCESSO!]")
            else:
                print("-> [FALHA]")
        else:
            registrar_envio(email, "email_simulado", nome)
            sucessos += 1
            print("   [i] Mensagem simulada registrada com sucesso.")

        if idx < len(alvos):
            delay = random.randint(DELAY_EMAIL_MIN, DELAY_EMAIL_MAX)
            print(f"   ⏳ Pausa de segurança de {delay}s...", flush=True)
            time.sleep(delay)

    print("\n" + "=" * 60)
    print(f"[OK] Campanha de e-mail finalizada! Total de e-mails enviados: {sucessos}/{len(alvos)}")
    print("=" * 60)
