"""Projeto Aplicado I - AED de contratos reais da Unifesp no PNCP.

Autor: Gustavo Curio Kolbe - RA 10750739.
Neste estudo, analiso valores globais, vigências cadastradas e o intervalo
entre assinatura e publicação. A fonte é pública e o recorte considera
publicações de 2025. As vigências e os valores podem refletir retificações.

Execute: python scripts/analise_exploratoria.py
Para coletar novamente: python scripts/coletar_dados_pncp.py
As saídas ficam em output/analise e output/graficos.
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
PASTA_PROJETO = Path(__file__).resolve().parents[1]
ARQUIVO_DADOS = PASTA_PROJETO / 'dados' / 'contratos_unifesp_pncp_2025.csv'
AZUL = '#06345d'
VERDE = '#00a76f'
# Arquivo que vou analisar.
arquivo_entrada = ARQUIVO_DADOS
pasta_saida = PASTA_PROJETO / 'output'

def calcular_estatisticas(serie):
    """Calcula uma medida por linha, usando somente os valores preenchidos."""
    valores_validos = serie.dropna()
    if valores_validos.empty:
        return {'count': 0}
    resultado = {}
    resultado['count'] = float(valores_validos.count())
    resultado['mean'] = float(valores_validos.mean())
    resultado['std'] = float(valores_validos.std())
    resultado['min'] = float(valores_validos.min())
    resultado['25%'] = float(valores_validos.quantile(0.25))
    resultado['50%'] = float(valores_validos.median())
    resultado['75%'] = float(valores_validos.quantile(0.75))
    resultado['max'] = float(valores_validos.max())
    resultado['moda'] = []
    for valor in valores_validos.mode():
        resultado['moda'].append(float(valor))
    resultado['percentis'] = {}
    resultado['percentis']['10'] = float(valores_validos.quantile(0.1))
    resultado['percentis']['90'] = float(valores_validos.quantile(0.9))
    resultado['percentis']['95'] = float(valores_validos.quantile(0.95))
    # Variância e desvio padrão usam o divisor n - 1.
    resultado['variancia'] = float(valores_validos.var())
    resultado['amplitude'] = float(valores_validos.max() - valores_validos.min())
    if valores_validos.mean() != 0:
        resultado['cv_percentual'] = float(valores_validos.std() / valores_validos.mean() * 100)
    else:
        resultado['cv_percentual'] = None
    return resultado

# 1. Leitura. Preservo os identificadores como texto para não perder zeros.
# read_csv() lê o arquivo; dados é uma tabela do Pandas (DataFrame).
tipos_identificadores = {
    'ID_PNCP': str,
    'Numero_Contrato': str,
    'CNPJ_Orgao': str,
    'ID_Fornecedor': str,
}
dados = pd.read_csv(
    arquivo_entrada,
    sep=';', encoding='utf-8-sig', dtype=tipos_identificadores,
)

colunas_necessarias = [
    'ID_PNCP', 'CNPJ_Orgao', 'Categoria', 'Tipo_Instrumento', 'Receita',
    'Valor_Global', 'Valor_Inicial', 'Data_Assinatura', 'Data_Publicacao',
    'Data_Vigencia_Inicio', 'Data_Vigencia_Fim', 'ID_Fornecedor', 'Fornecedor',
    'Ano_Contrato', 'Numero_Retificacoes',
]
for coluna in colunas_necessarias:
    if coluna not in dados.columns:
        raise ValueError('Falta a coluna: ' + coluna)

if dados.empty or dados['ID_PNCP'].isna().any() or dados['ID_PNCP'].duplicated().any():
    raise ValueError('A base precisa de registros com identificadores únicos e preenchidos.')

if not (dados['CNPJ_Orgao'] == '60453032000174').all():
    raise ValueError('A base contém outra instituição.')

dados['Receita'] = dados['Receita'].astype(str).str.lower().map({'true': True, 'false': False})

if dados['Receita'].isna().any():
    raise ValueError('O indicador Receita não foi interpretado.')

campos_ausentes = {}
for coluna, n in dados.isna().sum().items():
    campos_ausentes[coluna] = int(n)

datas_invalidas = {}

# 2. Conversão. As datas oficiais usam ano-mês-dia e a publicação inclui hora.
# Normalizo a publicação para comparar dias de calendário, sem considerar
# frações de dia. Não uso nenhuma dessas datas como solicitação interna.
for coluna in ['Data_Assinatura', 'Data_Publicacao', 'Data_Vigencia_Inicio', 'Data_Vigencia_Fim']:
    valores_antes_da_conversao = dados[coluna]
    dados[coluna] = pd.to_datetime(valores_antes_da_conversao, format='ISO8601', errors='coerce')
    datas_invalidas[coluna] = int((valores_antes_da_conversao.notna() & dados[coluna].isna()).sum())

if dados['Data_Publicacao'].isna().any() or not (dados['Data_Publicacao'].dt.year == 2025).all():
    raise ValueError('Publicação ausente, inválida ou fora de 2025.')

for coluna in ['Valor_Inicial', 'Valor_Global']:
    dados[coluna] = pd.to_numeric(dados[coluna], errors='coerce')

# 3. Recorte. Empenhos, termos de adesão e receitas não são comparáveis
# diretamente aos contratos iniciais de despesa. Mantenho toda a base em
# arquivo, mas delimito a AED a esse grupo antes de calcular estatísticas.
# Cada condição tem um nome. O símbolo & combina as duas condições.
contrato_inicial = dados['Tipo_Instrumento'] == 'Contrato (termo inicial)'
contrato_de_despesa = dados['Receita'] == False
filtro = contrato_inicial & contrato_de_despesa

dados['No_Escopo'] = filtro

contratos = dados.loc[filtro].copy()

if contratos.empty:
    raise ValueError('Nenhum contrato corresponde ao recorte.')

contratos['Vigencia_Dias'] = (contratos['Data_Vigencia_Fim'] - contratos['Data_Vigencia_Inicio']).dt.days

contratos['Intervalo_Publicacao_Dias'] = (contratos['Data_Publicacao'].dt.normalize() - contratos['Data_Assinatura']).dt.days

# Uma inconsistência em publicação não elimina os valores e vigências do
# contrato. Cada indicador tem sua própria verificação de elegibilidade.
contratos['Valor_Valido'] = contratos['Valor_Global'].notna() & (contratos['Valor_Global'] >= 0)

contratos['Vigencia_Valida'] = contratos['Vigencia_Dias'].notna() & (contratos['Vigencia_Dias'] >= 0)

contratos['Publicacao_Valida'] = contratos['Intervalo_Publicacao_Dias'].notna() & (contratos['Intervalo_Publicacao_Dias'] >= 0)

contratos['Observacao_Qualidade'] = ''

for indice, registro in contratos.iterrows():
    motivos = []
    if not registro.Valor_Valido:
        motivos.append('valor global ausente, inválido ou negativo')
    if registro.Valor_Valido and registro.Valor_Global == 0:
        motivos.append('valor global zero: conferir cadastro')
    if not registro.Vigencia_Valida:
        motivos.append('vigência ausente, inválida ou negativa')
    if not registro.Publicacao_Valida:
        motivos.append('intervalo assinatura-publicação ausente ou negativo')
    contratos.loc[indice, 'Observacao_Qualidade'] = '; '.join(motivos)

valores = contratos.loc[contratos['Valor_Valido'], 'Valor_Global']

vigencias = contratos.loc[contratos['Vigencia_Valida'], 'Vigencia_Dias']

publicacoes = contratos.loc[contratos['Publicacao_Valida'], 'Intervalo_Publicacao_Dias']

# 4. Estatística descritiva. Tamanhos pequenos aparecem nas tabelas e devem
# limitar a interpretação. A categoria oficial é mantida, sem rótulos jurídicos
# inventados. Valor global cadastrado não equivale a gasto pago em 2025.
grupos_categoria = contratos.groupby('Categoria')

estatisticas_categoria = pd.DataFrame()
estatisticas_categoria['Quantidade'] = grupos_categoria['ID_PNCP'].count()
estatisticas_categoria['Media_Valor'] = grupos_categoria['Valor_Global'].mean()
estatisticas_categoria['Mediana_Valor'] = grupos_categoria['Valor_Global'].median()
estatisticas_categoria['Desvio_Valor'] = grupos_categoria['Valor_Global'].std()
estatisticas_categoria['Minimo_Valor'] = grupos_categoria['Valor_Global'].min()
estatisticas_categoria['Maximo_Valor'] = grupos_categoria['Valor_Global'].max()
estatisticas_categoria['Soma_Valor'] = grupos_categoria['Valor_Global'].sum()
estatisticas_categoria['Mediana_Vigencia'] = grupos_categoria['Vigencia_Dias'].median()

estatisticas_categoria['Mediana_Publicacao'] = contratos.loc[contratos['Publicacao_Valida']].groupby('Categoria')['Intervalo_Publicacao_Dias'].median()

estatisticas_categoria = estatisticas_categoria.sort_values('Quantidade', ascending=False)

# 5. Valores atípicos. O critério IQR global sinaliza casos para examinar,
# mas não comprova irregularidade e não justifica remover valores elevados.
limites_outliers = {}

for coluna, coluna_validade in [('Valor_Global', 'Valor_Valido'), ('Vigencia_Dias', 'Vigencia_Valida'), ('Intervalo_Publicacao_Dias', 'Publicacao_Valida')]:
    serie = contratos.loc[contratos[coluna_validade], coluna]
    primeiro_quartil = serie.quantile(0.25)
    terceiro_quartil = serie.quantile(0.75)
    intervalo_quartis = terceiro_quartil - primeiro_quartil
    limite_inferior = primeiro_quartil - 1.5 * intervalo_quartis
    limite_superior = terceiro_quartil + 1.5 * intervalo_quartis
    contratos['Outlier_' + coluna] = contratos[coluna_validade] & ((contratos[coluna] < limite_inferior) | (contratos[coluna] > limite_superior))
    limites_outliers[coluna] = {}
    limites_outliers[coluna]['inferior'] = float(limite_inferior)
    limites_outliers[coluna]['superior'] = float(limite_superior)
    limites_outliers[coluna]['quantidade'] = int(contratos['Outlier_' + coluna].sum())

# 6. Frequências. As faixas facilitam a comunicação e não são limites legais.
faixas = pd.cut(publicacoes, [-1, 0, 2, 7, 30, float('inf')], labels=['Mesmo dia', '1 a 2 dias', '3 a 7 dias', '8 a 30 dias', 'Mais de 30 dias'])

frequencias = faixas.value_counts(sort=False).rename('Quantidade').to_frame()

frequencias['Percentual'] = frequencias['Quantidade'] / len(publicacoes) * 100

grupos_mensais = contratos.groupby(contratos['Data_Publicacao'].dt.month)
publicacoes_por_mes = pd.DataFrame()
publicacoes_por_mes['Quantidade'] = grupos_mensais['ID_PNCP'].count()
publicacoes_por_mes['Soma_Valor'] = grupos_mensais['Valor_Global'].sum()
# Incluo também os meses sem registros, preenchendo suas contagens com zero.
publicacoes_por_mes = publicacoes_por_mes.reindex(range(1, 13), fill_value=0)

publicacoes_por_mes.index.name = 'Mes_Publicacao'

# Fornecedor é agrupado pelo identificador, não pela grafia do nome. PFs
# receberam códigos no CSV de distribuição. A concentração é por valor
# cadastrado e não permite concluir dependência ou ausência de concorrência.
contratos_valor_valido = contratos.loc[contratos['Valor_Valido']]
grupos_fornecedores = contratos_valor_valido.groupby('ID_Fornecedor')
fornecedores = pd.DataFrame()
fornecedores['Fornecedor'] = grupos_fornecedores['Fornecedor'].first()
fornecedores['Quantidade'] = grupos_fornecedores['ID_PNCP'].count()
fornecedores['Soma_Valor'] = grupos_fornecedores['Valor_Global'].sum()
fornecedores = fornecedores.sort_values('Soma_Valor', ascending=False)

fornecedores['Participacao_Percentual'] = fornecedores['Soma_Valor'] / valores.sum() * 100

pares = contratos.loc[contratos['Valor_Valido'] & contratos['Vigencia_Valida'], ['Valor_Global', 'Vigencia_Dias']]

# corr() monta uma tabela de correlações. loc lê o cruzamento das duas colunas.
correlacoes_pearson = pares.corr(method='pearson')
pearson = float(correlacoes_pearson.loc['Valor_Global', 'Vigencia_Dias'])

correlacoes_spearman = pares.corr(method='spearman')
spearman = float(correlacoes_spearman.loc['Valor_Global', 'Vigencia_Dias'])

# 7. Exportação. JSON resume a análise; CSVs preservam os detalhes para
# conferir números e quais contratos ficaram fora de cada cálculo.
resumo = {}
resumo['fonte'] = 'PNCP'
resumo['instituicao'] = 'Unifesp'
resumo['linhas_coletadas'] = len(dados)
resumo['colunas_entrada'] = 19
resumo['contratos_escopo'] = len(contratos)
resumo['fora_escopo'] = int((~filtro).sum())
resumo['instrumentos'] = dados['Tipo_Instrumento'].value_counts().to_dict()
resumo['receitas_excluidas'] = int(((dados['Tipo_Instrumento'] == 'Contrato (termo inicial)') & dados['Receita']).sum())
resumo['ausentes'] = campos_ausentes
resumo['datas_invalidas'] = datas_invalidas
resumo['estatisticas_valor'] = calcular_estatisticas(valores)
resumo['estatisticas_vigencia'] = calcular_estatisticas(vigencias)
resumo['estatisticas_publicacao'] = calcular_estatisticas(publicacoes)
resumo['publicacoes_inconsistentes'] = int((~contratos['Publicacao_Valida']).sum())
resumo['valores_zero'] = int((valores == 0).sum())
resumo['soma_valor'] = float(valores.sum())
resumo['fornecedores'] = len(fornecedores)
resumo['maior_fornecedor'] = fornecedores.iloc[0]['Fornecedor']
resumo['participacao_top1'] = float(fornecedores['Participacao_Percentual'].iloc[0])
resumo['participacao_top5'] = float(fornecedores['Participacao_Percentual'].head(5).sum())
resumo['limites_outliers'] = limites_outliers
resumo['correlacao_valor_vigencia'] = dict(pearson=pearson, spearman=spearman, pares=len(pares))
resumo['retificados'] = int(contratos['Numero_Retificacoes'].gt(0).sum())
resumo['anos_contrato'] = contratos['Ano_Contrato'].value_counts().to_dict()

pasta_tabelas, pasta_graficos = (pasta_saida / 'analise', pasta_saida / 'graficos')

pasta_tabelas.mkdir(parents=True, exist_ok=True)

pasta_graficos.mkdir(parents=True, exist_ok=True)

# reset_index() coloca o nome do grupo em uma coluna antes de salvar.
tabelas_para_salvar = {
    'base_completa_tratada.csv': dados,
    'contratos_analisados.csv': contratos,
    'fora_do_escopo.csv': dados.loc[~filtro],
    'ocorrencias_qualidade.csv': contratos.loc[contratos['Observacao_Qualidade'] != ''],
    'estatisticas_por_categoria.csv': estatisticas_categoria.reset_index(),
    'frequencias_publicacao.csv': frequencias.reset_index(),
    'publicacoes_por_mes.csv': publicacoes_por_mes.reset_index(),
    'concentracao_fornecedores.csv': fornecedores.reset_index(),
}
for nome_arquivo, tabela in tabelas_para_salvar.items():
    tabela.to_csv(
        pasta_tabelas / nome_arquivo,
        sep=';', index=False, encoding='utf-8-sig',
        date_format='%Y-%m-%dT%H:%M:%S',
    )

(pasta_tabelas / 'resumo.json').write_text(json.dumps(resumo, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')

# 8. Gráficos. As escalas e o tamanho da amostra ficam explícitos para
# evitar comparar visualmente grandezas diferentes ou esconder exceções.
sns.set_theme(style='whitegrid', font_scale=1.05)

plt.rcParams.update({'axes.spines.top': False, 'axes.spines.right': False})

def salvar_grafico(nome):
    """Salva a figura com boa resolução e libera a memória usada."""
    # Ajusto o espaço, salvo o gráfico e fecho a figura.
    plt.tight_layout()
    plt.savefig(pasta_graficos / nome, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close()

plt.figure(figsize=(9, 4.7))

valores_positivos = valores[valores > 0]

sns.histplot(valores_positivos, log_scale=True, bins=20, color=AZUL)

plt.xlabel('Valor global cadastrado (R$, escala logarítmica)')

plt.ylabel('Contratos')

plt.title(f"Distribuição de {len(valores_positivos)} valores positivos; {resumo['valores_zero']} zero à parte")

salvar_grafico('valores_histograma.png')

nomes_curtos = {'Serviços de Engenharia': 'Engenharia', 'Informática (TIC)': 'TIC', 'Locação Imóveis': 'Locação'}

ordem = estatisticas_categoria.index.tolist()

dados_grafico = contratos.copy()

dados_grafico['Categoria_Grafico'] = dados_grafico['Categoria'].replace(nomes_curtos)

categorias_grafico = []
for coluna in ordem:
    categorias_grafico.append(nomes_curtos.get(coluna, coluna))

plt.figure(figsize=(9, 4.7))

sns.boxplot(data=dados_grafico, x='Categoria_Grafico', y='Vigencia_Dias', order=categorias_grafico, color='#8bb7c8')

plt.xticks(rotation=15)

plt.xlabel('Categoria')

plt.ylabel('Vigência cadastrada (dias corridos)')

plt.title('Vigência por categoria de processo')

salvar_grafico('vigencia_boxplot.png')

fig, ax = plt.subplots(figsize=(9, 4.7))

ax.barh(categorias_grafico, estatisticas_categoria['Mediana_Valor'] / 1000, color=AZUL)

ax.invert_yaxis()

# iloc[indice] lê uma linha pela posição, começando em zero.
for indice in range(len(estatisticas_categoria)):
    quantidade = int(estatisticas_categoria.iloc[indice]['Quantidade'])
    mediana = estatisticas_categoria.iloc[indice]['Mediana_Valor']
    if quantidade == 1:
        rotulo = '1 contrato'
    else:
        rotulo = f'{quantidade} contratos'
    ax.text(mediana / 1000 + 30, indice, rotulo, va='center')

ax.set_xlim(0, estatisticas_categoria['Mediana_Valor'].max() / 1000 * 1.28)

ax.set_xlabel('Mediana do valor global (R$ mil)')

ax.set_title('Mediana do valor global por categoria')

salvar_grafico('medianas_categoria.png')

fig, ax = plt.subplots(figsize=(9, 4.7))

ax.barh(frequencias.index.astype(str), frequencias['Percentual'], color=VERDE)

ax.invert_yaxis()

for indice in range(len(frequencias)):
    total_contratos = int(frequencias.iloc[indice]['Quantidade'])
    percentual = frequencias.iloc[indice]['Percentual']
    if total_contratos == 1:
        quantidade = '1 contrato'
    else:
        quantidade = f'{total_contratos} contratos'
    # :.1f apresenta uma casa decimal; replace() usa a vírgula no rótulo.
    rotulo = f'{percentual:.1f}% — {quantidade}'
    rotulo = rotulo.replace('.', ',')
    ax.text(percentual + 1, indice, rotulo, va='center')

ax.set_xlim(0, max(frequencias['Percentual']) * 1.55)

ax.set_xlabel(f'Percentual dos {len(publicacoes)} contratos com intervalo válido (%)')

ax.set_title('Intervalo entre assinatura e publicação')

salvar_grafico('faixas_publicacao.png')

fig, ax = plt.subplots(figsize=(9, 4.7))

cinco_maiores = fornecedores.head(5)

# O gráfico usa posições; a tabela completa identifica os fornecedores.
rotulos_fornecedores = []
for indice in range(len(cinco_maiores)):
    rotulos_fornecedores.append(f'Fornecedor {indice + 1}')
ax.barh(rotulos_fornecedores, cinco_maiores['Participacao_Percentual'], color=AZUL)

ax.invert_yaxis()

for indice in range(len(cinco_maiores)):
    percentual = cinco_maiores.iloc[indice]['Participacao_Percentual']
    rotulo = f'{percentual:.2f}%'.replace('.', ',')
    ax.text(percentual + 1, indice, rotulo, va='center')

ax.set_xlim(0, max(cinco_maiores['Participacao_Percentual']) * 1.2)

ax.set_xlabel('Participação na soma dos valores globais (%)')

ax.set_title('Cinco maiores fornecedores por valor cadastrado')

salvar_grafico('concentracao_fornecedores.png')

plt.figure(figsize=(9, 4.7))

contratos_positivos = dados_grafico[(dados_grafico['Valor_Global'] > 0) & dados_grafico['Vigencia_Valida']]

sns.scatterplot(data=contratos_positivos, x='Valor_Global', y='Vigencia_Dias', hue='Categoria_Grafico', s=45)

plt.xscale('log')

plt.xlabel('Valor global (R$, escala logarítmica)')

plt.ylabel('Vigência cadastrada (dias)')

plt.title(f'Valor e vigência - {len(contratos_positivos)} contratos com valor positivo')

plt.legend(fontsize=8)

salvar_grafico('valor_vigencia.png')

print('Análise concluída.')
print('Contratos analisados:', len(contratos))
print('Intervalos válidos:', len(publicacoes))
print('Tabelas:', pasta_tabelas)
print('Gráficos:', pasta_graficos)
