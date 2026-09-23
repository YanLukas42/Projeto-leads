"""
Configurações da vertente de Mineração e Abordagem de Influenciadores / Criadores de Conteúdo.
Foco: Criadores entre 10.000 e 50.000 inscritos/seguidores para parcerias e publi de Aulas de Inglês.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Dados do Remetente / Negócio
REMETENTE_NOME = os.getenv("REMETENTE_NOME", "Lukas Willian")
REMETENTE_EMAIL = os.getenv("SMTP_USER", "")
EMPRESA_LINGUAS = os.getenv("EMPRESA_LINGUAS", "Vanguard Idiomas")
REMETENTE_CARGO = "Parcerias & Expansão"
PRODUTO_SERVICO = "aulas práticas e mentoria particular de inglês"

# Parâmetros de Filtro de Criadores
MIN_INSCRITOS_PADRAO = 10_000
MAX_INSCRITOS_PADRAO = 50_000

# Pastas de saída
OUTPUT_DIR = BASE_DIR / "influencers" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TRACKER_FILE = BASE_DIR / "influencers" / "historico_influencers.json"
LOG_FILE = BASE_DIR / "influencers" / "campanha_influencers.log"
