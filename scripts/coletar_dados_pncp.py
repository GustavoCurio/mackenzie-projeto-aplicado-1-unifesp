"""Coleta os registros reais da Unifesp no PNCP publicados em 2025.

Execute: python scripts/coletar_dados_pncp.py
A coleta pode ser executada para atualizar a base.
O CSV incluído no projeto permite reproduzir os resultados do relatório.
"""

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


# 1. Definir a instituição, o período e as pastas
pasta_projeto = Path(__file__).resolve().parents[1]
pasta_dados = pasta_projeto / 'dados'
pasta_backup = pasta_projeto / '.backup_local' / 'pncp_bruto'
pasta_dados.mkdir(parents=True, exist_ok=True)
pasta_backup.mkdir(parents=True, exist_ok=True)
endereco_api = 'https://pncp.gov.br/api/consulta/v1/contratos'
cnpj_unifesp = '60453032000174'


# 2. Ler todas as páginas da API
# A API divide o resultado em páginas. O while continua até a última página.
pagina = 1
registros = []
fontes = []
total_esperado = None

while True:
    parametros = {
        'dataInicial': '20250101',
        'dataFinal': '20251231',
        'cnpjOrgao': cnpj_unifesp,
        'pagina': pagina,
        'tamanhoPagina': 500,
    }
    # urlencode() transforma os parâmetros em parte do endereço da consulta.
    endereco_consulta = endereco_api + '?' + urlencode(parametros)
    pedido = Request(endereco_consulta, headers={
        'Accept': 'application/json',
        'User-Agent': 'Projeto-Aplicado-I/1.0',
    })
    # Se a API estiver indisponível, a execução para e pode ser reiniciada.
    with urlopen(pedido, timeout=60) as resposta:
        conteudo = resposta.read()
    resultado = json.loads(conteudo)

    if pagina == 1:
        total_esperado = resultado['totalRegistros']
    if resultado['totalRegistros'] != total_esperado:
        raise ValueError('A consulta mudou durante a coleta. Execute novamente.')

    nome_backup = f'pncp_unifesp_publicacao_2025_pagina_{pagina}.json'
    (pasta_backup / nome_backup).write_bytes(conteudo)
    fonte = {}
    fonte['url'] = endereco_consulta
    fonte['arquivo_local'] = '.backup_local/pncp_bruto/' + nome_backup
    fonte['sha256'] = hashlib.sha256(conteudo).hexdigest()
    fonte['registros'] = len(resultado['data'])
    fontes.append(fonte)
    registros.extend(resultado['data'])
    print('Página', pagina, ':', len(resultado['data']), 'registros.')

    if pagina >= resultado['totalPaginas']:
        break
    pagina = pagina + 1


# 3. Conferir o total, a instituição e o período
if len(registros) != total_esperado:
    raise ValueError('O total coletado não confere com o total da API.')
if len(registros) == 0:
    raise ValueError('A consulta não retornou registros.')
for registro in registros:
    if registro['orgaoEntidade']['cnpj'] != cnpj_unifesp:
        raise ValueError('A consulta trouxe registros de outra instituição.')
    if not registro['dataPublicacaoPncp'].startswith('2025-'):
        raise ValueError('A consulta trouxe publicação fora de 2025.')


# 4. Criar códigos para fornecedores que são pessoas físicas
# Nomes e documentos de pessoas físicas são substituídos por códigos no CSV.
# A lista ordenada mantém o mesmo código para a mesma pessoa nesta coleta.
documentos_pf = []
for registro in registros:
    documento = registro['niFornecedor']
    if registro['tipoPessoa'] == 'PF' and documento not in documentos_pf:
        documentos_pf.append(documento)
documentos_pf.sort()
codigos_pf = {}
for posicao, documento in enumerate(documentos_pf, start=1):
    codigos_pf[documento] = f'PF_{posicao:03d}'


# 5. Selecionar as 19 colunas do estudo
linhas_csv = []
for registro in registros:
    identificador = registro['niFornecedor']
    nome_fornecedor = registro['nomeRazaoSocialFornecedor']
    if registro['tipoPessoa'] == 'PF':
        identificador = codigos_pf[registro['niFornecedor']]
        nome_fornecedor = 'Fornecedor pessoa física ' + identificador

    linha = {}
    linha['ID_PNCP'] = registro['numeroControlePNCP']
    linha['Numero_Contrato'] = registro['numeroContratoEmpenho']
    linha['Ano_Contrato'] = registro['anoContrato']
    linha['CNPJ_Orgao'] = registro['orgaoEntidade']['cnpj']
    linha['Orgao'] = registro['orgaoEntidade']['razaoSocial']
    linha['Unidade'] = registro['unidadeOrgao']['nomeUnidade']
    linha['Categoria'] = registro['categoriaProcesso']['nome']
    linha['Tipo_Instrumento'] = registro['tipoContrato']['nome']
    linha['Receita'] = registro['receita']
    linha['Tipo_Pessoa_Fornecedor'] = registro['tipoPessoa']
    linha['ID_Fornecedor'] = identificador
    linha['Fornecedor'] = nome_fornecedor
    linha['Valor_Inicial'] = registro['valorInicial']
    linha['Valor_Global'] = registro['valorGlobal']
    linha['Data_Assinatura'] = registro['dataAssinatura']
    linha['Data_Publicacao'] = registro['dataPublicacaoPncp']
    linha['Data_Vigencia_Inicio'] = registro['dataVigenciaInicio']
    linha['Data_Vigencia_Fim'] = registro['dataVigenciaFim']
    linha['Numero_Retificacoes'] = registro['numeroRetificacao']
    linhas_csv.append(linha)


# 6. Salvar o CSV
arquivo_csv = pasta_dados / 'contratos_unifesp_pncp_2025.csv'
nomes_colunas = list(linhas_csv[0].keys())
with arquivo_csv.open('w', encoding='utf-8-sig', newline='') as arquivo:
    escritor = csv.DictWriter(arquivo, fieldnames=nomes_colunas, delimiter=';')
    escritor.writeheader()
    escritor.writerows(linhas_csv)


# 7. Registrar a origem para permitir a conferência da coleta
# O hash é um resumo digital usado para conferir se o arquivo foi alterado.
metadados = {}
metadados['fonte'] = 'Portal Nacional de Contratações Públicas (PNCP)'
metadados['instituicao'] = 'Universidade Federal de São Paulo (Unifesp)'
metadados['cnpj_orgao'] = cnpj_unifesp
metadados['endpoint'] = endereco_api
metadados['data_coleta_utc'] = datetime.now(timezone.utc).isoformat()
metadados['recorte'] = 'Contratos/empenhos publicados no PNCP entre 01/01/2025 e 31/12/2025'
metadados['campo_filtro'] = 'dataPublicacaoPncp'
metadados['registros'] = len(registros)
metadados['paginas'] = len(fontes)
metadados['fontes'] = fontes
metadados['arquivo_distribuido'] = arquivo_csv.name
metadados['sha256_csv'] = hashlib.sha256(arquivo_csv.read_bytes()).hexdigest()
metadados['colunas_csv'] = len(nomes_colunas)
metadados['fornecedores_pf_pseudonimizados'] = len(documentos_pf)
metadados['observacao'] = 'Valores e vigências refletem o cadastro disponível na coleta, inclusive retificações. Publicação não significa assinatura em 2025.'
texto_metadados = json.dumps(metadados, ensure_ascii=False, indent=2)
(pasta_dados / 'metadados_coleta.json').write_text(texto_metadados, encoding='utf-8')
print('Coleta concluída:', len(registros), 'registros reais.')
