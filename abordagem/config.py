"""
Configurações do remetente e parâmetros da campanha comercial.
"""

import os

REMETENTE_NOME = os.getenv("REMETENTE_NOME", "Lukas")
REMETENTE_EMPRESA = os.getenv("REMETENTE_EMPRESA", "ZapMenu")
REMETENTE_DESCRICAO = os.getenv("REMETENTE_DESCRICAO", "sistema de pedidos e fidelização direta no WhatsApp")
REMETENTE_WHATSAPP = os.getenv("REMETENTE_WHATSAPP", "")
REMETENTE_EMAIL = os.getenv("REMETENTE_EMAIL", os.getenv("SMTP_USER", ""))

# Parâmetros de Segurança Anti-Ban do WhatsApp
WHATSAPP_LIMITE_DIARIO = 25
WHATSAPP_DELAY_MIN = 40
WHATSAPP_DELAY_MAX = 90
