"""
Módulo de controle de envios (Tracker).
Registra histórico de mensagens enviadas para evitar disparos duplicados
e controla a cota diária de segurança para proteção do chip.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


HISTORICO_FILE = Path(__file__).resolve().parent / "historico_envios.json"


def _carregar_historico() -> Dict[str, Any]:
    if not HISTORICO_FILE.exists():
        return {"envios": []}
    try:
        with open(HISTORICO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"envios": []}


def _salvar_historico(dados: Dict[str, Any]):
    with open(HISTORICO_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)


def foi_abordado(identificador: str) -> bool:
    """Verifica se o celular ou e-mail já recebeu abordagem anteriormente."""
    id_limpo = identificador.strip().lower()
    if not id_limpo or id_limpo == "x":
        return False

    dados = _carregar_historico()
    for item in dados.get("envios", []):
        if item.get("identificador", "").strip().lower() == id_limpo:
            return True
    return False


def total_envios_hoje(canal: str = "whatsapp") -> int:
    """Retorna o total de mensagens enviadas no dia atual para o canal."""
    hoje = datetime.now().strftime("%Y-%m-%d")
    dados = _carregar_historico()
    
    total = 0
    for item in dados.get("envios", []):
        if item.get("canal") == canal and item.get("data", "").startswith(hoje):
            total += 1
    return total


def registrar_envio(identificador: str, canal: str, nome: str, status: str = "enviado"):
    """Registra uma abordagem realizada com timestamp."""
    dados = _carregar_historico()
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    dados.setdefault("envios", []).append({
        "identificador": identificador.strip(),
        "canal": canal,
        "nome": nome.strip(),
        "data": agora,
        "status": status
    })
    _salvar_historico(dados)
