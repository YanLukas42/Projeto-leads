"""
Módulo de consulta de dados oficiais de empresas por CNPJ.
Utiliza APIs públicas gratuitas (BrasilAPI e MinhaReceita) como fallback.
Extrai dados cadastrais, telefones classificados (Fixo vs Celular) e Quadro de Sócios (QSA).
"""

import re
import json
import urllib.request
from typing import Dict, Any, Optional, List, Tuple


def limpar_digitos(texto: str) -> str:
    """Remove caracteres não numéricos."""
    return re.sub(r'\D', '', texto or "")


def classificar_telefone(numero_bruto: str) -> Tuple[str, str]:
    """
    Classifica se o telefone é Celular (com dígito 9) ou Fixo.
    Retorna (tipo, numero_formatado):
    - tipo: 'CELULAR' ou 'FIXO' ou 'DESCONHECIDO'
    """
    digitos = limpar_digitos(numero_bruto)
    
    # Remover código do país 55 se presente no início
    if len(digitos) in (12, 13) and digitos.startswith("55"):
        digitos = digitos[2:]

    # Celular com DDD: 11 dígitos (ex: 19 99145-2802) e o 3º dígito é 9
    if len(digitos) == 11 and digitos[2] == '9':
        return "CELULAR", digitos

    # Celular sem DDD: 9 dígitos e começa com 9
    if len(digitos) == 9 and digitos[0] == '9':
        return "CELULAR", digitos

    # Fixo com DDD: 10 dígitos (ex: 19 3289-5369) e o 3º dígito é 2, 3, 4 ou 5
    if len(digitos) == 10 and digitos[2] in '2345':
        return "FIXO", digitos

    # Fixo sem DDD: 8 dígitos e começa com 2, 3, 4 ou 5
    if len(digitos) == 8 and digitos[0] in '2345':
        return "FIXO", digitos

    return "DESCONHECIDO", digitos if digitos else numero_bruto


def extrair_decisores_qsa(qsa_lista: List[Dict[str, Any]]) -> str:
    """
    Identifica os sócios-administradores ou diretores prioritariamente.
    """
    if not qsa_lista:
        return ""

    administradores = []
    socios_gerais = []

    for membro in qsa_lista:
        nome = membro.get("nome_socio") or membro.get("nome") or ""
        qualificacao = (membro.get("qualificacao_socio") or membro.get("qualificacao") or "").lower()
        
        if not nome:
            continue
            
        nome_formatado = nome.strip().title()
        
        # Priorizar sócios administradores ou diretores
        if any(cargo in qualificacao for cargo in ["administrador", "diretor", "presidente", "gerente"]):
            administradores.append(f"{nome_formatado} ({qualificacao.title()})")
        else:
            socios_gerais.append(nome_formatado)

    if administradores:
        return "; ".join(administradores[:2])
    elif socios_gerais:
        return "; ".join(socios_gerais[:2])
    return ""


def consultar_cnpj(cnpj: str) -> Optional[Dict[str, Any]]:
    """
    Consulta os dados de um CNPJ nas bases públicas abertas.
    """
    cnpj_limpo = limpar_digitos(cnpj)
    if len(cnpj_limpo) != 14:
        return None

    endpoints = [
        f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}",
        f"https://minhareceita.org/{cnpj_limpo}",
        f"https://publica.cnpj.ws/cnpj/{cnpj_limpo}"
    ]

    for url in endpoints:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                
                nome = data.get("nome_fantasia") or data.get("razao_social") or ""
                tel_bruto = data.get("ddd_telefone_1") or data.get("telefone") or ""
                email = data.get("email") or ""
                logradouro = data.get("logradouro") or ""
                numero = data.get("numero") or ""
                bairro = data.get("bairro") or ""
                municipio = data.get("municipio") or ""
                uf = data.get("uf") or ""
                cep = data.get("cep") or ""
                
                # Classificar telefone
                tipo_tel, num_limpo = classificar_telefone(tel_bruto)
                celular_wpp = num_limpo if tipo_tel == "CELULAR" else ""
                fixo = num_limpo if tipo_tel == "FIXO" else (tel_bruto if tipo_tel != "CELULAR" else "")

                # Extrair decisores do QSA
                qsa = data.get("qsa") or []
                decisor = extrair_decisores_qsa(qsa)

                endereco_parts = [p for p in [logradouro, numero, bairro, cep] if p]
                endereco = ", ".join(endereco_parts)
                cidade_str = f"{municipio} - {uf}" if uf else municipio

                return {
                    "nome": nome.strip(),
                    "status_lead": "CNPJ Cadastrado",
                    "celular_whatsapp": celular_wpp,
                    "telefone_fixo": fixo,
                    "decisor_socio": decisor,
                    "email": email.strip().lower(),
                    "instagram": "",
                    "site": "",
                    "endereco": endereco,
                    "cidade": cidade_str,
                    "nicho": data.get("cnae_fiscal_descricao", "Empresa"),
                    "fonte": "Base Oficial CNPJ"
                }
        except Exception:
            continue

    return None
