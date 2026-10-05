# Etapa 2 — Proposta analítica e análise exploratória

**Autor:** Gustavo Curio Kolbe — RA 10750739. Trabalho individual.

## Sumário

- [Objetivo e dados](#objetivo-e-dados)
- [Documento](#documento)
- [Reprodução](#reprodução)
- [Resultados e cuidados](#resultados-e-cuidados)
- [Arquivos](#arquivos)

## Objetivo e dados

A coleta que foi realizada no dia 28/09/2026 contém 615 registros e 19 atributos da Unifesp, publicados em 2025. O recorte principal contém 183 contratos iniciais de despesa.

## Documento

- [PDF da Etapa 2](Etapa%202%20-%20Proposta%20Analitica%20e%20AED.pdf): versão com 15 páginas visualmente conferidas.
- [Word editável](Etapa%202%20-%20Proposta%20Analitica%20e%20AED.docx): conteúdo editável; conferir paginação e sumário no Word, pois a prévia visual automática está indisponível neste ambiente.
- [Texto editável](Etapa%202%20-%20Texto%20editavel.md).

O documento mantém organização, objetivos e metadados da primeira etapa e acrescenta proposta analítica, tratamento, medidas descritivas, percentis, gráficos, correlações, inconsistências, outliers, interpretação, limitações e glossário. O número de servidores não foi quantificado nas fontes utilizadas e está identificado como limitação da contextualização. O prazo de entrega continua em branco até a confirmação do calendário.

## Reprodução

Recomenda-se Python 3.11 ou superior. Dentro desta pasta:

```console
python -m pip install -r requirements.txt
python scripts/analise_exploratoria.py
```

As tabelas são gravadas em `output/analise` e as seis figuras em `output/graficos`. Os scripts têm comentários sobre leitura, filtros, cálculos e interpretação.

Os scripts foram organizados em uma versão didática, com cálculos separados e nomes de variáveis descritivos. Para estudar a sequência e os comandos, consulte [Como estudar os scripts](scripts/Como%20estudar%20os%20scripts.md).

Para uma nova coleta opcional:

```console
python scripts/coletar_dados_pncp.py
```

Uma nova coleta pode alterar o cadastro e exige revisão dos resultados e da redação. Para reproduzir esta entrega, usar o CSV incluído. Respostas brutas com identificadores de pessoas físicas ficam em `.backup_local`, ignorada pelo Git.

## Resultados e cuidados

- Mediana do valor global: R$ 186.000,00; vigência mediana: 365 dias.
- Intervalo de publicação mediano: 2 dias, com 177 registros válidos.
- Seis intervalos negativos excluídos apenas desse indicador; um valor zero mantido e sinalizado.
- Pearson: 0,208; Spearman: 0,295, em 183 pares. O gráfico logarítmico mostra 182 valores positivos.
- Cinco fornecedores concentram 87,09% da soma dos valores globais cadastrados.

Os valores não são pagamentos no exercício. Os intervalos não medem tramitação interna. Outliers e concentração não comprovam irregularidades. O painel é uma proposta, sem implantação ou validação institucional.

## Arquivos

`scripts/`: análise e coleta. `dados/`: base e metadados da fonte. `output/analise/`: resumo e tabelas. `output/graficos/`: gráficos. `docs/Fontes_e_Coleta.md`: descrição da origem. `requirements.txt`: dependências.
