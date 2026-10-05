# Fontes e processo de coleta

## Fonte primária

Os registros são reais e foram obtidos do ambiente de produção do Portal Nacional de Contratações Públicas (PNCP). Não foram utilizados exemplos do manual, dados de treinamento ou ambiente de homologação.

- Instituição: Universidade Federal de São Paulo (Unifesp).
- CNPJ do órgão: 60.453.032/0001-74.
- Recorte: publicação no PNCP de 01/01/2025 a 31/12/2025.
- Coleta: 05/10/2026, às 06:20, no horário de São Paulo. O instante completo em UTC está no arquivo de metadados.
- Retorno completo: 615 registros, em duas páginas, de 500 e 115 registros.
- CSV distribuído: 615 linhas e 19 colunas selecionadas.

As consultas exatas foram:

[Primeira página da API oficial](https://pncp.gov.br/api/consulta/v1/contratos?dataInicial=20250101&dataFinal=20251231&cnpjOrgao=60453032000174&pagina=1&tamanhoPagina=500)

[Segunda página da API oficial](https://pncp.gov.br/api/consulta/v1/contratos?dataInicial=20250101&dataFinal=20251231&cnpjOrgao=60453032000174&pagina=2&tamanhoPagina=500)

A consulta é por **publicação**, não por assinatura. A seleção analisada contém 170 contratos com ano cadastral 2025 e 13 com 2024. A análise não afirma que todos foram assinados em 2025.

## Preservação e transformação

O coletor preserva os bytes das respostas oficiais no backup local. URLs, quantidade de registros e hashes SHA-256 constam em `dados/metadados_coleta.json`. O hash do CSV permite conferir se a versão utilizada é a mesma da coleta documentada.

O arquivo público `contratos_unifesp_pncp_2025.csv` é uma projeção dos campos necessários à análise. Campos aninhados, como categoria e unidade, foram transformados em colunas. Os valores financeiros e as datas foram preservados como informados. O texto livre do objeto não foi incluído.

A fonte completa contém dois fornecedores pessoa física. Seus nomes e documentos foram substituídos por códigos consistentes no CSV e nas saídas. Os arquivos brutos completos ficam em `.backup_local/pncp_bruto`, que não integra a entrega. A projeção usa os nomes e identificadores públicos de PJ/PE para permitir o agrupamento por fornecedor. Esse tratamento não certifica anonimização irreversível.

## Recorte analítico

A análise inclui somente `Tipo_Instrumento = Contrato (termo inicial)` e `Receita = False`. São 183 registros. Os 423 empenhos, 3 termos de adesão e 6 contratos iniciais de receita ficam no arquivo completo e em `fora_do_escopo.csv`, mas não entram na comparação.

Seis registros têm publicação anterior à assinatura cadastrada. Eles são mantidos nas análises de valores e vigências, mas excluídos do intervalo de publicação, que usa 177 registros. As ocorrências estão identificadas em `ocorrencias_qualidade.csv`. Um valor global zero é preservado, com observação para conferência. Nenhum valor foi inventado ou alterado para tornar o resultado mais favorável.

## Validade e limitações

O cadastro pode mudar após a coleta. As vigências e valores observados podem refletir atualizações e retificações posteriores à publicação de 2025. Na seleção, 51 contratos têm retificações informadas. A consulta não é um retrato congelado do cadastro em 31/12/2025.

As datas não medem aprovação interna ou horas de trabalho. Valores globais não correspondem a pagamentos efetuados no ano. Categorias têm tamanhos e finalidades diferentes. Diferenças de data, concentração e outliers exigem documentação adicional para interpretar causas.

## Referências oficiais

- [PNCP: dados abertos e acesso público](https://www.gov.br/pncp/pt-br/acesso-a-informacao/copy_of_dados-abertos).
- [PNCP: dicionário de Contrato/Empenho](https://pncp.gov.br/manual/pt-br/latest/contrato_empenho/consultar_contrato_ou_empenho.html).
- [PNCP: Manual API Consultas, serviço de contratos por data de publicação](https://www.gov.br/pncp/pt-br/central-de-conteudo/manuais/versoes-anteriores/ManualPNCPAPIConsultasVerso1.0.pdf).
- [Unifesp: apresentação institucional](https://unifesp.br/campus/osa2/eppen-novo/apresentacao).
- [Unifesp: portal de transparência](https://unifesp.br/reitoria/transparencia/).
- [Unifesp: Relatório de Gestão 2020, p. 12](https://www.unifesp.br/reitoria/transparencia/images/docs/relatorio_gestao/relatorio_gestao_2020.pdf), usado como referência histórica de identidade institucional, sem atribuir vigência atual a todo o texto.

O PNCP apresenta os dados abertos como disponíveis para consulta e reutilização. O trabalho mantém a atribuição à fonte e distingue informações oficiais de cálculos e propostas do autor.
