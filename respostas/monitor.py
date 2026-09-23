"""
Módulo de Monitoramento Automático de Respostas (Inbox de Prospecção).
Conecta-se à caixa de entrada via IMAP para identificar automaticamente
quando um lead abordado responde à sua campanha.
"""

import os
import sys
import time
import imaplib
import email
from email.header import decode_header
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

PROJETO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJETO_ROOT))

from abordagem.canal_email import carregar_config_smtp
from abordagem.tracker import _carregar_historico


RESPOSTAS_FILE = Path(__file__).resolve().parent / "respostas_recebidas.json"


def _carregar_respostas() -> List[Dict[str, Any]]:
    if not RESPOSTAS_FILE.exists():
        return []
    try:
        import json
        with open(RESPOSTAS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _salvar_respostas(lista: List[Dict[str, Any]]):
    import json
    with open(RESPOSTAS_FILE, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=2, ensure_ascii=False)


def decodificar_texto(header_val) -> str:
    if not header_val:
        return ""
    partes = decode_header(header_val)
    resultado = ""
    for texto, encoding in partes:
        if isinstance(texto, bytes):
            resultado += texto.decode(encoding or "utf-8", errors="ignore")
        else:
            resultado += str(texto)
    return resultado


def checar_novas_respostas() -> List[Dict[str, Any]]:
    """
    Verifica se há respostas de leads abordados na Caixa de Entrada do Gmail.
    """
    config = carregar_config_smtp()
    user = config.get("smtp_user")
    password = config.get("smtp_password")

    if not user or not password:
        print("[!] Credenciais não configuradas para monitorar respostas.")
        return []

    # Carregar e-mails abordados de empresas e de influenciadores
    historico = _carregar_historico()
    emails_abordados = {
        item.get("identificador", "").lower(): item.get("nome", "")
        for item in historico.get("envios", [])
        if "@" in item.get("identificador", "")
    }

    # Carregar e-mails de influenciadores
    influencers_hist = PROJETO_ROOT / "influencers" / "historico_influencers.json"
    if influencers_hist.exists():
        try:
            import json
            with open(influencers_hist, "r", encoding="utf-8") as f:
                inf_data = json.load(f)
                for email_inf in inf_data.get("enviados", []):
                    emails_abordados[email_inf.lower()] = "Criador de Conteúdo / Influenciador"
        except Exception:
            pass

    if not emails_abordados:
        return []

    novas_respostas = []
    respostas_existentes = _carregar_respostas()
    ids_existentes = {r.get("msg_id") for r in respostas_existentes}

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(user, password)
        mail.select("inbox")

        # Buscar e-mails recentes não lidos ou dos últimos dias
        status, mensagens = mail.search(None, "ALL")
        if status != "OK":
            mail.logout()
            return []

        ids = mensagens[0].split()
        # Verificar as últimas 20 mensagens da caixa
        for msg_num in ids[-20:]:
            status, dados = mail.fetch(msg_num, "(RFC822)")
            if status != "OK":
                continue

            raw_email = dados[0][1]
            msg = email.message_from_bytes(raw_email)

            remetente_raw = decodificar_texto(msg.get("From"))
            assunto = decodificar_texto(msg.get("Subject"))
            msg_id = msg.get("Message-ID", str(msg_num))

            if msg_id in ids_existentes:
                continue

            # Extrair e-mail limpo do remetente
            import re
            match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', remetente_raw)
            if not match:
                continue
            email_remetente = match.group(0).lower()

            if email_remetente in emails_abordados:
                nome_empresa = emails_abordados[email_remetente]
                corpo_texto = ""

                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            corpo_texto = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                            break
                else:
                    corpo_texto = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

                info_resposta = {
                    "msg_id": msg_id,
                    "empresa": nome_empresa,
                    "email": email_remetente,
                    "assunto": assunto,
                    "previa": corpo_texto.strip()[:200],
                    "data_recebimento": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                novas_respostas.append(info_resposta)
                respostas_existentes.append(info_resposta)

        mail.logout()
        if novas_respostas:
            _salvar_respostas(respostas_existentes)

    except Exception as e:
        print(f"[!] Erro ao monitorar caixa de entrada: {e}")

    return novas_respostas


if __name__ == "__main__":
    print("[*] Verificando se algum estúdio/lead respondeu na Caixa de Entrada...")
    respostas = checar_novas_respostas()
    if respostas:
        print(f"\n🔥 ENCONTRADAS {len(respostas)} NOVAS RESPOSTAS:")
        for r in respostas:
            print(f"  🏢 {r['empresa']} ({r['email']})")
            print(f"     Assunto: {r['assunto']}")
            print(f"     Mensagem: {r['previa'][:120]}...\n")
    else:
        print("[i] Nenhuma resposta nova identificada ainda.")
