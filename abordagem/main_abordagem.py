"""
Ponto de entrada do módulo de abordagem comercial (Outreach).
Permite selecionar uma lista de leads gerada e disparar abordagens
personalizadas via WhatsApp (com proteção anti-ban) ou E-mail (Gmail SMTP).
"""

import sys
import csv
import argparse
from pathlib import Path
from typing import List, Dict, Any

# Garantir imports do projeto
PROJETO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJETO_ROOT))

from abordagem.canal_whatsapp import processar_campanha_whatsapp
from abordagem.canal_email import processar_campanha_email
from abordagem.tracker import total_envios_hoje, _carregar_historico


LEADS_OUTPUT_DIR = PROJETO_ROOT / "leads" / "output"


def listar_planilhas_leads() -> List[Path]:
    """Lista todos os arquivos CSV disponíveis na pasta de saída de leads."""
    if not LEADS_OUTPUT_DIR.exists():
        return []
    arquivos = sorted(LEADS_OUTPUT_DIR.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    return arquivos


def carregar_leads_csv(caminho_csv: Path) -> List[Dict[str, Any]]:
    """Carrega os leads do arquivo CSV gerado."""
    leads = []
    with open(caminho_csv, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=",")
        for row in reader:
            leads.append(row)
    return leads


def menu_interativo():
    print("=" * 60)
    print("         PAINEL DE ABORDAGEM DE LEADS (CLI)")
    print("=" * 60)

    arquivos = listar_planilhas_leads()
    if not arquivos:
        print("[!] Nenhuma planilha de leads encontrada em leads/output/.")
        print("    Execute primeiro uma busca com 'python3 leads/main.py'.")
        return

    print("Selecione a lista de leads que deseja abordar:")
    for idx, arq in enumerate(arquivos[:10], start=1):
        print(f"  [{idx}] {arq.name}")

    opcao_arq = input("\nEscolha o número da lista: ").strip()
    if not opcao_arq.isdigit() or int(opcao_arq) < 1 or int(opcao_arq) > len(arquivos):
        print("[!] Opção inválida.")
        return

    arquivo_selecionado = arquivos[int(opcao_arq) - 1]
    leads = carregar_leads_csv(arquivo_selecionado)
    print(f"\n[+] Carregados {len(leads)} leads do arquivo: {arquivo_selecionado.name}")

    print("\nQual canal de abordagem deseja utilizar?")
    print("  [1] WhatsApp (Proteção do chip: max 25 msgs/dia, delay randômico 40-90s)")
    print("  [2] WhatsApp (Modo navegador: abre o WhatsApp Web com texto pronto)")
    print("  [3] E-mail Real (Disparo via Gmail com intervalo seguro)")
    print("  [4] E-mail Simulação (Prévia das mensagens sem enviar)")
    print("  [5] Ver histórico de abordagens já realizadas")

    canal_op = input("\nEscolha o canal (1, 2, 3, 4 ou 5): ").strip()

    if canal_op == "1":
        limite_input = input("Quantos leads deseja abordar agora (padrão 20, max 25): ").strip()
        limite = int(limite_input) if limite_input.isdigit() else 20
        processar_campanha_whatsapp(leads, limite_sessao=limite, abrir_navegador=False)

    elif canal_op == "2":
        limite_input = input("Quantos leads deseja abrir no WhatsApp Web (padrão 10): ").strip()
        limite = int(limite_input) if limite_input.isdigit() else 10
        processar_campanha_whatsapp(leads, limite_sessao=limite, abrir_navegador=True)

    elif canal_op == "3":
        limite_input = input("Quantos e-mails deseja enviar agora (padrão 10): ").strip()
        limite = int(limite_input) if limite_input.isdigit() else 10
        processar_campanha_email(leads, modo_simulacao=False, limite=limite)

    elif canal_op == "4":
        limite_input = input("Quantos e-mails deseja simular (padrão 10): ").strip()
        limite = int(limite_input) if limite_input.isdigit() else 10
        processar_campanha_email(leads, modo_simulacao=True, limite=limite)

    elif canal_op == "5":
        historico = _carregar_historico()
        envios = historico.get("envios", [])
        print(f"\n[+] Total de abordagens no histórico: {len(envios)}")
        print(f"[+] Envios hoje pelo WhatsApp: {total_envios_hoje('whatsapp')}")
        for e in envios[-8:]:
            print(f"    - [{e['data']}] ({e['canal']}) {e['nome']} -> {e['identificador']}")
    else:
        print("[!] Opção inválida.")


def main():
    parser = argparse.ArgumentParser(description="Módulo de abordagem comercial automatizada de leads.")
    parser.add_argument("--arquivo", type=str, help="Caminho do arquivo CSV de leads")
    parser.add_argument("--canal", choices=["whatsapp", "email"], help="Canal de envio")
    parser.add_argument("--limite", type=int, default=10, help="Limite de mensagens para esta sessão")
    parser.add_argument("--enviar", action="store_true", help="Enviar e-mail de verdade (sem simulação)")
    parser.add_argument("--navegador", action="store_true", help="Abrir WhatsApp no navegador padrão")

    args = parser.parse_args()

    if args.arquivo and args.canal:
        caminho = Path(args.arquivo)
        if not caminho.exists():
            caminho = LEADS_OUTPUT_DIR / args.arquivo
        if not caminho.exists():
            print(f"[!] Arquivo não encontrado: {args.arquivo}")
            return

        leads = carregar_leads_csv(caminho)
        if args.canal == "whatsapp":
            processar_campanha_whatsapp(leads, limite_sessao=args.limite, abrir_navegador=args.navegador)
        elif args.canal == "email":
            processar_campanha_email(leads, modo_simulacao=not args.enviar, limite=args.limite)
    else:
        menu_interativo()


if __name__ == "__main__":
    main()
