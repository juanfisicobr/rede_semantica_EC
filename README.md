# Análise de Redes Semânticas em Educação Comparada

Este repositório contém o código-fonte, os dados brutos e os dados tratados utilizados para o mapeamento das estratégias metodológicas em pesquisas de Educação Comparada no Brasil. O projeto emprega uma abordagem híbrida que integra **Mineração de Texto** (*Text Mining*) e **Teoria dos Grafos** para revelar a estrutura cognitiva e os eixos temáticos de teses e dissertações da área.

## 📋 Sobre o Projeto

O objetivo deste *script* é processar dados textuais (títulos, resumos ou objetos de estudo), calcular métricas de relevância e agrupamento, e gerar visualizações de redes semânticas. Diferente de nuvens de palavras tradicionais, este método preserva e destaca o contexto relacional dos termos, permitindo uma análise estrutural do campo científico.

**Principais funcionalidades:**

* **Pré-processamento:** Limpeza de texto, remoção de *stop words*, normalização e lematização básica.
* **Matriz de Coocorrência:** Identificação de termos que aparecem conjuntamente no mesmo contexto documental.
* **Métricas de Rede:**
    * **PageRank:** Determina a centralidade e a relevância estrutural dos termos.
    * **Louvain Modularity:** Detecta comunidades (clusters temáticos) densamente conectados.
* **Interatividade:** Permite a correção manual de acentuação (via CSV) antes da plotagem final, garantindo rigor ortográfico.
* **Visualização:** Gera grafos estilizados com layout centralizado, arestas curvas e distinção visual por cores (comunidades) e tamanhos (relevância).

## 🛠️ Tecnologias Utilizadas

O projeto foi desenvolvido em **Python 3** utilizando as seguintes bibliotecas para análise de dados e redes complexas:

* `pandas`: Manipulação de dados estruturados e I/O de arquivos.
* `networkx`: Criação, manipulação e estudo da estrutura e dinâmica das redes.
* `python-louvain` (`community`): Implementação do algoritmo de detecção de comunidades.
* `matplotlib`: Geração das visualizações gráficas de alta resolução.
* `numpy`: Computação científica e operações numéricas.

## 📦 Instalação e Requisitos

Para executar o código, certifique-se de ter o Python instalado. Recomenda-se o uso de um ambiente virtual (venv). Instale as dependências necessárias com o comando:

```bash
pip install pandas networkx python-louvain matplotlib numpy
```

## 🚀 Como Usar

O *script* foi desenhado para funcionar de maneira semi-automática, permitindo intervenção humana para refinamento ortográfico dos termos extraídos.

### 1. Preparação dos Dados
Crie um arquivo de texto chamado `OBJETO_DE_COMPARAÇÃO.txt` na raiz do projeto.

* **Conteúdo:** O arquivo deve conter os textos a serem analisados (resumos, objetos de estudo, palavras-chave).
* **Delimitador:** Cada documento individual deve ser separado pela sequência de caracteres `###`.

**Exemplo do `OBJETO_DE_COMPARAÇÃO.txt`:**

```text
### Análise comparada de currículos no Brasil e Portugal...

### Políticas públicas de formação docente no Chile e Argentina...

### Estudo sobre gestão escolar em escolas públicas...
```
### 2. Execução
Execute o script Python:

```Bash

python analise_rede.py
```

### 3. Etapa Interativa (Correção de Acentos)
Durante a execução, o script irá parar e exibir a seguinte mensagem:
```text
>>> PRESIONA ENTER para continuar depois de guardar tus cambios...
```

Neste momento, o script gerou um arquivo chamado mapeo_terminos.csv.

Abra este CSV (Excel, LibreOffice ou editor de texto).

A coluna original_sin_tilde contém os termos processados (sem acento).

Edite a coluna corregido_con_tilde inserindo os acentos corretos (ex: mude "politica" para "Política").

Salve o arquivo CSV (mantenha o mesmo nome).

Volte ao terminal e pressione ENTER.

###  4. Resultado
O *script* finalizará o processamento e gerará o arquivo de imagem:

* `rede_estilo_imagem.png`: A visualização final da rede semântica em alta resolução (600 DPI).



## 📂 Estrutura do Repositório

```text
.
├── analise_rede.py          # Código-fonte principal (Script Python)
├── OBJETO_DE_COMPARAÇÃO.txt # Dados de entrada (Corpus textual bruto)
├── mapeo_terminos.csv       # Arquivo intermediário para correção manual de termos
├── rede_estilo_imagem.png   # Saída gráfica (Visualização da rede final)
└── README.md                # Documentação do projeto
```
## 📄 Ciência Aberta e Transparência
Em consonância com os princípios da Ciência Aberta, este repositório disponibiliza não apenas o código, mas também os dados brutos e tratados utilizados na pesquisa. Isso permite a auditabilidade do processo metodológico e a replicabilidade dos grafos apresentados no artigo.

## ⚖️ Licença
Este projeto está sob a licença MIT. Sinta-se à vontade para utilizar, modificar e distribuir o código para fins acadêmicos e de pesquisa, mediante a devida citação. Teran Briceno, Juan e Tauchen, Gionara (2025). Mapeamento de Redes Semânticas em Educação Comparada Python. GitHub. https://github.com/juanfisicobr/rede_semantica_EC
