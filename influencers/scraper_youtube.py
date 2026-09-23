"""
Módulo de Mineração de Canais do YouTube para Influenciadores (10k a 50k inscritos).
Suporta busca interna web do YouTube, extração de metadados em alta velocidade e fallback com yt-dlp.
"""

import sys
import json
import subprocess
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import requests

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from influencers.config import MIN_INSCRITOS_PADRAO, MAX_INSCRITOS_PADRAO
from influencers.enricher_social import enriquecer_criador

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
}


def parse_inscritos_texto(texto: str) -> Optional[int]:
    """Converte '15,4 mil inscritos' ou '25K subscribers' em inteiro numérico."""
    if not texto:
        return None
    t = texto.lower().replace("\xa0", " ").replace(",", ".").replace(" ", "")
    
    # Exemplo: 15.4k ou 15.4mil
    match_k = re.search(r'([\d.]+)(?:k|mil)', t)
    if match_k:
        try:
            return int(float(match_k.group(1)) * 1000)
        except ValueError:
            return None
            
    match_mi = re.search(r'([\d.]+)(?:mi|m|milhões|milhoes)', t)
    if match_mi:
        try:
            return int(float(match_mi.group(1)) * 1_000_000)
        except ValueError:
            return None

    # Exemplo: número direto 15400
    match_num = re.search(r'\d+', t)
    if match_num:
        try:
            return int(match_num.group(0))
        except ValueError:
            return None
            
    return None


def obter_metadados_canal(url_canal: str) -> Dict[str, Any]:
    """
    Extrai o título, descrição completa e links do canal via endpoint About/Browse do YouTube.
    """
    try:
        resp = requests.get(url_canal, headers=HEADERS, timeout=6)
        if resp.status_code == 200:
            m = re.search(r'ytInitialData\s*=\s*({.+?});', resp.text)
            if m:
                data = json.loads(m.group(1))
                
                # Extrair token da aba Sobre se existir
                content = data.get("header", {}).get("pageHeaderRenderer", {}).get("content", {})
                page_header = content.get("pageHeaderViewModel", {})
                desc_obj = page_header.get("description", {}).get("descriptionPreviewViewModel", {})
                
                descricao = ""
                links_relevantes = []
                
                # Tentar chamar endpoint continuation da aba Sobre
                try:
                    on_tap = desc_obj.get("rendererContext", {}).get("commandContext", {}).get("onTap", {})
                    token = (on_tap.get("innertubeCommand", {})
                                   .get("showEngagementPanelEndpoint", {})
                                   .get("engagementPanel", {})
                                   .get("engagementPanelSectionListRenderer", {})
                                   .get("content", {})
                                   .get("sectionListRenderer", {})
                                   .get("contents", [{}])[0]
                                   .get("itemSectionRenderer", {})
                                   .get("contents", [{}])[0]
                                   .get("continuationItemRenderer", {})
                                   .get("continuationEndpoint", {})
                                   .get("continuationCommand", {})
                                   .get("token"))
                    
                    if token:
                        api_url = "https://www.youtube.com/youtubei/v1/browse"
                        payload = {
                            "continuation": token,
                            "context": {"client": {"clientName": "WEB", "clientVersion": "2.20240409.00.00"}}
                        }
                        r_about = requests.post(api_url, json=payload, headers=HEADERS, timeout=6)
                        if r_about.status_code == 200:
                            about_data = r_about.json()
                            endpoints = about_data.get("onResponseReceivedEndpoints", [])
                            if endpoints:
                                vm = endpoints[0].get("appendContinuationItemsAction", {}).get("continuationItems", [{}])[0].get("aboutChannelRenderer", {}).get("metadata", {}).get("aboutChannelViewModel", {})
                                descricao = vm.get("description", "")
                                for l_item in vm.get("links", []):
                                    ext = l_item.get("channelExternalLinkViewModel", {})
                                    l_content = ext.get("link", {}).get("content", "")
                                    if l_content:
                                        if not l_content.startswith("http"):
                                            l_content = f"https://{l_content}"
                                        links_relevantes.append(l_content)
                except Exception:
                    pass

                # Se não pegou pela aba sobre, faz fallback básico
                if not descricao:
                    meta = data.get("metadata", {}).get("channelMetadataRenderer", {})
                    descricao = meta.get("description", "")
                
                if not links_relevantes:
                    links_html = re.findall(r'https?:\/\/[a-zA-Z0-9.\-_/]+', resp.text)
                    links_relevantes = [
                        l for l in set(links_html) 
                        if any(d in l.lower() for d in ["instagram.com", "linktr.ee", "beacons.ai", "wa.me"])
                    ]

                return {
                    "nome": page_header.get("title", {}).get("dynamicTextViewModel", {}).get("text", {}).get("content", ""),
                    "url": url_canal,
                    "descricao": descricao,
                    "links": links_relevantes
                }
    except Exception:
        pass

    # Fallback via yt-dlp
    cmd = ["yt-dlp", "--dump-json", "--flat-playlist", "--playlist-items", "1", url_canal]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15)
        if proc.returncode == 0 and proc.stdout.strip():
            primeira_linha = proc.stdout.strip().split("\n")[0]
            dados = json.loads(primeira_linha)
            return {
                "nome": dados.get("channel") or dados.get("uploader") or "",
                "url": dados.get("channel_url") or url_canal,
                "descricao": dados.get("description") or "",
                "links": [url_canal]
            }
    except Exception:
        pass

    return {"nome": "", "url": url_canal, "descricao": "", "links": []}


def buscar_canais_youtube_busca(termo: str, limite: int = 40) -> List[Dict[str, Any]]:
    """
    Busca canais no YouTube usando busca com filtro de canais (sp=EgIQAg%253D%253D).
    """
    url_busca = f"https://www.youtube.com/results?search_query={requests.utils.quote(termo)}&sp=EgIQAg%253D%253D"
    canais_encontrados = []

    try:
        resp = requests.get(url_busca, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            m = re.search(r'ytInitialData\s*=\s*({.+?});', resp.text)
            if m:
                data = json.loads(m.group(1))
                contents = (data.get("contents", {})
                            .get("twoColumnSearchResultsRenderer", {})
                            .get("primaryContents", {})
                            .get("sectionListRenderer", {})
                            .get("contents", []))
                
                for section in contents:
                    items = section.get("itemSectionRenderer", {}).get("contents", [])
                    for item in items:
                        if "channelRenderer" in item:
                            c = item["channelRenderer"]
                            titulo = c.get("title", {}).get("simpleText", "")
                            channel_id = c.get("channelId", "")
                            
                            inscritos_obj = c.get("videoCountText") or c.get("subscriberCountText") or {}
                            inscritos_txt = ""
                            if isinstance(inscritos_obj, dict):
                                inscritos_txt = inscritos_obj.get("simpleText") or inscritos_obj.get("accessibility", {}).get("accessibilityData", {}).get("label", "")
                            
                            inscritos_num = parse_inscritos_texto(inscritos_txt)
                            
                            handle = ""
                            sub_text = c.get("subscriberCountText", {})
                            if isinstance(sub_text, dict) and sub_text.get("simpleText", "").startswith("@"):
                                handle = sub_text.get("simpleText")
                            
                            canal_url = f"https://www.youtube.com/{handle}" if handle else f"https://www.youtube.com/channel/{channel_id}"
                            
                            canais_encontrados.append({
                                "nome": titulo,
                                "url": canal_url,
                                "inscritos_texto": inscritos_txt.replace("\xa0", " "),
                                "inscritos_num": inscritos_num
                            })
                            if len(canais_encontrados) >= limite:
                                break
    except Exception as err:
        print(f"Erro na busca de canais: {err}")

    return canais_encontrados


def minerar_influenciadores(
    termo_busca: str,
    nicho: str = "Geral",
    min_inscritos: int = MIN_INSCRITOS_PADRAO,
    max_inscritos: int = MAX_INSCRITOS_PADRAO,
    limite: int = 15
) -> List[Dict[str, Any]]:
    """
    Minera canais pelo termo, filtra pela faixa de inscritos (10k a 50k) e enriquece os contatos.
    """
    print(f"\n🔍 Buscando canais para: '{termo_busca}' (Filtro: {min_inscritos:,} a {max_inscritos:,} inscritos)...")
    brutos = buscar_canais_youtube_busca(termo_busca, limite=50)
    print(f"  -> {len(brutos)} canais localizados na busca inicial.")
    
    resultados_qualificados = []
    
    for canal in brutos:
        inscritos = canal.get("inscritos_num")
        nome = canal.get("nome", "")
        url = canal.get("url", "")
        inscritos_txt = canal.get("inscritos_texto", "N/D")
        
        # Filtro da faixa de 10k a 50k
        if inscritos:
            if inscritos < min_inscritos or inscritos > max_inscritos:
                continue
        else:
            continue
                
        print(f"  🎯 Qualificado: {nome} ({inscritos_txt}) -> Coletando contatos...")
        meta = obter_metadados_canal(url)
        descricao = meta.get("descricao", "")
        links = meta.get("links", [])
        
        contatos = enriquecer_criador({
            "descricao": descricao,
            "links": links
        })
        
        tem_contato = (contatos["email"] != "X" or contatos["whatsapp"] != "X" or contatos["instagram"] != "X")
        status_contato = "🔥 COM CONTATO" if tem_contato else "⚠️ SEM CONTATO DIRETO"
        
        lead_influencer = {
            "Canal": nome,
            "Nicho": nicho,
            "Inscritos": inscritos_txt,
            "Email": contatos["email"],
            "WhatsApp": contatos["whatsapp"],
            "Instagram": contatos["instagram"],
            "Linktree": contatos["linktree"],
            "URL_Canal": url,
            "Status": status_contato
        }
        
        resultados_qualificados.append(lead_influencer)
        if len(resultados_qualificados) >= limite:
            break
            
    print(f"✅ Concluído: {len(resultados_qualificados)} canais qualificados e enriquecidos na faixa alvo!")
    return resultados_qualificados
