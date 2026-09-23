"""
CLI Principal da Vertente de Influenciadores (10k a 50k inscritos).
Mineração, Enriquecimento e Abordagem Comercial para Aulas de Inglês.
"""

import sys
import csv
import argparse
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from influencers.config import OUTPUT_DIR, MIN_INSCRITOS_PADRAO, MAX_INSCRITOS_PADRAO
from influencers.scraper_youtube import minerar_influenciadores
from influencers.copy_influencers import gerar_email_influencer, gerar_whatsapp_influencer


def exportar_csv(leads: list, termo: str) -> Path:
    """Exporta lista de influenciadores para CSV RFC 4180."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    termo_slug = termo.lower().replace(" ", "_")[:20]
    filename = OUTPUT_DIR / f"influencers_{termo_slug}_{len(leads)}_{timestamp}.csv"
    
    colunas = ["Canal", "Nicho", "Inscritos", "Email", "WhatsApp", "Instagram", "Linktree", "URL_Canal", "Status"]
    
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=colunas, delimiter=",", quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for l in leads:
            writer.writerow(l)
            
    return filename


def main():
    parser = argparse.ArgumentParser(description="Prospecção de Influenciadores de Conteúdo (10k-50k) para Aulas de Inglês")
    parser.add_argument("--termo", "-t", type=str, help="Termo de pesquisa (ex: 'programação python', 'jogos indies', 'carreira ti')")
    parser.add_argument("--nicho", "-n", type=str, default="Tecnologia & Carreira", help="Nome do nicho do público do canal")
    parser.add_argument("--limite", "-l", type=int, default=15, help="Quantidade máxima de canais a minerar")
    parser.add_argument("--min", type=int, default=MIN_INSCRITOS_PADRAO, help="Mínimo de inscritos (default: 10.000)")
    parser.add_argument("--max", type=int, default=MAX_INSCRITOS_PADRAO, help="Máximo de inscritos (default: 50.000)")
    parser.add_argument("--previa-copy", action="store_true", help="Mostra a prévia das mensagens geradas para os leads minerados")
    args = parser.parse_args()

    termo = args.termo
    if not termo:
        print("\n=== PROSPECÇÃO DE INFLUENCIADORES (10k a 50k) ===")
        print("Foco: Contratação de publis e parcerias para Aulas de Inglês.")
        termo = input("\nDigite o termo de busca no YouTube (ex: 'programação', 'jogos indies', 'estudos'): ").strip()
        if not termo:
            print("Termo não pode ser vazio.")
            sys.exit(1)

    leads = minerar_influenciadores(
        termo_busca=termo,
        nicho=args.nicho,
        min_inscritos=args.min,
        max_inscritos=args.max,
        limite=args.limite
    )

    if not leads:
        print("⚠️ Nenhum canal encontrado para o filtro especificado.")
        return

    csv_path = exportar_csv(leads, termo)
    print(f"\n📂 Lista de influenciadores salva com sucesso em:")
    print(f"👉 {csv_path}")

    # Exibir resumo no terminal
    com_contato = sum(1 for l in leads if l["Email"] != "X" or l["WhatsApp"] != "X")
    print(f"\n📊 RESUMO DA MINERAÇÃO:")
    print(f"- Total de canais: {len(leads)}")
    print(f"- Canais com E-mail ou WhatsApp direto: {com_contato} ({int(com_contato/len(leads)*100)}%)")

    # Amostra de Copy
    if args.previa_copy or True:
        primeiro = leads[0]
        copy_email = gerar_email_influencer(primeiro)
        copy_wa = gerar_whatsapp_influencer(primeiro)
        print("\n" + "="*60)
        print(f"✉️ EXEMPLO DE E-MAIL GERADO ({primeiro['Canal']}):")
        print(f"Assunto: {copy_email['assunto']}")
        print(copy_email['corpo'])
        print("="*60)
        print(f"💬 EXEMPLO DE WHATSAPP GERADO ({primeiro['Canal']}):")
        print(copy_wa)
        print("="*60)


if __name__ == "__main__":
    main()
