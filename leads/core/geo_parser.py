"""
Módulo de interpretação de múltiplas cidades e bairros.
Suporta formatos flexíveis:
- 'Campinas: Cambuí, Taquaral'
- 'DF: Asa Sul, Águas Claras'
- 'Campinas, Paulínia, Valinhos'
- 'São Paulo'
"""

import re
from typing import List, Dict


def interpretar_locais(entrada_usuario: str) -> List[Dict[str, str]]:
    """
    Interpreta a string de entrada e retorna uma lista estruturada de alvos de busca.
    Retorna lista de dicionários:
    [
        {
            "cidade": "Campinas",
            "bairro": "Cambuí",
            "termo_busca": "Cambuí, Campinas",
            "rotulo": "Cambuí (Campinas)"
        },
        ...
    ]
    """
    texto = entrada_usuario.strip()
    if not texto:
        return []

    # Caso 1: Sintaxe com dois-pontos -> Cidade: Bairro1, Bairro2...
    if ":" in texto:
        partes = texto.split(":", 1)
        cidade_base = partes[0].strip()
        bairros_str = partes[1].strip()
        
        # Ajuste de DF / Brasília
        cidade_normalizada = cidade_base
        if cidade_base.lower() in ("df", "distrito federal"):
            cidade_normalizada = "Brasília"

        bairros = [b.strip() for b in re.split(r'[,;]', bairros_str) if b.strip()]
        if not bairros:
            return [{
                "cidade": cidade_normalizada,
                "bairro": "",
                "termo_busca": cidade_normalizada,
                "rotulo": cidade_normalizada
            }]

        resultados = []
        for b in bairros:
            # Termo para o geocodificador Nominatim
            if cidade_normalizada == "Brasília" and b.lower() in ("águas claras", "aguas claras", "taguatinga", "guará", "guara", "ceilândia", "ceilandia"):
                termo_busca = f"{b}, Distrito Federal"
            else:
                termo_busca = f"{b}, {cidade_normalizada}"
                
            resultados.append({
                "cidade": cidade_normalizada,
                "bairro": b.title(),
                "termo_busca": termo_busca,
                "rotulo": f"{b.title()} ({cidade_normalizada})"
            })
        return resultados

    # Caso 2: Múltiplas cidades ou termos separados por vírgula ou ponto e vírgula
    itens = [item.strip() for item in re.split(r'[,;]', texto) if item.strip()]
    resultados = []
    for item in itens:
        cidade_nome = item.title()
        if item.lower() in ("df", "distrito federal"):
            cidade_nome = "Brasília"
            
        resultados.append({
            "cidade": cidade_nome,
            "bairro": "",
            "termo_busca": cidade_nome,
            "rotulo": cidade_nome
        })

    return resultados
