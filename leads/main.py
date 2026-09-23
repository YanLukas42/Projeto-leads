"""
Ponto de entrada da ferramenta de prospecção de leads via terminal.
Opera com motor multi-fontes e suporte a Múltiplas Cidades e Bairros Nobres/Específicos.
Exemplos de entrada:
- "Campinas: Cambuí, Taquaral"
- "DF: Asa Sul, Águas Claras"
- "Campinas, Paulínia, Valinhos"
"""

import sys
import argparse
from pathlib import Path

# Garantir importação correta dos módulos locais
sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.geo_parser import interpretar_locais
from core.scraper import buscar_comercios_locais
from core.scraper_web import buscar_leads_web
from core.scraper_maps import buscar_leads_mapas
from core.deduplicator import consolidar_leads
from core.enricher import enriquecer_lead_pelo_site
from core.cnpj import consultar_cnpj
from core.exporter import exportar_para_csv


def linha_separadora():
    print("-" * 65)


def fluxo_busca_comercios(entrada_cidade: str, nicho: str, limite: int):
    linha_separadora()
    print(f"[*] MOTOR MULTI-FONTES DE LEADS (CIDADES & BAIRROS)")
    print(f"[*] Entrada: '{entrada_cidade}' | Nicho: '{nicho}' | Limite por alvo: {limite}")
    linha_separadora()

    locais = interpretar_locais(entrada_cidade)
    if not locais:
        print("[!] Localidade inválida.")
        return

    print(f"[+] Alvos geográficos identificados ({len(locais)}):")
    for loc in locais:
        print(f"    📍 {loc['rotulo']}")
    linha_separadora()

    todos_leads_brutos = []

    for idx_loc, loc in enumerate(locais, start=1):
        cidade = loc["cidade"]
        bairro = loc["bairro"]
        termo_geo = loc["termo_busca"]
        rotulo = loc["rotulo"]

        print(f"\n--- [{idx_loc}/{len(locais)}] Processando: {rotulo} ---")

        # 1. Base Geográfica (OSM)
        print("    [1/3] Base comercial física...")
        lote_geo = buscar_comercios_locais(cidade, nicho, limite=limite, bairro=bairro, termo_geo=termo_geo)
        print(f"          -> {len(lote_geo)} encontrados.")

        # 2. Busca Web e Instagram no bairro/cidade
        print("    [2/3] Perfis comerciais web/Instagram...")
        lote_web = buscar_leads_web(cidade, nicho, limite=limite, bairro=bairro)
        print(f"          -> {len(lote_web)} encontrados.")

        # 3. Fichas de Mapa
        print("    [3/3] Fichas e presença de mapa...")
        termo_mapa = f"{nicho} {bairro} {cidade}" if bairro else f"{nicho} {cidade}"
        lote_mapas = buscar_leads_mapas(cidade, termo_mapa, limite=limite)
        print(f"          -> {len(lote_mapas)} encontrados.")

        todos_leads_brutos.append(lote_geo)
        todos_leads_brutos.append(lote_web)
        todos_leads_brutos.append(lote_mapas)

    # Consolidação e Deduplicação Inteligente
    linha_separadora()
    print("[*] Consolidando, deduplicando e enriquecendo contatos...")
    leads_unificados = consolidar_leads(todos_leads_brutos)

    if not leads_unificados:
        print("[!] Nenhum lead retornado para esses critérios.")
        return

    leads_finais = []
    quentes = 0
    celulares = 0
    instagrams = 0

    for idx, lead in enumerate(leads_unificados, start=1):
        print(f"    [{idx}/{len(leads_unificados)}] Enriquecendo: {lead['nome'][:25]}...", end="\r", flush=True)
        lead_enriquecido = enriquecer_lead_pelo_site(lead)
        leads_finais.append(lead_enriquecido)

        if "QUENTE" in lead_enriquecido.get("status_lead", ""):
            quentes += 1
        if lead_enriquecido.get("celular_whatsapp"):
            celulares += 1
        if lead_enriquecido.get("instagram"):
            instagrams += 1

    print("\n[+] Processamento multi-alvo finalizado!")

    # Nome base para o arquivo
    nome_saida = "multi_alvos"
    if len(locais) == 1:
        nome_saida = locais[0]["cidade"]
    else:
        nome_saida = f"{locais[0]['cidade']}_e_regioes"

    arquivo_csv = exportar_para_csv(leads_finais, cidade=nome_saida, nicho=nicho)

    linha_separadora()
    print("                 RELATÓRIO CONJUNTO DA RODADA")
    linha_separadora()
    print(f"📁 Arquivo gerado: {arquivo_csv}")
    print(f"📊 Total de Leads Únicos: {len(leads_finais)}")
    print(f"🔥 Leads Quentes (Presença Digital Comprovada): {quentes}")
    print(f"📱 Celulares com WhatsApp (Dígito 9): {celulares}")
    print(f"📸 Perfis de Instagram Localizados: {instagrams}")
    linha_separadora()


def fluxo_consulta_cnpj(cnpj: str):
    linha_separadora()
    print(f"[*] Consultando CNPJ: {cnpj}")
    linha_separadora()

    dados = consultar_cnpj(cnpj)
    if not dados:
        print("[!] CNPJ não encontrado ou inválido.")
        return

    print(f"[+] Razão / Nome: {dados['nome']}")
    print(f"[+] Decisor / Sócio: {dados['decisor_socio'] or 'X'}")
    print(f"[+] Celular / WhatsApp: {dados['celular_whatsapp'] or 'X'}")
    print(f"[+] Telefone Fixo: {dados['telefone_fixo'] or 'X'}")
    print(f"[+] E-mail: {dados['email'] or 'X'}")
    print(f"[+] Endereço: {dados['endereco'] or 'X'}")
    print(f"[+] Cidade: {dados['cidade'] or 'X'}")

    arquivo_csv = exportar_para_csv([dados], cidade=dados['cidade'], nicho="cnpj")
    print(f"\n[OK] Salvo em: {arquivo_csv}")
    linha_separadora()


def menu_interativo():
    linha_separadora()
    print("      PROSPECTADOR DE LEADS MULTI-FONTES & BAIRROS (CLI)")
    linha_separadora()
    print("1. Buscar comércios por Cidades ou Bairros")
    print("   Exemplos:")
    print("   - Campinas: Cambuí, Taquaral")
    print("   - DF: Asa Sul, Águas Claras")
    print("   - Campinas, Paulínia, Valinhos")
    print("2. Consultar empresa por CNPJ (com Sócios/QSA)")
    print("3. Sair")
    linha_separadora()

    opcao = input("Escolha uma opção (1, 2 ou 3): ").strip()

    if opcao == "1":
        entrada = input("Digite a cidade ou 'Cidade: Bairros': ").strip()
        if not entrada:
            print("[!] Localidade é obrigatória.")
            return
        nicho = input("Digite o nicho (ex: restaurante, clinica, academia): ").strip()
        if not nicho:
            nicho = "restaurante"
        limite_input = input("Limite por alvo (padrão 10): ").strip()
        limite = int(limite_input) if limite_input.isdigit() else 10

        fluxo_busca_comercios(entrada, nicho, limite)

    elif opcao == "2":
        cnpj = input("Digite o número do CNPJ: ").strip()
        if cnpj:
            fluxo_consulta_cnpj(cnpj)
        else:
            print("[!] CNPJ não informado.")

    elif opcao == "3":
        print("Encerrando.")
    else:
        print("[!] Opção inválida.")


def main():
    parser = argparse.ArgumentParser(description="Ferramenta multi-fontes de prospecção e enriquecimento de leads.")
    parser.add_argument("--cidade", type=str, help="Nome da cidade ou formato 'Cidade: Bairro1, Bairro2'")
    parser.add_argument("--nicho", type=str, help="Nicho de atuação (ex: restaurante, odontologia, academia)")
    parser.add_argument("--limite", type=int, default=10, help="Limite de busca por alvo (padrão 10)")
    parser.add_argument("--cnpj", type=str, help="Consultar dados cadastrais de um CNPJ")

    args = parser.parse_args()

    if args.cnpj:
        fluxo_consulta_cnpj(args.cnpj)
    elif args.cidade and args.nicho:
        fluxo_busca_comercios(args.cidade, args.nicho, args.limite)
    else:
        menu_interativo()


if __name__ == "__main__":
    main()
