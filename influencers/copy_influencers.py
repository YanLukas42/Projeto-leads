"""
Módulo de geração de copys personalizadas para criadores de conteúdo (10k a 50k).
Foco: Fechar parcerias comerciais / publis / menções para venda de Aulas de Inglês.
Linguagem direta, humana e orientada a conversão (baixo atrito).
"""

import random
from typing import Dict, Any

from influencers.config import REMETENTE_NOME, PRODUTO_SERVICO


PALAVRAS_CANAL_TEMATICO = {
    "canal", "dicas", "escola", "mundo", "portal", "fala", "universo", "central",
    "usando", "aprendendo", "programando", "programação", "programacao", "programador",
    "curso", "cursos", "tutoriais", "tutorial", "games", "jogos", "gamer", "review",
    "estudos", "concurso", "concursos", "viagens", "viagem", "manual", "manualdomundo",
    "tech", "dev", "desenvolvimento", "código", "codigo", "computação", "computacao",
    "nação", "nacao", "clube", "hora", "diário", "diario", "guia", "estúdio", "estudio",
    "lab", "laboratório", "laboratorio", "hub", "station", "espaço", "espaco", "tv"
}


def extrair_primeiro_nome_criador(nome_canal: str) -> str:
    """Extrai um primeiro nome se o canal for pessoal. Caso contrário, usa 'pessoal'."""
    if not nome_canal or nome_canal == "X":
        return "pessoal"
    partes = nome_canal.split()
    if not partes:
        return "pessoal"
    primeiro = partes[0].strip()
    primeiro_lower = primeiro.lower()
    
    # Se o nome for gerúndio (ex: Usando, Programando, Criando)
    if any(primeiro_lower.endswith(s) for s in ["ando", "endo", "indo"]):
        return "pessoal"
        
    if primeiro_lower in PALAVRAS_CANAL_TEMATICO or len(primeiro) <= 2:
        return "pessoal"
        
    # Se qualquer parte do nome contiver termos de canal coletivo, prefere 'pessoal'
    partes_lower = [p.lower() for p in partes]
    if any(t in partes_lower for t in ["indie", "games", "studios", "tv", "brasil", "channel", "produções"]):
        return "pessoal"
        
    return primeiro.capitalize()


from influencers.config import REMETENTE_NOME, REMETENTE_CARGO, EMPRESA_LINGUAS, PRODUTO_SERVICO


# =====================================================================
# FRAMEWORKS DE E-MAIL PARA INFLUENCIADORES (FIXO + COMISSÃO SOBRE LUCRO)
# =====================================================================

def _copy_email_fixo_mais_comissao_1(nome: str, canal: str, nicho: str) -> Dict[str, str]:
    """Modelo 1: Parceria Híbrida Direta (Fixo Garantido + % Lucro)"""
    assunto = f"Parceria comercial para o {canal} (Fixo + Comissão)"
    corpo = f"""Fala {nome}, tudo bem?

Meu nome é {REMETENTE_NOME}, represento a {EMPRESA_LINGUAS} ({REMETENTE_CARGO}) e acompanho com atenção a qualidade do conteúdo que você produz no {canal} sobre {nicho}.

Estamos selecionando alguns criadores com audiência engajada para um modelo de parceria diferente do tradicional: oferecemos um **valor fixo por divulgação** mais uma **participação percentual (comissão) sobre o lucro** de cada novo aluno matriculado através do seu canal.

Dessa forma, você garante uma receita imediata e constrói uma renda recorrente com o crescimento da campanha.

Você teria abertura para avaliarmos uma ação teste no {canal} neste mês? Se tiver um mídia kit ou preferir alinhar pelo WhatsApp comercial, me avisa por aqui!

Um abraço,
{REMETENTE_NOME}
{EMPRESA_LINGUAS}"""
    return {"assunto": assunto, "corpo": corpo}


def _copy_email_fixo_mais_comissao_2(nome: str, canal: str, nicho: str) -> Dict[str, str]:
    """Modelo 2: Foco em Monetização da Audiência de Idiomas (Low-Friction)"""
    assunto = f"Proposta de patrocínio / publi no {canal}"
    corpo = f"""Oi {nome}, tudo certo?

Passando rápido porque vejo um potencial enorme de monetização na audiência do {canal}.

Sou representante da {EMPRESA_LINGUAS} e atuamos com {PRODUTO_SERVICO}, uma solução prática que conecta muito com quem te acompanha.

Queremos patrocinar vídeos no seu canal trabalhando com um formato híbrido bem vantajoso: **pagamento fixo garantido por menção/inserção + comissão agressiva sobre as matrículas**.

Como funciona a sua contratação de publicidade hoje? Você tem uma tabela de valores base para inserções no início do vídeo ou shorts?

Se fizer sentido, podemos trocar 2 minutos de ideia sem compromisso.

Valeu!
{REMETENTE_NOME}
{REMETENTE_CARGO} | {EMPRESA_LINGUAS}"""
    return {"assunto": assunto, "corpo": corpo}


def _copy_email_fixo_mais_comissao_3(nome: str, canal: str, nicho: str) -> Dict[str, str]:
    """Modelo 3: Consulta Rápida de Mídia Kit + Apresentação da Parceria"""
    assunto = f"{canal} + {EMPRESA_LINGUAS}: proposta de parceria"
    corpo = f"""Olá {nome}, tudo bem por aí?

Aqui é o {REMETENTE_NOME}, da área de {REMETENTE_CARGO} da {EMPRESA_LINGUAS}.

Estamos mapeando canais com audiência qualificada para divulgar nossos programas de {PRODUTO_SERVICO}. 

Temos verba aprovada para fechar ações neste mês e gostamos de trabalhar com **investimento fixo na divulgação somado a comissão sobre as vendas**, alinhando os incentivos para você lucrar alto com a gente.

Você teria disponibilidade na sua grade para uma inserção patrocinada nas próximas semanas? 

Se puder me enviar sua média de valores ou seu contato de WhatsApp comercial para alinharmos os detalhes, seria ótimo.

Abraços,
{REMETENTE_NOME}"""
    return {"assunto": assunto, "corpo": corpo}


def gerar_email_influencer(lead: Dict[str, Any]) -> Dict[str, str]:
    """Seleciona dinamicamente a melhor copy de e-mail para o criador."""
    canal = lead.get("Canal") or lead.get("Nome") or "seu canal"
    nicho = lead.get("Nicho") or "seus temas"
    nome = extrair_primeiro_nome_criador(canal)

    modelos = [
        _copy_email_fixo_mais_comissao_1,
        _copy_email_fixo_mais_comissao_2,
        _copy_email_fixo_mais_comissao_3
    ]
    escolhido = random.choice(modelos)
    return escolhido(nome, canal, nicho)


# =====================================================================
# FRAMEWORKS DE WHATSAPP / DIRECT
# =====================================================================

def gerar_whatsapp_influencer(lead: Dict[str, Any]) -> str:
    """Gera mensagem curta e direta para WhatsApp comercial de criadores."""
    canal = lead.get("Canal") or lead.get("Nome") or "seu canal"
    nicho = lead.get("Nicho") or "seus temas"
    nome = extrair_primeiro_nome_criador(canal)

    variacoes = [
        f"""Fala {nome}, tudo bem? Aqui é o {REMETENTE_NOME}.

Acompanho seus vídeos no {canal} e achei muito massa o trabalho! 

Estou fechando algumas ações de patrocínio para o nosso projeto de {PRODUTO_SERVICO} neste mês e gostaria de saber se você tem valores fechados para menção em vídeo ou publi rápida no Reels/Shorts.

Você tem um mídia kit ou tabela de valores que possa me mandar por aqui?

Valeu!""",

        f"""Oi {nome}, tudo certo? {REMETENTE_NOME} aqui.

Curto bastante a linha de conteúdo do {canal}! Temos uma escola/mentoria de {PRODUTO_SERVICO} e queríamos fechar uma parceria comercial com você para as próximas semanas.

Você teria espaço na grade do canal para uma inserção patrocinada? Se puder me passar como funcionam seus valores e formatos, seria ótimo!

Abraço!"""
    ]

    return random.choice(variacoes)
