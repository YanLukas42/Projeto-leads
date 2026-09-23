"""
Módulo de Enriquecimento de Contatos para Criadores de Conteúdo.
Extrai E-mails, WhatsApps e perfis sociais a partir de descrições e árvores de links (Linktree, Beacons, etc.).
"""

import re
import urllib.parse
from typing import Dict, Any, List, Optional
import requests

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
WHATSAPP_REGEX = re.compile(r'(?:wa\.me|api\.whatsapp\.com\/send\?phone=)(\d+)')
LINKTREE_REGEX = re.compile(r'https?:\/\/(?:www\.)?(?:linktr\.ee|beacons\.ai|bento\.me)\/[a-zA-Z0-9._\-]+')
INSTA_REGEX = re.compile(r'https?:\/\/(?:www\.)?instagram\.com\/([a-zA-Z0-9._]+)')

EMAILS_IGNORADOS = {
    "contato@youtube.com", "suporte@youtube.com", "privacy@linktr.ee",
    "support@linktr.ee", "press@beacons.ai", "support@beacons.ai"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}


def extrair_emails_texto(texto: str) -> List[str]:
    """Extrai e-mails válidos de um texto descartando falsos positivos."""
    if not texto:
        return []
    encontrados = EMAIL_REGEX.findall(texto)
    validos = []
    for e in encontrados:
        e_clean = e.lower().strip(".")
        if e_clean not in EMAILS_IGNORADOS and not e_clean.endswith(".png") and not e_clean.endswith(".jpg"):
            if e_clean not in validos:
                validos.append(e_clean)
    return validos


def extrair_whatsapp_texto(texto: str) -> Optional[str]:
    """Identifica link wa.me ou número de WhatsApp brasileiro no texto."""
    if not texto:
        return None
    match = WHATSAPP_REGEX.search(texto)
    if match:
        num = match.group(1)
        if len(num) in (10, 11, 12, 13):
            return num
    
    # Procura formato (XX) 9XXXX-XXXX
    br_phone = re.search(r'(?:(?:\+|00)?55\s*)?(?:\(?([1-9]{2})\)?\s*)?(?:9\d{4})[-.\s]?(\d{4})', texto)
    if br_phone:
        nums = re.sub(r'\D', '', br_phone.group(0))
        if len(nums) in (10, 11, 12, 13):
            return nums
    return None


def resolver_agregador_links(url_agregador: str) -> Dict[str, str]:
    """
    Visita a página do Linktree / Beacons / Bento para coletar o WhatsApp e E-mail de contato comercial.
    """
    contatos = {"email": "", "whatsapp": "", "instagram": ""}
    try:
        resp = requests.get(url_agregador, headers=HEADERS, timeout=6)
        if resp.status_code != 200:
            return contatos
        
        conteudo = resp.text
        
        # WhatsApp no agregador
        wa_match = WHATSAPP_REGEX.search(conteudo)
        if wa_match:
            contatos["whatsapp"] = wa_match.group(1)
        
        # E-mails no agregador
        emails = extrair_emails_texto(conteudo)
        if emails:
            contatos["email"] = emails[0]
            
        # Instagram no agregador
        insta_match = INSTA_REGEX.search(conteudo)
        if insta_match:
            user = insta_match.group(1)
            if user not in ["p", "reel", "stories", "explore"]:
                contatos["instagram"] = f"https://instagram.com/{user}"

    except Exception:
        pass
    
    return contatos


def enriquecer_criador(dados_brutos: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processa a descrição e links do canal para extrair canais de contato acionáveis.
    """
    descricao = dados_brutos.get("descricao", "") or ""
    links_externos = dados_brutos.get("links", []) or []
    
    email_direto = ""
    whatsapp_direto = ""
    instagram_direto = ""
    linktree_url = ""

    # 1. Procura na descrição
    emails_desc = extrair_emails_texto(descricao)
    if emails_desc:
        email_direto = emails_desc[0]
    
    wa_desc = extrair_whatsapp_texto(descricao)
    if wa_desc:
        whatsapp_direto = wa_desc

    insta_desc = INSTA_REGEX.search(descricao)
    if insta_desc:
        user = insta_desc.group(1)
        if user not in ["p", "reel", "stories", "explore"]:
            instagram_direto = f"https://instagram.com/{user}"

    # 2. Varre links externos (aba Sobre ou descrição)
    for link in links_externos:
        if not link:
            continue
        if LINKTREE_REGEX.search(link):
            linktree_url = link
        elif INSTA_REGEX.search(link) and not instagram_direto:
            user = INSTA_REGEX.search(link).group(1)
            if user not in ["p", "reel", "stories"]:
                instagram_direto = f"https://instagram.com/{user}"
        elif "wa.me" in link or "whatsapp.com" in link:
            wa = extrair_whatsapp_texto(link)
            if wa and not whatsapp_direto:
                whatsapp_direto = wa

    # 3. Se tiver agregador e faltar email ou whatsapp, visita o agregador
    if linktree_url and (not email_direto or not whatsapp_direto):
        contatos_agg = resolver_agregador_links(linktree_url)
        if not email_direto and contatos_agg["email"]:
            email_direto = contatos_agg["email"]
        if not whatsapp_direto and contatos_agg["whatsapp"]:
            whatsapp_direto = contatos_agg["whatsapp"]
        if not instagram_direto and contatos_agg["instagram"]:
            instagram_direto = contatos_agg["instagram"]

    return {
        "email": email_direto or "X",
        "whatsapp": whatsapp_direto or "X",
        "instagram": instagram_direto or "X",
        "linktree": linktree_url or "X"
    }
