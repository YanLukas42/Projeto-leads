"""
Módulo de busca web de leads via perfis sociais (Instagram) e presenças comerciais indexadas.
Excelente fonte para capturar leads extremamente quentes e ativos em bairros e cidades.
"""

import re
import time
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from typing import List, Dict, Any

try:
    from core.cnpj import classificar_telefone
except ImportError:
    from .cnpj import classificar_telefone


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]


def _limpar_nome_empresa(titulo: str) -> str:
    if not titulo:
        return ""
    texto = re.sub(r'\(?@[\w\.-]+\)?', '', titulo)
    texto = re.sub(r'•\s*Instagram.*$', '', texto, flags=re.IGNORECASE)
    texto = re.sub(r'-\s*Instagram.*$', '', texto, flags=re.IGNORECASE)
    texto = re.sub(r'\|\s*Instagram.*$', '', texto, flags=re.IGNORECASE)
    texto = re.sub(r'See Instagram photos.*$', '', texto, flags=re.IGNORECASE)
    partes = re.split(r'[-–|•]', texto)
    nome = partes[0].strip() if partes else texto.strip()
    return re.sub(r'\s+', ' ', nome).strip()


def buscar_leads_web(cidade: str, nicho: str, limite: int = 15, bairro: str = "") -> List[Dict[str, Any]]:
    """
    Busca estabelecimentos ativos indexados com perfil de Instagram e contatos na cidade/bairro.
    """
    termo_local = f"{bairro} {cidade}" if bairro else cidade
    queries = [
        f"{nicho} {termo_local} site:instagram.com",
        f"{nicho} {termo_local} instagram"
    ]

    leads = []
    perfis_vistos = set()

    for idx, q in enumerate(queries):
        if len(leads) >= limite:
            break

        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(q)}"
        headers = {
            "User-Agent": USER_AGENTS[idx % len(USER_AGENTS)],
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"
        }

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
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

                    url_raw = url_elem.get_text(strip=True).lower()
                    if "instagram.com" not in url_raw:
                        continue

                    link_instagram = "https://" + url_raw.replace("https://", "").replace("http://", "").strip()
                    if any(ign in link_instagram for ign in ["/explore", "/tags", "/reels", "/p/", "/direct"]):
                        continue

                    if link_instagram in perfis_vistos:
                        continue
                    perfis_vistos.add(link_instagram)

                    titulo = title_elem.get_text(strip=True)
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                    nome = _limpar_nome_empresa(titulo)
                    if not nome or len(nome) < 2:
                        continue

                    telefones = re.findall(r'(?:\(?\d{2}\)?\s?)?(?:9\d{4}[-\s]?\d{4}|\d{4}[-\s]?\d{4})', snippet)
                    celular = ""
                    fixo = ""
                    for t in telefones:
                        tipo, num = classificar_telefone(t)
                        if tipo == "CELULAR" and not celular:
                            celular = num
                        elif tipo == "FIXO" and not fixo:
                            fixo = num

                    endereco = ""
                    match_end = re.search(r'(?:📍|Av\.|Avenida|Rua|R\.)\s*([^,]+,\s*\d+[^-\n\.]*)', snippet)
                    if match_end:
                        endereco = match_end.group(0).replace("📍", "").strip()

                    leads.append({
                        "nome": nome,
                        "status_lead": "QUENTE (Perfil Ativo no Instagram)",
                        "celular_whatsapp": celular,
                        "telefone_fixo": fixo,
                        "decisor_socio": "",
                        "email": "",
                        "instagram": link_instagram,
                        "site": "",
                        "bairro_regiao": bairro.title() if bairro else "Geral",
                        "endereco": endereco,
                        "cidade": cidade.strip().title(),
                        "nicho": nicho.strip(),
                        "fonte": "Busca Web / Instagram"
                    })

            time.sleep(0.4)
        except Exception:
            continue

    return leads
