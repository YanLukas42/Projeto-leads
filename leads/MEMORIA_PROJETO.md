# Memória e Diretrizes Estratégicas do Projeto de Leads & Abordagem

Este documento registra as diretrizes, premissas e a visão de produto construídas em conjunto para nortear o desenvolvimento e a análise contínua dos resultados.

---

## 1. Visão de Parceria e Análise Conjunta
- **Propósito**: Esta ferramenta é uma máquina de aquisição de clientes de ponta a ponta: Captação -> Abordagem Segura -> Monitoramento de Respostas.
- **Análise a Quatro Mãos**: Todos os resultados, métricas de conversão e qualidade dos dados gerados são analisados em conjunto (usuário e assistente de IA).

---

## 2. Estrutura das Três Vertentes do Projeto

```text
Projeto-leads/
├── leads/                   # Vertente 1: Captação e Inteligência Geográfica
│   ├── core/
│   │   ├── geo_parser.py    # Suporte a Cidades e Bairros (ex: "Campinas: Cambuí")
│   │   ├── scraper.py       # Base física municipal
│   │   ├── scraper_web.py   # Rastreamento web e Instagram
│   │   ├── scraper_maps.py  # Fichas de mapa locais
│   │   ├── enricher.py      # Crawler de mídias e classificação de leads quentes
│   │   ├── cnpj.py          # Dados cadastrais e sócios/QSA da Receita
│   │   ├── deduplicator.py  # Fusão e remoção de duplicatas
│   │   └── exporter.py      # CSV universal RFC 4180
│   └── output/              # Planilhas CSV geradas
│
├── abordagem/               # Vertente 2: Motor Comercial de Conversão
│   ├── config.py            # Credenciais e parâmetros de segurança (Lukas)
│   ├── gerador_copy.py      # 4 Modelos validados de Cold Outreach (PAS, Low-Friction, Outcome-Led)
│   ├── canal_whatsapp.py    # WhatsApp seguro com delays humanos (40-90s) e teto de 25 msgs/dia
│   ├── canal_email.py       # Disparador B2B via Gmail SMTP com delays de segurança
│   ├── disparador_background.py # Automação em background contínua
│   └── tracker.py           # Histórico de envios (impede disparos duplicados)
│
└── respostas/               # Vertente 3: Monitor de Retorno e Respostas (Inbox)
    ├── monitor.py           # Monitor IMAP que identifica quando um lead responde
    └── respostas_recebidas.json # Registro de respostas quentes recebidas

├── influencers/             # Vertente 4: Criadores de Conteúdo (10k a 50k) para Aulas de Inglês
    ├── config.py            # Configurações do negócio de inglês e filtros
    ├── scraper_youtube.py   # Mineração de canais via YouTube Browse + yt-dlp
    ├── enricher_social.py   # Resolvedor de Linktree/Beacons -> WhatsApp e E-mail
    ├── copy_influencers.py  # Copys de Mídia Kit e Parceria para criadores
    ├── disparador_influencers.py # Disparador SMTP para criadores
    ├── main.py              # CLI de mineração e abordagem
    ├── SCRIPT_FECHAMENTO.md # Playbook com scripts de resposta rápida, objeções e roteiro de 45s
    └── output/              # CSVs de criadores qualificados
```

---

## 3. Campanhas em Execução Ativa
- **Campanha Ativa**: 55 Estúdios de Games no Brasil.
- **Canal**: E-mail B2B via Gmail SMTP (configurado via .env).
- **Cadência**: Intervalos de 8 a 15 segundos por disparo com rotação de 4 frameworks de copy.
- **Acompanhamento ao Vivo**: [`abordagem/campanha_ativa.log`](file:///home/lukas/Documents/GitHub/Projeto-leads/abordagem/campanha_ativa.log).
