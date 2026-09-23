"""
Disparador autônomo em background de campanhas de e-mail.
Executa envios com intervalos seguros, validação de e-mail,
gravação contínua de log e atualização do histórico de envio.
"""

import sys
import time
import random
from pathlib import Path
from datetime import datetime

PROJETO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJETO_ROOT))

from abordagem.main_abordagem import carregar_leads_csv
from abordagem.canal_email import enviar_email_smtp, carregar_config_smtp
from abordagem.gerador_copy import gerar_email_abordagem
from abordagem.tracker import foi_abordado, registrar_envio

LOG_FILE = Path(__file__).resolve().parent / "campanha_ativa.log"


def log_mensagem(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha = f"[{timestamp}] {msg}"
    print(linha, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(linha + "\n")


def rodar_disparos_background(caminho_csv: Path, limite: int = 50, delay_min: int = 8, delay_max: int = 15):
    """
    Processa a lista de leads e dispara e-mails de forma contínua e segura.
    """
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"=== INÍCIO DA CAMPANHA EM BACKGROUND: {datetime.now()} ===\n")

    log_mensagem(f"Iniciando campanha para o arquivo: {caminho_csv.name}")
    config_smtp = carregar_config_smtp()
    remetente = config_smtp.get("smtp_user")
    log_mensagem(f"Remetente autenticado: {remetente}")

    leads = carregar_leads_csv(caminho_csv)
    log_mensagem(f"Total de leads lidos no arquivo: {len(leads)}")

    # Filtrar aptos
    leads_aptos = []
    for l in leads:
        email = l.get("Email") or l.get("email") or ""
        if email and email != "X" and "@" in email and not foi_abordado(email):
            leads_aptos.append(l)

    log_mensagem(f"Leads qualificados e inéditos para envio: {len(leads_aptos)}")
    alvos = leads_aptos[:limite]
    log_mensagem(f"Meta de envios desta rodada: {len(alvos)}")

    sucessos = 0
    falhas = 0

    for idx, lead in enumerate(alvos, start=1):
        nome = lead.get("Nome") or lead.get("nome") or "Empresa"
        email = (lead.get("Email") or lead.get("email")).strip().lower()

        conteudo = gerar_email_abordagem(lead)
        assunto = conteudo["assunto"]
        corpo = conteudo["corpo"]

        log_mensagem(f"[{idx}/{len(alvos)}] Enviando para: {nome} <{email}>")
        log_mensagem(f"    Assunto: '{assunto}'")

        ok = enviar_email_smtp(email, assunto, corpo, config_smtp)
        if ok:
            registrar_envio(email, "email_real", nome)
            sucessos += 1
            log_mensagem(f"    [SUCESSO] E-mail entregue ao servidor SMTP.")
        else:
            falhas += 1
            log_mensagem(f"    [ERRO] Falha ao enviar para {email}.")

        if idx < len(alvos):
            espera = random.randint(delay_min, delay_max)
            log_mensagem(f"    [PAUSA] Aguardando {espera}s de resfriamento antes do próximo envio...")
            time.sleep(espera)

    log_mensagem(f"=== CAMPANHA FINALIZADA ===")
    log_mensagem(f"Total disparados com sucesso: {sucessos}/{len(alvos)} (Falhas: {falhas})")


if __name__ == "__main__":
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else (PROJETO_ROOT / "leads" / "output" / "leads_brasil_55_estudios_games_20260921_203958.csv")
    limite = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    rodar_disparos_background(csv_path, limite=limite)
