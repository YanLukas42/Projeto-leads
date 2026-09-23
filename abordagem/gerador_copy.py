"""
Módulo de geração de copys personalizadas e validadas para abordagem (E-mail e WhatsApp).
Implementa frameworks modernos de Cold Email B2B (Low-Friction, Outcome-Led, PAS e Quick Question).
Linguagem natural, humana e direta (sem formalismos robóticos).
Não inclui o e-mail no corpo (já presente no cabeçalho do Gmail).
"""

import random
from typing import Dict, Any

from abordagem.config import REMETENTE_NOME, REMETENTE_EMPRESA


TERMOS_GENERICOS_CARGO = {
    "direção", "direcao", "diretoria", "produção", "producao",
    "executiva", "executivo", "equipe", "administração", "administracao",
    "gerência", "gerencia", "sócio", "socio", "responsável", "responsavel",
    "time", "departamento", "comercial", "gestão", "gestao"
}


def extrair_primeiro_nome(decisor_str: str) -> str:
    """
    Extrai apenas o primeiro nome de uma pessoa real.
    Descarta cargos ou termos genéricos como 'Direção / Produção Executiva'.
    """
    if not decisor_str or decisor_str == "X":
        return ""
    
    # Remover qualificações entre parênteses
    nome_limpo = decisor_str.split("(")[0].split("/")[0].strip()
    partes = nome_limpo.split()
    if not partes:
        return ""

    primeiro = partes[0].title()
    if primeiro.lower() in TERMOS_GENERICOS_CARGO:
        return ""
    
    # Se o nome for muito curto ou suspeito
    if len(primeiro) <= 2:
        return ""

    return primeiro


def _saudacao_destinatario(empresa: str, decisor: str) -> str:
    """Gera saudação natural: se tiver nome de pessoa usa o primeiro nome, senão 'pessoal'."""
    nome = extrair_primeiro_nome(decisor)
    if nome:
        return nome
    return "pessoal"


# =====================================================================
# FRAMEWORKS VALIDADOS DE E-MAIL (B2B TECH & GAME DEV)
# =====================================================================

def _copy_games_framework_1(empresa: str, destinatario: str) -> Dict[str, str]:
    """Modelo 1: Pipeline & Apoio Técnico (PAS Conversacional)"""
    assunto = f"Apoio técnico / pipeline no {empresa}"
    corpo = f"""Fala {destinatario}, tudo bem?

Acompanho o trabalho do estúdio e sei como o ritmo de produção de jogos exige bastante do time principal — especialmente quando surgem demandas de backend, APIs, ferramentas internas ou automação de testes (QA) que acabam tirando o foco da gameplay.

Sou desenvolvedor de software e atuo justamente resolvendo esses gargalos de infraestrutura e engenharia para estúdios independentes, sem que vocês precisem inflar a folha interna.

Faz sentido trocarmos uma ideia rápida de 5 minutos sobre como vocês estruturam demandas de tecnologia aí no {empresa}, ou por enquanto já estão 100% cobertos?

Um abraço,
{REMETENTE_NOME}"""
    return {"assunto": assunto, "corpo": corpo}


def _copy_games_framework_2(empresa: str, destinatario: str) -> Dict[str, str]:
    """Modelo 2: The Quick Question (Ultra Baixo Atrito - 4 linhas)"""
    assunto = f"Pergunta rápida sobre os projetos do {empresa}"
    corpo = f"""Oi {destinatario}, tudo certo?

Passando rápido porque admiro os projetos que vocês vêm lançando no {empresa}.

Trabalho com desenvolvimento de software e apoio técnico especializado para estúdios de games (backend, integrações e ferramentas de suporte ao pipeline).

Vocês costumam abrir espaço para parceiros externos de tecnologia em demandas específicas dos projetos atuais?

Se fizer sentido, podemos trocar 2 minutinhos de ideia sem compromisso.

Valeu!
{REMETENTE_NOME}"""
    return {"assunto": assunto, "corpo": corpo}


def _copy_games_framework_3(empresa: str, destinatario: str) -> Dict[str, str]:
    """Modelo 3: Outcome-Led / Foco em Entrega e Desempenho"""
    assunto = f"Desenvolvimento e escala técnica para o {empresa}"
    corpo = f"""Olá {destinatario}, tudo bem por aí?

Estava dando uma olhada no portfólio do {empresa} e a qualidade das produções chama bastante atenção.

Tenho ajudado equipes de tecnologia e games a acelerar prazos de entrega desenvolvendo microsserviços, esteiras automatizadas de teste e arquiteturas robustas de backend.

Você teria abertura para eu te mandar uma prévia rápida de como isso poderia somar nos lançamentos de vocês deste ano?

Se não for o melhor momento agora, sem problemas também!

Abraço,
{REMETENTE_NOME}"""
    return {"assunto": assunto, "corpo": corpo}


def _copy_games_framework_4(empresa: str, destinatario: str) -> Dict[str, str]:
    """Modelo 4: Networking Direto de Desenvolvedor para Estúdio"""
    assunto = f"{empresa} + parceria técnica"
    corpo = f"""Fala {destinatario}, beleza?

Meu nome é {REMETENTE_NOME}, sou desenvolvedor de software e estou mapeando estúdios brasileiros com produções sólidas para construir parcerias técnicas de longo prazo.

Queria entender diretamente com quem toca os projetos no {empresa}: vocês têm planos de terceirizar ou acelerar partes de backend, integrações de rede ou ferramentas nos próximos meses?

Se tiverem 5 minutos livres nesta semana, seria ótimo bater um papo rápido.

Abraços!
{REMETENTE_NOME}"""
    return {"assunto": assunto, "corpo": corpo}


# =====================================================================
# FRAMEWORKS VALIDADOS PARA RESTAURANTES & VAREJO LOCAL
# =====================================================================

def _copy_restaurante_framework_1(empresa: str, destinatario: str, cidade: str, regiao: str) -> Dict[str, str]:
    """Modelo Restaurante 1: Foco em Redução de Taxas do iFood"""
    assunto = f"Taxas de delivery no {empresa} ({cidade})"
    corpo = f"""Olá {destinatario}, tudo bem?

Acompanho o movimento do {empresa} aqui em {regiao} e sei que a conta das taxas de 12% a 27% de aplicativos como o iFood pesa no final de cada mês.

Criamos o {REMETENTE_EMPRESA}, uma solução prática que coloca o cardápio e os pedidos direto no seu WhatsApp, fidelizando os clientes para comprarem direto com vocês sem comissão.

Faz sentido batermos um papo de 3 minutos para eu te mostrar como funciona na prática, ou por aí vocês já têm uma estratégia própria rodando?

Um abraço,
{REMETENTE_NOME}"""
    return {"assunto": assunto, "corpo": corpo}


def _copy_restaurante_framework_2(empresa: str, destinatario: str, cidade: str, regiao: str) -> Dict[str, str]:
    """Modelo Restaurante 2: Piloto Gratuito / Baixo Atrito"""
    assunto = f"Teste gratuito de pedidos WhatsApp no {empresa}"
    corpo = f"""Oi {destinatario}, tudo certo?

Passando rápido: desenvolvemos um canal de pedidos direto no WhatsApp para restaurantes aqui de {cidade} aumentarem o faturamento de clientes recorrentes sem custo de comissão.

Gostaria de liberar um teste gratuito de 15 dias para você ver o {REMETENTE_EMPRESA} rodando no {empresa} sem compromisso nenhum.

Quem seria a pessoa responsável pela parte comercial ou de atendimento para eu enviar uma demonstração rápida de 2 minutos?

Valeu!
{REMETENTE_NOME}"""
    return {"assunto": assunto, "corpo": corpo}


# =====================================================================
# GERADORES PÚBLICOS
# =====================================================================

def gerar_email_abordagem(lead: Dict[str, Any]) -> Dict[str, str]:
    """
    Gera assunto e corpo para abordagem B2B por e-mail,
    alternando entre frameworks validados de alta conversão.
    """
    empresa = lead.get("Nome") or lead.get("nome") or "seu negócio"
    cidade = lead.get("Cidade") or lead.get("cidade") or "sua cidade"
    bairro = lead.get("Bairro_Regiao") or lead.get("bairro_regiao") or ""
    nicho = (lead.get("Nicho") or lead.get("nicho") or "").lower()
    decisor = lead.get("Decisor_Socio") or lead.get("decisor_socio") or ""
    
    destinatario = _saudacao_destinatario(empresa, decisor)
    regiao = f"{bairro}, {cidade}" if (bairro and bairro != "X" and bairro != "Geral") else cidade

    # 1. Nicho Games / Jogos Digitais / Estúdios
    if any(g in nicho for g in ["game", "jogos", "estudio", "digital"]):
        frameworks_games = [
            _copy_games_framework_1,
            _copy_games_framework_2,
            _copy_games_framework_3,
            _copy_games_framework_4
        ]
        escolhido = random.choice(frameworks_games)
        return escolhido(empresa, destinatario)

    # 2. Nicho Restaurantes / Gastronomia
    if any(r in nicho for r in ["restaurante", "bar", "pizza", "hamburguer", "comida", "buffet"]):
        frameworks_restaurante = [
            _copy_restaurante_framework_1,
            _copy_restaurante_framework_2
        ]
        escolhido = random.choice(frameworks_restaurante)
        return escolhido(empresa, destinatario, cidade, regiao)

    # 3. Nicho Geral (B2B Corporativo / Serviços)
    assunto = f"Parceria técnica e tecnologia para o {empresa}"
    corpo = f"""Olá {destinatario}, tudo bem?

Acompanho a atuação do {empresa} aqui em {regiao} e gostaria de fazer um contato rápido.

Sou desenvolvedor de software e atuo criando soluções sob medida (automações, integrações e ferramentas web) para empresas que querem otimizar processos e captar mais clientes sem aumentar custos fixos.

Faz sentido conversarmos 5 minutos essa semana para entender os desafios atuais de vocês?

Um abraço,
{REMETENTE_NOME}"""
    return {"assunto": assunto, "corpo": corpo}


def gerar_mensagem_whatsapp(lead: Dict[str, Any]) -> str:
    """
    Gera uma mensagem natural, curta e consultiva para o WhatsApp.
    """
    empresa = lead.get("Nome") or lead.get("nome") or "sua empresa"
    cidade = lead.get("Cidade") or lead.get("cidade") or ""
    bairro = lead.get("Bairro_Regiao") or lead.get("bairro_regiao") or ""
    instagram = lead.get("Instagram") or lead.get("instagram") or ""
    decisor = lead.get("Decisor_Socio") or lead.get("decisor_socio") or ""
    destinatario = _saudacao_destinatario(empresa, decisor)
    regiao = f"{bairro}, {cidade}" if (bairro and bairro != "X" and bairro != "Geral") else cidade

    saudacoes = ["Fala", "Opa", "Oi, tudo bem?", "Olá!"]
    saudacao = random.choice(saudacoes)

    inicio = f"{saudacao} {destinatario}! Aqui é o {REMETENTE_NOME}."

    if instagram and instagram != "X":
        gancho = f"Vi o perfil de vocês no Instagram ({instagram.split('?')[0]}) aqui em {regiao}"
    else:
        gancho = f"Acompanho o trabalho do {empresa} aqui em {regiao}"

    propostas = [
        f"Desenvolvemos uma ferramenta de WhatsApp que permite ao restaurante receber pedidos direto dos clientes sem pagar taxa do iFood, além de reativar quem já comprou antes.",
        f"Criamos um canal de pedidos rápidos direto no WhatsApp para restaurantes da região aumentarem o lucro sem depender de comissão de apps de entrega."
    ]
    proposta = random.choice(propostas)

    chamadas = [
        f"Faz sentido batermos um papo de 2 minutos para eu te mostrar como funciona no {empresa}, ou por aí vocês já estão atendidos nesse ponto?",
        f"Gostaria de liberar um acesso de teste sem custo para vocês verem rodando. Quem seria a melhor pessoa aí para eu mandar um vídeo rápido de 1 minuto?"
    ]
    chamada = random.choice(chamadas)

    return f"{inicio}\n\n{gancho}.\n\n{proposta}\n\n{chamada}\n\nAbraço!"
