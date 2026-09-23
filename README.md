# 🎯 Sistema de Prospecção & Abordagem Multi-Canal (Leads & Influencers)

Sistema completo para mineração, enriquecimento, qualificação de leads B2B e criadores de conteúdo (influenciadores), com automação de disparos via WhatsApp e E-mail (SMTP seguro) e monitoramento de respostas.

---

## 🚀 Módulos do Projeto

1. **`leads/`**:
   - Scraping e mineração via Google Places/Maps, Receita/CNPJ e Web.
   - Enriquecimento de contatos (e-mails, celulares/WhatsApp, redes sociais).
   - Deduplicação inteligente e exportação formatada.

2. **`abordagem/`**:
   - Disparador de alta conversão B2B via E-mail (Gmail SMTP com delays humanos).
   - Disparador via WhatsApp com proteções anti-ban (tetos diários e pausas randômicas).
   - Tracker de envios para evitar abordagens duplicadas.
   - Gerador de copys persuasivas personalizadas por nicho.

3. **`influencers/`**:
   - Mineração de canais do YouTube e perfis por palavras-chave e métricas.
   - Enriquecimento de redes sociais e e-mails de parcerias comerciais.
   - Disparador com modelos de copy adaptados para parcerias e mídia kit.

4. **`respostas/`**:
   - Monitoramento contínuo da caixa de entrada via IMAP para detecção em tempo real de retornos de leads abordados.

---

## ⚙️ Pré-requisitos & Instalação

### 1. Clonar o repositório
```bash
git clone https://github.com/SEU_USUARIO/Projeto-leads.git
cd Projeto-leads
```

### 2. Criar e ativar o ambiente virtual
```bash
python3 -m venv .venv
source .venv/bin/activate  # No Linux/macOS
# ou: .venv\Scripts\activate  # No Windows
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente
Copie o modelo de ambiente e preencha suas credenciais:
```bash
cp .env.example .env
```
Edite o arquivo `.env`:
- `SMTP_USER`: Seu e-mail de envio.
- `SMTP_PASSWORD`: Sua Senha de Aplicativo (App Password do Google/provedor).
- Demais dados opcionais de remetente e personalização.

> ⚠️ **Aviso de Segurança**: Nunca faça commit do seu arquivo `.env` real nem de relatórios contendo dados de contato de terceiros. Eles já estão bloqueados pelo `.gitignore`.

---

## 💻 Como Usar

### Mineração de Leads:
```bash
python3 leads/main.py
```

### Disparador de Abordagem B2B:
```bash
python3 abordagem/main_abordagem.py
```

### Mineração e Abordagem de Influenciadores:
```bash
python3 influencers/main.py
```

### Monitoramento de Respostas:
```bash
python3 respostas/monitor.py
```

---

## 🔒 Segurança e Privacidade
- O projeto segue boas práticas de proteção de credenciais via variáveis de ambiente.
- Dados brutos extraídos (`.csv`), históricos de disparo (`.json`) e arquivos de log (`.log`) são ignorados pelo Git para conformidade com a LGPD e privacidade de dados.
