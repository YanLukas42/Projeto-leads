# Módulo de Abordagem Comercial (Outreach)

Este módulo é responsável por transformar a base de leads gerada em oportunidades reais de vendas, com foco em WhatsApp e E-mail, garantindo máxima proteção contra bloqueios de chip (Anti-Ban).

---

## Estrutura de Arquivos

```text
abordagem/
├── gerador_copy.py      # IA que cria abordagens hiper-personalizadas por lead
├── canal_whatsapp.py    # Disparador WhatsApp com proteção estrita de chip
├── canal_email.py       # Disparador B2B para e-mails (simulação e SMTP)
├── tracker.py           # Histórico de envios para evitar mensagens duplicadas
├── main_abordagem.py    # Ponto de entrada CLI simples
└── README.md            # Este manual
```

---

## Como Executar

### 1. Modo Interativo no Terminal
Basta executar:
```bash
python3 abordagem/main_abordagem.py
```
O sistema listará as planilhas da pasta `leads/output/` para você escolher qual lista deseja abordar e qual canal utilizar.

### 2. Modo Direto via Linha de Comando
```bash
# Executar campanha no WhatsApp (com trava diária e delay randômico de 30-60s)
python3 abordagem/main_abordagem.py --arquivo "leads/output/leads_campinas_e_regioes_restaurante_20260921_193051.csv" --canal whatsapp --limite 10

# Executar campanha abrindo no navegador com a mensagem pronta
python3 abordagem/main_abordagem.py --arquivo "leads/output/leads_campinas_e_regioes_restaurante_20260921_193051.csv" --canal whatsapp --limite 5 --navegador

# Simulação da campanha de e-mail (para conferir as copies antes de disparar)
python3 abordagem/main_abordagem.py --arquivo "leads/output/leads_campinas_e_regioes_restaurante_20260921_193051.csv" --canal email
```

---

## Regras de Segurança Implementadas (Anti-Ban)

1. **Trava Diária Rígida**: Máximo de 25 mensagens por dia no WhatsApp.
2. **Delays Randômicos**: Intervalo imprevisível de **40 a 90 segundos** entre cada mensagem (simulando comportamento humano).
3. **Variação Dinâmica de Texto**: A cada lead, saudações, ganchos e CTAs são alternados pela IA para que nenhum hash de texto seja repetido.
4. **Anti-Duplicação**: O `tracker.py` armazena o histórico em `historico_envios.json`. Leads já abordados são pulados automaticamente.
