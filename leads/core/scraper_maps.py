"""
Módulo de extração de fichas e presenças locais em mapas comerciais.
Identifica locais com avaliações públicas, telefones e endereços no ecossistema de mapas.
Filtra agregadores genéricos (ex: apontador, listamais) para focar apenas em comércios reais.
"""

import re
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from typing import List, Dict, Any

try:
    from core.cnpj import classificar_telefone
except ImportError:
    from .cnpj import classificar_telefone


AGREGADORES_IGNORADOS = [
    "tripadvisor", "wikipedia", "youtube", "facebook.com/public",
    "apontador.com", "listamais.com", "guiamais.com", "solutudo.com",
    "campinasguialocal.com", "onelinkweb.com", "telelistas.net", "clube.",
    "sympla.com", "ifood.com.br/restaurantes", "encontrecampinas.com"
]


def buscar_leads_mapas(cidade: str, nicho: str, limite: int = 15) -> List[Dict[str, Any]]:
    """
    Busca fichas comerciais indexadas de mapas e guias para a cidade e nicho,
    descartando agregadores genéricos.
    """
    query = f"{nicho} em {cidade} maps avaliacoes telefone"
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"
    }

    leads = []
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            soup = BeautifulSoup(resp.read().decode("utf-8", errors="ignore"), "html.parser")
            resultados = soup.find_all("div", class_="result")

            for r in resultados:
                if len(leads) >= limite:
                    break

                title_elem = r.find("a", class_="result__a")
                snippet_elem = r.find("a", class_="result__snippet")
                url_elem = r.find("a", class_="result__url")

                if not title_elem or not url_elem:
                    continue

                titulo = title_elem.get_text(strip=True)
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                url_link = url_elem.get_text(strip=True).lower()

                # Ignorar agregadores e portais
                if any(agr in url_link for agr in AGREGADORES_IGNORADOS):
                    continue

                # Limpar nome comercial
                partes = re.split(r'[-–|•]', titulo)
                nome = partes[0].strip() if partes else titulo.strip()
                if any(ign in nome.lower() for ign in ["melhores", "onde comer", "guia de", "top 10", "encontre", "restaurantes em"]):
                    continue

                if len(nome) < 3:
                    continue

                # Telefones
                telefones = re.findall(r'(?:\(?\d{2}\)?\s?)?(?:9\d{4}[-\s]?\d{4}|\d{4}[-\s]?\d{4})', snippet)
                celular = ""
                fixo = ""
                for t in telefones:
                    tipo, num = classificar_telefone(t)
                    if tipo == "CELULAR" and not celular:
                        celular = num
                    elif tipo == "FIXO" and not fixo:
                        fixo = num

                site_url = ""
                if not any(soc in url_link for soc in ["google.", "instagram.", "facebook.", "maps"]):
                    site_url = "https://" + url_link.replace("https://", "").replace("http://", "").strip()

                leads.append({
                    "nome": nome,
                    "status_lead": "QUENTE (Ficha de Mapa / Ativo)",
                    "celular_whatsapp": celular,
                    "telefone_fixo": fixo,
                    "decisor_socio": "",
                    "email": "",
                    "instagram": "",
                    "site": site_url,
                    "endereco": "",
                    "cidade": cidade.strip().title(),
                    "nicho": nicho.strip(),
                    "fonte": "Fichas de Mapa"
                })

    except Exception:
        pass

    return leads
