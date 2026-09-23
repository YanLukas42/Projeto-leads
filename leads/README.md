# Ferramenta de Prospecção de Leads (CLI)

Ferramenta modular em Python para encontrar comércios locais por cidades, regiões e bairros nobres, enriquecer contatos (Instagram, WhatsApp com dígito 9, Telefones, E-mails e Sócios) e exportar em CSV.

---

## Como Executar

### 1. Modo Interativo no Terminal
```bash
python3 leads/main.py
```
O sistema exibirá as opções para você digitar:
- Uma cidade única: `Campinas`
- Múltiplas cidades: `Campinas, Paulínia, Valinhos`
- Cidade com bairros específicos: `Campinas: Cambuí, Taquaral` ou `DF: Asa Sul, Águas Claras`

---

### 2. Modo Direto via Argumentos de Linha de Comando

```bash
# Busca com bairros específicos
python3 leads/main.py --cidade "Campinas: Cambuí, Taquaral" --nicho "restaurante" --limite 15

# Busca em múltiplas cidades
python3 leads/main.py --cidade "Campinas, Valinhos, Paulínia" --nicho "odontologia" --limite 20

# Busca no Distrito Federal com regiões administrativas
python3 leads/main.py --cidade "DF: Asa Sul, Águas Claras" --nicho "academia" --limite 20

# Consulta de CNPJ oficial (com Quadro de Sócios/QSA)
python3 leads/main.py --cnpj "00.000.000/0001-91"
```

---

## Onde os Leads são Salvos
Os arquivos gerados são salvos em:
```text
leads/output/leads_<cidade>_<nicho>_<data_hora>.csv
```

### Estrutura das Colunas do CSV:
1. **Nome**: Nome fantasia ou razão comercial.
2. **Status_Lead**: `🔥 QUENTE (Alta Presença Digital)`, `MORNO` ou `FRIO`.
3. **Celular_WhatsApp**: Apenas números móveis (com dígito 9) prontos para disparo.
4. **Telefone_Fixo**: Números fixos identificados (recepção/escritório).
5. **Decisor_Socio**: Nome do sócio-administrador/diretor (QSA).
6. **Email**: E-mail oficial do comércio.
7. **Instagram**: Link direto do perfil no Instagram.
8. **Site**: Website oficial.
9. **Bairro_Regiao**: Bairro ou região mapeada (ex: Cambuí, Taquaral, Asa Sul).
10. **Endereco**: Logradouro e número.
11. **Cidade**: Município.
12. **Nicho**: Segmento pesquisado.
13. **Fonte**: Origem dos dados (Base Comercial, Busca Web/Instagram, Fichas).
