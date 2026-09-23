# Módulo de Monitoramento de Respostas (Inbox de Leads)

Este módulo fecha o ciclo de prospecção comercial: ele se conecta à sua conta de e-mail via IMAP e avisa imediatamente quando um lead abordado responde à sua mensagem.

---

## Como Funciona

1. O script lê o arquivo de histórico [`abordagem/historico_envios.json`](file:///home/lukas/Documents/GitHub/Projeto-leads/abordagem/historico_envios.json).
2. Conecta de forma segura à sua Caixa de Entrada.
3. Se algum dos estúdios ou empresas que você abordou responder ao e-mail, ele extrai o texto da resposta e salva em `respostas_recebidas.json`.
4. Emite um alerta com o nome da empresa e o resumo do que responderam para você dar o retorno rápido.

---

## Como Executar

Para checar respostas a qualquer momento:
```bash
python3 respostas/monitor.py
```
