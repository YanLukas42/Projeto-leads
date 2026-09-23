"""
Módulo de enriquecimento de leads via scraping do site oficial do estabelecimento.
Localiza Instagram, WhatsApp, telefones classificados (Fixo vs Celular), e-mails
e calcula o nível de presença digital (Lead Quente vs Frio).
"""

import re
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from typing import Dict, Any

from core.cnpj import classificar_telefone


def _limpar_instagram(url: str) -> str:
    """Limpa e formata o link do perfil do Instagram."""
    if not url:
        return ""
    url_limpa = url.split("?")[0].rstrip("/")
    if any(ign in url_limpa.lower() for ign in ["/sharer", "/p/", "/stories/", "/explore"]):
        return ""
    return url_limpa


def enriquecer_lead_pelo_site(lead: Dict[str, Any]) -> Dict[str, Any]:
    """
    Acessa o site do lead (se houver), extrai Instagram, WhatsApp, e-mails,
    classifica telefones e atribui status de qualidade (Presença Digital).
    """
    site = lead.get("site", "").strip()
    
    # Classificar o telefone original se houver
    tel_original = lead.get("telefone_fixo", "") or lead.get("celular_whatsapp", "") or ""
    if tel_original:
        tipo, num = classificar_telefone(tel_original)
        if tipo == "CELULAR":
            lead["celular_whatsapp"] = num
            lead["telefone_fixo"] = ""
        elif tipo == "FIXO":
            lead["telefone_fixo"] = num
            lead["celular_whatsapp"] = ""

    # Se tiver site, raspar contatos adicionais
    if site and (site.startswith("http://") or site.startswith("https://")):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        try:
            req = urllib.request.Request(site, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
                soup = BeautifulSoup(html, "html.parser")

                # 1. Instagram
                if not lead.get("instagram"):
                    insta_links = [
                        a["href"] for a in soup.find_all("a", href=True)
                        if "instagram.com" in a["href"]
                    ]
                    for il in insta_links:
                        insta_formatado = _limpar_instagram(il)
                        if insta_formatado:
                            lead["instagram"] = insta_formatado
                            break

                # 2. WhatsApp
                if not lead.get("celular_whatsapp"):
                    wpp_links = [
                        a["href"] for a in soup.find_all("a", href=True)
                        if "wa.me" in a["href"] or "whatsapp.com" in a["href"] or "api.whatsapp.com" in a["href"]
                    ]
                    if wpp_links:
                        match = re.search(r'(?:phone=|wa\.me/|send\?phone=)?(\+?55\d{10,11}|\d{10,11})', wpp_links[0])
                        if match:
                            num_wpp = match.group(1).replace("+", "")
                            lead["celular_whatsapp"] = num_wpp

                # 3. E-mail
                if not lead.get("email"):
                    mailto_links = [
                        a["href"].replace("mailto:", "").split("?")[0].strip()
                        for a in soup.find_all("a", href=True)
                        if a["href"].startswith("mailto:")
                    ]
                    if mailto_links:
                        lead["email"] = mailto_links[0]
                    else:
                        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)
                        emails_validos = [
                            e for e in emails
                            if not any(ext in e.lower() for ext in [".png", ".jpg", ".svg", ".webp", "wixpress", "sentry", "example"])
                        ]
                        if emails_validos:
                            lead["email"] = emails_validos[0]

                # 4. Outros telefones no HTML
                if not lead.get("celular_whatsapp") and not lead.get("telefone_fixo"):
                    telefones_encontrados = re.findall(r'(?:\(?\d{2}\)?\s?)?(?:9\d{4}[-\s]?\d{4}|\d{4}[-\s]?\d{4})', html)
                    for t in telefones_encontrados:
                        tipo, num = classificar_telefone(t)
                        if tipo == "CELULAR" and not lead.get("celular_whatsapp"):
                            lead["celular_whatsapp"] = num
                        elif tipo == "FIXO" and not lead.get("telefone_fixo"):
                            lead["telefone_fixo"] = num

        except Exception:
            pass

    # Cálculo da Temperatura e Presença Digital
    has_site = bool(lead.get("site"))
    has_insta = bool(lead.get("instagram"))
    has_cel = bool(lead.get("celular_whatsapp"))
    has_email = bool(lead.get("email"))

    pontos = 0
    if has_site:
        pontos += 1
    if has_insta:
        pontos += 2  # Canal direto e visual
    if has_cel:
        pontos += 2  # WhatsApp é prioridade máxima
    if has_email:
        pontos += 1

    if pontos >= 3:
        lead["status_lead"] = "🔥 QUENTE (Alta Presença Digital)"
    elif pontos >= 2:
        lead["status_lead"] = "🔥 QUENTE (Canal Direto Ativo)"
    elif pontos == 1:
        lead["status_lead"] = "MORNO (Presença Moderada)"
    else:
        lead["status_lead"] = "FRIO (Sem Presença Digital)"

    return lead
