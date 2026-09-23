"""
Módulo de busca de estabelecimentos comerciais locais.
Utiliza geocodificação rápida de município ou bairro + Overpass BBox para alta performance.
"""

import json
import urllib.request
import urllib.parse
from typing import List, Dict, Any, Optional, Tuple

try:
    from core.cnpj import classificar_telefone
except ImportError:
    from .cnpj import classificar_telefone


NICHE_TAGS = {
    "restaurante": 'node["amenity"~"restaurant|food_court"]',
    "pizzaria": 'node["amenity"="restaurant"]["cuisine"~"pizza",i]',
    "padaria": 'node["shop"~"bakery|pastry"]',
    "bar": 'node["amenity"~"bar|pub"]',
    "cafe": 'node["amenity"="cafe"]',
    "farmacia": 'node["amenity"="pharmacy"]',
    "academia": 'node["leisure"="fitness_centre"]',
    "dentista": 'node["amenity"~"dentist|clinic"]',
    "odontologia": 'node["amenity"~"dentist|clinic"]',
    "clinica": 'node["amenity"="clinic"]',
    "hospital": 'node["amenity"="hospital"]',
    "petshop": 'node["shop"="pet"]',
    "veterinario": 'node["amenity"="veterinary"]',
    "salao": 'node["shop"="hairdresser|beauty"]',
    "barbearia": 'node["shop"="hairdresser"]',
    "estetica": 'node["shop"~"beauty|hairdresser|massage|spa"]',
    "oficina": 'node["shop"="car_repair"]',
    "loja": 'node["shop"]',
    "mercado": 'node["shop"~"supermarket|convenience"]',
    "hotel": 'node["tourism"="hotel"]',
    "buffet": 'node["amenity"~"restaurant|events_venue"]',
}


def obter_coordenadas_local(termo_busca: str) -> Optional[Tuple[str, str, str, str]]:
    """
    Obtém o Bounding Box (minlat, minlon, maxlat, maxlon) de uma cidade ou bairro via Nominatim.
    """
    termo_norm = termo_busca.strip().lower()
    
    # Tratamento especial para o Distrito Federal inteiro se não for um bairro específico
    if termo_norm in ("brasilia", "brasília", "distrito federal", "df"):
        return ("-16.0505", "-48.2857", "-15.5002", "-47.3083")

    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(termo_busca)}+Brazil&format=json&limit=1"
    headers = {"User-Agent": "LeadProspectorApp/1.0 (contact: support@leadprospector.local)"}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data and len(data) > 0:
                s, n, w, e = data[0]["boundingbox"]
                return (s, w, n, e)
    except Exception:
        pass
    return None


def _resolver_seletor_nicho(nicho: str) -> str:
    nicho_clean = nicho.strip().lower()
    for key, selector in NICHE_TAGS.items():
        if key in nicho_clean or nicho_clean in key:
            return selector
    return f'node["name"~"{nicho_clean}",i]'


def buscar_comercios_locais(cidade: str, nicho: str, limite: int = 30, bairro: str = "", termo_geo: str = "") -> List[Dict[str, Any]]:
    """
    Busca estabelecimentos comerciais em uma cidade ou bairro pelo nicho.
    """
    cidade_formatada = cidade.strip().title()
    bairro_formatado = bairro.strip().title() if bairro else ""
    termo_consulta = termo_geo if termo_geo else (f"{bairro_formatado}, {cidade_formatada}" if bairro_formatado else cidade_formatada)
    
    selector = _resolver_seletor_nicho(nicho)
    bbox = obter_coordenadas_local(termo_consulta)
    
    if bbox:
        s, w, n, e = bbox
        filtro_geo = f"({s},{w},{n},{e})"
        query = f"""
        [out:json][timeout:15];
        (
          {selector}{filtro_geo};
        );
        out {limite};
        """
    else:
        query = f"""
        [out:json][timeout:25];
        area["name"="{cidade_formatada}"]["admin_level"~"8|7|6|9|4"]->.searchArea;
        (
          {selector}(area.searchArea);
        );
        out {limite};
        """

    overpass_urls = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
    ]
    
    data = None
    for endpoint in overpass_urls:
        try:
            req = urllib.request.Request(
                endpoint,
                data=query.encode("utf-8"),
                headers={"User-Agent": "LeadProspectorApp/1.0"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data and "elements" in data and len(data["elements"]) > 0:
                    break
        except Exception:
            continue

    if not data or "elements" not in data:
        return []

    leads = []
    for elem in data.get("elements", []):
        tags = elem.get("tags", {})
        nome = tags.get("name")
        if not nome:
            continue
            
        telefone_bruto = (
            tags.get("phone")
            or tags.get("contact:phone")
            or tags.get("contact:mobile")
            or tags.get("contact:whatsapp")
            or ""
        )
        
        tipo_tel, num_formatado = classificar_telefone(telefone_bruto)
        celular = num_formatado if tipo_tel == "CELULAR" else ""
        fixo = num_formatado if tipo_tel == "FIXO" else (telefone_bruto if tipo_tel != "CELULAR" else "")

        site = (
            tags.get("website")
            or tags.get("contact:website")
            or tags.get("url")
            or ""
        )
        email = (
            tags.get("email")
            or tags.get("contact:email")
            or ""
        )
        
        rua = tags.get("addr:street", "")
        numero = tags.get("addr:housenumber", "")
        bairro_osm = tags.get("addr:suburb", "") or bairro_formatado
        endereco_partes = [p for p in [rua, numero, bairro_osm] if p]
        endereco = ", ".join(endereco_partes) if endereco_partes else ""

        leads.append({
            "nome": nome.strip(),
            "status_lead": "Pendente",
            "celular_whatsapp": celular,
            "telefone_fixo": fixo,
            "decisor_socio": "",
            "email": email.strip(),
            "instagram": "",
            "site": site.strip(),
            "bairro_regiao": bairro_osm or "Geral",
            "endereco": endereco,
            "cidade": cidade_formatada,
            "nicho": nicho.strip(),
            "fonte": "Base Comercial Local"
        })

    return leads
