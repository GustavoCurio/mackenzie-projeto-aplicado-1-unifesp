# Etapa 2 — Proposta analítica e análise exploratória

**Autor:** Gustavo Curio Kolbe — RA 10750739. Trabalho individual.

**Repositório:** https://github.com/GustavoCurio/mackenzie-projeto-aplicado-1-unifesp

## Sumário

- [Objetivo e dados](#objetivo-e-dados)
- [Etapas da análise](#etapas-da-análise)
- [Reprodução](#reprodução)
- [Principais resultados](#principais-resultados)
- [Limitações](#limitações)
- [Arquivos](#arquivos)

## Objetivo e dados

Este trabalho faz parte do Projeto Aplicado I do curso de Ciência de Dados da Universidade Presbiteriana Mackenzie. O objetivo é analisar os valores, as vigências e os intervalos entre assinatura e publicação dos contratos da Universidade Federal de São Paulo (Unifesp).

Na Etapa 2, o estudo complementa a definição da organização e dos dados apresentada na primeira etapa. A proposta é utilizar a análise exploratória para identificar características dos contratos e definir indicadores que possam apoiar consultas e o planejamento administrativo.

A fonte é o [Portal Nacional de Contratações Públicas (PNCP)](https://www.gov.br/pncp/pt-br/acesso-a-informacao/copy_of_dados-abertos). A coleta foi realizada em 05/10/2026, considerando os registros da Unifesp publicados entre 01/01/2025 e 31/12/2025.

A base possui 615 registros e 19 colunas. Para a comparação principal, foram selecionados 183 contratos iniciais de despesa. Empenhos, termos de adesão e contratos de receita permanecem na base original, mas ficam fora desse recorte. Os nomes e documentos de fornecedores pessoas físicas foram substituídos por códigos no CSV distribuído.

## Etapas da análise

1. Leitura do CSV e conferência dos identificadores e das colunas.
2. Conversão dos valores e das datas.
3. Seleção dos contratos iniciais de despesa.
4. Cálculo da vigência e do intervalo de publicação em dias corridos.
5. Cálculo de médias, medianas, modas, quartis, percentis e medidas de dispersão.
6. Comparação por categoria, identificação de outliers e análise de correlações.
7. Geração das tabelas e dos gráficos.

## Reprodução

Recomenda-se Python 3.11 ou superior. Dentro desta pasta:

```console
python -m pip install -r requirements.txt
python scripts/analise_exploratoria.py
```

As tabelas são gravadas em `output/analise` e os seis gráficos em `output/graficos`. O arquivo `dados/metadados_coleta.json` registra a origem e as informações da coleta.

Os códigos contêm comentários sobre os filtros e os cálculos. O [guia dos scripts](scripts/Como%20estudar%20os%20scripts.md) descreve a sequência da análise e os principais comandos utilizados.

Para uma nova coleta opcional:

```console
python scripts/coletar_dados_pncp.py
```

Para reproduzir os resultados apresentados no trabalho, utilize o CSV que acompanha o projeto. Uma nova coleta pode trazer alterações nos registros do PNCP e, por isso, produzir resultados diferentes. As respostas brutas da API são armazenadas em `.backup_local` e não fazem parte da publicação.

## Principais resultados

- Mediana do valor global: R$ 186.000,00; vigência mediana: 365 dias.
- Intervalo de publicação mediano: 2 dias, com 177 registros válidos.
- Seis intervalos negativos excluídos apenas desse indicador; um valor zero mantido e sinalizado.
- Pearson: 0,208; Spearman: 0,295, em 183 pares. O gráfico logarítmico mostra 182 valores positivos.
- Cinco fornecedores concentram 87,09% da soma dos valores globais cadastrados.

## Limitações

Os valores globais correspondem ao cadastro disponível na coleta e não representam pagamentos realizados em 2025. As vigências também podem refletir alterações e prorrogações. O intervalo entre assinatura e publicação não mede o tempo de tramitação interna.

As categorias têm quantidades diferentes de contratos, o que limita algumas comparações. Outliers e concentração de valores indicam pontos para análise, mas não comprovam irregularidades. As correlações não demonstram causalidade. O painel de acompanhamento é uma proposta do projeto e não foi implantado na Unifesp.

## Arquivos

| Pasta ou arquivo | Conteúdo |
| --- | --- |
| `scripts/` | Códigos de coleta e análise exploratória e guia de leitura. |
| `dados/` | Base CSV e metadados da coleta. |
| `output/analise/` | Tabelas e resumo dos cálculos. |
| `output/graficos/` | Gráficos da análise exploratória. |
| `docs/` | Informações sobre as fontes e a aquisição dos dados. |
| `requirements.txt` | Bibliotecas necessárias para executar a análise. |
