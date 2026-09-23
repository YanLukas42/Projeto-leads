"""
Módulo de deduplicação e consolidação inteligente de leads multi-fontes.
Cruza dados pelo nome normalizado, telefone celular ou redes sociais,
fundindo informações complementares em um único lead completo.
"""

import re
import unicodedata
from typing import List, Dict, Any


def normalizar_texto(texto: str) -> str:
    """Remove acentos, caracteres especiais e espaços excessivos."""
    if not texto:
        return ""
    # Remove acentos
    nfkd = unicodedata.normalize('NFKD', texto)
    sem_acento = "".join([c for c in nfkd if not unicodedata.combining(c)])
    # Mantém apenas letras e números
    limpo = re.sub(r'[^a-zA-Z0-9\s]', '', sem_acento.lower())
    # Remove stopwords comuns de nomes comerciais
    stopwords = ["restaurante", "pizzaria", "bar", "buffet", "loja", "ltda", "me", "epp", "eireli", "comercio", "do", "da", "de"]
    palavras = [p for p in limpo.split() if p not in stopwords]
    return " ".join(palavras) if palavras else limpo.strip()


def consolidar_leads(listas_de_leads: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Funde múltiplos lotes de leads sem duplicar registros,
    combinando campos preenchidos de diferentes fontes.
    """
    leads_consolidados = []
    # Dicionário de índices: chave_normalizada -> índice em leads_consolidados
    indices_por_nome = {}
    indices_por_celular = {}
    indices_por_instagram = {}

    for lote in listas_de_leads:
        for lead in lote:
            nome = lead.get("nome", "").strip()
            if not nome:
                continue

            nome_norm = normalizar_texto(nome)
            celular = lead.get("celular_whatsapp", "").strip()
            instagram = lead.get("instagram", "").strip().lower()

            # Verificar se já existe correspondência
            idx_existente = None
            if celular and celular in indices_por_celular:
                idx_existente = indices_por_celular[celular]
            elif instagram and instagram in indices_por_instagram:
                idx_existente = indices_por_instagram[instagram]
            elif nome_norm and nome_norm in indices_por_nome:
                idx_existente = indices_por_nome[nome_norm]

            if idx_existente is not None:
                # Fundir com o lead já existente
                alvo = leads_consolidados[idx_existente]

                # Preencher campos que estejam vazios no alvo
                for campo in ["celular_whatsapp", "telefone_fixo", "decisor_socio", "email", "instagram", "site", "endereco"]:
                    if not alvo.get(campo) and lead.get(campo):
                        alvo[campo] = lead[campo]

                # Atualizar fonte combinada
                fonte_atual = alvo.get("fonte", "")
                nova_fonte = lead.get("fonte", "")
                if nova_fonte and nova_fonte not in fonte_atual:
                    alvo["fonte"] = f"{fonte_atual} + {nova_fonte}"

                # Elevar status para Quente Multi-Fontes
                alvo["status_lead"] = "🔥 QUENTE (Validado Multi-Fontes)"

            else:
                # Lead novo
                novo_idx = len(leads_consolidados)
                leads_consolidados.append(dict(lead))

                if nome_norm:
                    indices_por_nome[nome_norm] = novo_idx
                if celular:
                    indices_por_celular[celular] = novo_idx
                if instagram:
                    indices_por_instagram[instagram] = novo_idx

    return leads_consolidados
