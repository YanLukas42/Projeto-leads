"""
Módulo de disparo e geração de mensagens para WhatsApp.
Implementa regras rigorosas de proteção do chip:
- Teto diário de segurança (20 a 30 mensagens).
- Delays randômicos humanos (30 a 60 segundos entre envios).
- Registro no tracker para impedir envios duplicados.
"""

import time
import random
import webbrowser
import urllib.parse
from typing import List, Dict, Any

from abordagem.tracker import foi_abordado, registrar_envio, total_envios_hoje
from abordagem.gerador_copy import gerar_mensagem_whatsapp


from abordagem.config import WHATSAPP_LIMITE_DIARIO, WHATSAPP_DELAY_MIN, WHATSAPP_DELAY_MAX

LIMITE_DIARIO_PADRAO = WHATSAPP_LIMITE_DIARIO
DELAY_MIN = WHATSAPP_DELAY_MIN
DELAY_MAX = WHATSAPP_DELAY_MAX


def formatar_numero_whatsapp(numero: str) -> str:
    """Garante o prefixo 55 internacional do Brasil."""
    num_limpo = "".join([c for c in numero if c.isdigit()])
    if len(num_limpo) in (10, 11):
        return "55" + num_limpo
    return num_limpo


def processar_campanha_whatsapp(leads: List[Dict[str, Any]], limite_sessao: int = 20, abrir_navegador: bool = False):
    """
    Executa a preparação e envio das abordagens para o WhatsApp com proteção do chip.
    """
    print("\n" + "=" * 60)
    print("      DISPARADOR SEGURO DE WHATSAPP (ANTI-BAN)")
    print("=" * 60)

    enviados_hoje = total_envios_hoje("whatsapp")
    restantes_hoje = max(0, LIMITE_DIARIO_PADRAO - enviados_hoje)

    print(f"[*] Mensagens já enviadas hoje: {enviados_hoje}/{LIMITE_DIARIO_PADRAO}")
    print(f"[*] Cota de segurança disponível: {restantes_hoje}")

    if restantes_hoje == 0:
        print("[!] Teto diário de segurança atingido para este chip.")
        print("    Para proteger o número, aguarde até amanhã para novos envios.")
        return

    leads_aptos = []
    for l in leads:
        celular = l.get("Celular_WhatsApp") or l.get("celular_whatsapp") or ""
        if celular and celular != "X" and not foi_abordado(celular):
            leads_aptos.append(l)

    print(f"[+] Leads aptos com WhatsApp válido e inédito: {len(leads_aptos)}")
    if not leads_aptos:
        print("[!] Nenhum lead pendente com WhatsApp encontrado.")
        return

    total_a_processar = min(len(leads_aptos), limite_sessao, restantes_hoje)
    print(f"[*] Total que será processado nesta sessão: {total_a_processar}")
    print(f"[*] Delays programados: entre {DELAY_MIN}s e {DELAY_MAX}s por mensagem (comportamento humano).")
    print("-" * 60)

    sucessos = 0
    for idx, lead in enumerate(leads_aptos[:total_a_processar], start=1):
        nome = lead.get("Nome") or lead.get("nome") or "Empresa"
        celular = formatar_numero_whatsapp(lead.get("Celular_WhatsApp") or lead.get("celular_whatsapp"))
        
        # Gerar copy personalizada
        mensagem = gerar_mensagem_whatsapp(lead)
        texto_encoded = urllib.parse.quote(mensagem)
        link_whatsapp = f"https://wa.me/{celular}?text={texto_encoded}"

        print(f"\n[{idx}/{total_a_processar}] 🏢 {nome} | 📱 +{celular}")
        print("💬 Prévia da mensagem gerada:")
        for linha in mensagem.split("\n")[:2]:
            print(f"   > {linha}")

        if abrir_navegador:
            print("[+] Abrindo WhatsApp Web com a mensagem pronta...")
            webbrowser.open(link_whatsapp)
        else:
            print(f"[🔗 Link Direto]: {link_whatsapp}")

        # Registrar no histórico
        registrar_envio(celular, "whatsapp", nome)
        sucessos += 1

        # Aplicar delay de segurança se houver próximo item
        if idx < total_a_processar:
            delay = random.randint(DELAY_MIN, DELAY_MAX)
            print(f"⏳ Pausa de segurança anti-ban: aguardando {delay}s...", flush=True)
            time.sleep(delay)

    print("\n" + "=" * 60)
    print(f"[OK] Sessão finalizada com sucesso! {sucessos} abordagens registradas.")
    print(f"     Total de envios hoje: {total_envios_hoje('whatsapp')}/{LIMITE_DIARIO_PADRAO}")
    print("=" * 60)
