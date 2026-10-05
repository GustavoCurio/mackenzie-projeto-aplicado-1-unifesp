# Como estudar os scripts da Etapa 2

Comece por `analise_exploratoria.py`. Ele usa o CSV que acompanha a entrega e não precisa acessar a internet. O arquivo de coleta é uma parte separada, para obter ou atualizar os registros no PNCP.

## Ordem de leitura

1. **Caminhos e importações:** identificam as bibliotecas e o local dos arquivos.
2. **Função calcular_estatisticas:** calcula uma medida por linha. Uma função reúne comandos que serão usados para mais de uma coluna.
3. **Leitura e conferência:** abrem o CSV, verificam a instituição e transformam valores e datas nos tipos adequados.
4. **Recorte:** seleciona somente contratos iniciais de despesa, deixando 183 registros na base utilizada nesta entrega.
5. **Datas e validade:** calculam vigência e intervalo de publicação. Seis intervalos negativos ficam fora apenas da estatística de publicação.
6. **Categorias e outliers:** calculam medidas por grupo e sinalizam valores fora dos limites do IQR.
7. **Frequências, fornecedores e correlações:** contam as faixas, calculam participações e comparam valor e vigência.
8. **Exportação e gráficos:** salvam os resultados e montam cada figura separadamente.

## Comandos que aparecem na análise

| Comando | Para que serve neste trabalho |
| --- | --- |
| `dados['Valor_Global']` | Seleciona uma coluna da tabela. |
| `dados.loc[filtro]` | Seleciona as linhas que atendem ao filtro. |
| `tabela.iloc[0]` | Lê a primeira linha pela posição. |
| `groupby('Categoria')` | Reúne os contratos da mesma categoria. |
| `mean()` e `median()` | Calculam média e mediana. |
| `quantile(0.25)` | Calcula o primeiro quartil. |
| `isna()` e `notna()` | Identificam valores ausentes e preenchidos. |
| `&`, `|` e `~` | Combinam condições: e, ou e negação. |
| `for` | Repete comandos para colunas, grupos ou rótulos. |
| `if` | Executa um comando quando uma condição é atendida. |
| `to_csv()` | Salva uma tabela em arquivo CSV. |

## Um exemplo para entender o filtro

```python
contrato_inicial = dados['Tipo_Instrumento'] == 'Contrato (termo inicial)'
contrato_de_despesa = dados['Receita'] == False
filtro = contrato_inicial & contrato_de_despesa
contratos = dados.loc[filtro].copy()
```

Primeiro verifico o instrumento. Depois verifico se é despesa. O símbolo `&` exige as duas condições. Por fim, copio as linhas selecionadas para a tabela `contratos`.

## Pontos para explicar ao professor

- A base original tem 615 registros; a comparação usa 183 contratos iniciais de despesa.
- Valor global é um valor cadastrado, não o pagamento realizado em 2025.
- A vigência é calculada subtraindo o início do fim cadastrado.
- A publicação é calculada subtraindo a assinatura do dia da publicação.
- Os seis intervalos negativos são sinalizados; seus valores e vigências continuam nos demais cálculos.
- A escala logarítmica não mostra o valor zero, mas ele continua nas estatísticas quando é válido.
- Uma correlação não demonstra causa, e um outlier não comprova irregularidade.

## Arquivo de coleta

Leia `coletar_dados_pncp.py` depois de entender a análise. Ele consulta as páginas da API, confere o total e o período, troca identificadores de PF por códigos, salva as 19 colunas e registra a origem da coleta. Usa bibliotecas que já acompanham o Python.

Se a API estiver indisponível, a coleta para e precisa ser executada novamente. Não é necessário refazer a coleta para reproduzir esta entrega: use o CSV incluído.
