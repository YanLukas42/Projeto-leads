"""
Módulo de exportação de leads para arquivo CSV.
Preenche valores ausentes com 'X' e salva no padrão universal RFC 4180 (vírgula com aspas),
garantindo compatibilidade perfeita com visualizadores de IDE (VS Code), Excel e Google Sheets.
Inclui coluna Bairro_Regiao para segmentação geográfica avançada.
"""

import csv
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


COLUNAS = [
    ("nome", "Nome"),
    ("status_lead", "Status_Lead"),
    ("celular_whatsapp", "Celular_WhatsApp"),
    ("telefone_fixo", "Telefone_Fixo"),
    ("decisor_socio", "Decisor_Socio"),
    ("email", "Email"),
    ("instagram", "Instagram"),
    ("site", "Site"),
    ("bairro_regiao", "Bairro_Regiao"),
    ("endereco", "Endereco"),
    ("cidade", "Cidade"),
    ("nicho", "Nicho"),
    ("fonte", "Fonte")
]


def sanitizar_nome_arquivo(texto: str) -> str:
    """Remove caracteres especiais para criar um nome de arquivo válido."""
    return re.sub(r'[^a-zA-Z0-9_-]', '_', texto.lower().strip())


def sanitizar_valor_campo(valor: Any) -> str:
    """Limpa quebras de linha e formata o valor do campo."""
    if valor is None:
        return "X"
    texto = str(valor).strip()
    if not texto or texto.lower() in ("none", "null"):
        return "X"
    texto = texto.replace("\r", " ").replace("\n", " ")
    return re.sub(r'\s+', ' ', texto)


def exportar_para_csv(leads: List[Dict[str, Any]], cidade: str = "", nicho: str = "", output_dir: Path = None) -> Path:
    """
    Exporta a lista de leads no formato CSV universal (delimitado por vírgula e com aspas).
    """
    if output_dir is None:
        output_dir = Path(__file__).resolve().parent.parent / "output"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_cidade = sanitizar_nome_arquivo(cidade) if cidade else "geral"
    nome_nicho = sanitizar_nome_arquivo(nicho) if nicho else "leads"
    
    nome_arquivo = f"leads_{nome_cidade}_{nome_nicho}_{timestamp}.csv"
    caminho_arquivo = output_dir / nome_arquivo

    with open(caminho_arquivo, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=",", quoting=csv.QUOTE_ALL)
        
        # Cabeçalho
        writer.writerow([label for _, label in COLUNAS])
        
        # Linhas
        for lead in leads:
            linha = [sanitizar_valor_campo(lead.get(chave)) for chave, _ in COLUNAS]
            writer.writerow(linha)

    return caminho_arquivo
