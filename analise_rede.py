import pandas as pd
import networkx as nx
import re
from itertools import combinations
import community as community_louvain
import matplotlib.pyplot as plt
import unicodedata
import numpy as np

# --- Funções de Processamento de Texto  ---
def _eliminar_tildes(texto):
    nfkd_form = unicodedata.normalize('NFD', texto)
    return "".join([c for c in nfkd_form if unicodedata.category(c) != 'Mn'])

def preprocess_text(text, custom_stopwords=None):
    mapa_normalizacao = {
        'pesquisas': 'pesquisa',
    }
    stop_words = set(['de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as', 'dos',
                      'como', 'mas', 'ao', 'ele', 'das', 'à', 'seu', 'sua', 'ou', 'quando', 'muito', 'nos', 'já', 'eu', 'também', 'só', 'pelo', 'pela',
                      'até', 'isso', 'ela', 'entre', 'depois', 'sem', 'mesmo', 'nas', 'quais', 'sobre'])
    if custom_stopwords:
        stop_words.update(custom_stopwords)
    text = text.lower()
    text = _eliminar_tildes(text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    tokens = text.split()
    normalized_tokens = [mapa_normalizacao.get(token, token) for token in tokens]
    filtered_tokens = [word for word in normalized_tokens if word not in stop_words and len(word) > 2]
    return filtered_tokens

def create_cooccurrence_matrix_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
    documents_raw = content.split('###')
    documents_raw = [doc.strip() for doc in documents_raw if doc.strip()]
    custom_stopwords = ['educacional', 'formacao']
    processed_docs = [preprocess_text(doc, custom_stopwords) for doc in documents_raw]
    vocabulary = sorted(list(set(term for doc in processed_docs for term in doc)))
    M = pd.DataFrame(0, index=vocabulary, columns=vocabulary)
    for doc in processed_docs:
        unique_terms_in_doc = sorted(list(set(doc)))
        for term in unique_terms_in_doc:
            M.loc[term, term] += 1
        for term1, term2 in combinations(unique_terms_in_doc, 2):
            M.loc[term1, term2] += 1
            M.loc[term2, term1] += 1
    return M

def calcular_e_associar_metricas(G, M):
    try:
        partition = community_louvain.best_partition(G, weight='weight')
    except ValueError:
        partition = {n: 0 for n in G.nodes()} # Fallback se o grafo estiver vazio

    pagerank = nx.pagerank(G, weight='weight')
    occurrences = {term: M.loc[term, term] for term in G.nodes()}
    clusters_ajustados = {node: cluster_id + 1 for node, cluster_id in partition.items()}
    nx.set_node_attributes(G, clusters_ajustados, 'cluster')
    nx.set_node_attributes(G, pagerank, 'pagerank')
    nx.set_node_attributes(G, occurrences, 'occurrences')
    print("Métricas (Cluster, PageRank, Ocorrencias) calculadas e associadas.")
    return G

def filtrar_rede(G, top_n, min_edge_weight_for_viz):
    if G.number_of_nodes() <= top_n:
        top_nodes = list(G.nodes())
    else:
        pagerank_dict = nx.get_node_attributes(G, 'pagerank')
        sorted_nodes = sorted(pagerank_dict, key=pagerank_dict.get, reverse=True)
        top_nodes = sorted_nodes[:top_n]
    G_sub = G.subgraph(top_nodes).copy()
    G_final = nx.Graph()
    G_final.add_nodes_from(G_sub.nodes(data=True))
    for u, v, data in G_sub.edges(data=True):
        if data['weight'] >= min_edge_weight_for_viz:
            G_final.add_edge(u, v, weight=data['weight'])
    G_final.remove_nodes_from(list(nx.isolates(G_final)))
    print(f"Rede final: {G_final.number_of_nodes()} nós, {G_final.number_of_edges()} arestas.")
    return G_final


#  FUNÇÃO DE VISUALIZAÇÃO 

def visualizar_rede_estilizada(G, title, output_filename):
    if G.number_of_nodes() == 0:
        print("A rede está vazia.")
        return
    G.remove_edges_from(nx.selfloop_edges(G))

    plt.figure(figsize=(20, 12), facecolor='white')
    ax = plt.gca()

    # --- Layout Centralizado ---
    pagerank_dict = nx.get_node_attributes(G, 'pagerank')
    central_node = max(pagerank_dict, key=pagerank_dict.get)
    pos = nx.spring_layout(G, k=0.5, iterations=10, seed=42)
    pos[central_node] = np.array([0, 0])

    
    for node, coords in pos.items():
        if node != central_node:
            norm = np.linalg.norm(coords)
            if norm == 0: norm = 1
            pos[node] = coords + (coords / norm) * 0.3 # Afasta 30%

  
    cluster_values = [data.get('cluster', 0) for _, data in G.nodes(data=True)]
    cmap = plt.cm.get_cmap('Set1') 

    
    pagerank_values = [data.get('pagerank', 0) for _, data in G.nodes(data=True)]
    min_size = 2000
    max_size = 20000

    node_sizes = []
    if pagerank_values:
        min_pr, max_pr = min(pagerank_values), max(pagerank_values)
        for p in pagerank_values:
            size = min_size + ((p - min_pr) / (max_pr - min_pr + 1e-9)) * (max_size - min_size)
            node_sizes.append(size)

  
    node_list = list(G.nodes())
    central_idx = node_list.index(central_node)
    node_sizes[central_idx] = 25000  

    # --- Desenhar o "Halo" ---
    
    nx.draw_networkx_nodes(
        G, pos,
        node_color=cluster_values, cmap=cmap,
        node_size=[s * 1.2 for s in node_sizes], 
        alpha=0.2, 
        linewidths=0
    )

    # Desenha o núcleo dos nós
    nodes = nx.draw_networkx_nodes(
        G, pos,
        node_color=cluster_values, cmap=cmap,
        node_size=node_sizes,
        alpha=0.7,
        edgecolors='white', linewidths=2
    )

    # ---  Arestas Curvas ---
    edge_weights = [data['weight'] for u, v, data in G.edges(data=True)]
    if edge_weights:
        max_w = max(edge_weights)
        widths = [1 + (w / max_w * 4) for w in edge_weights]
    else:
        widths = 1

    nx.draw_networkx_edges(
        G, pos,
        alpha=0.4,
        width=widths,
        edge_color='#999999',
        connectionstyle="arc3,rad=0.3" 
    )

   
    labels = {}
    for node, data in G.nodes(data=True):
        if node == central_node:
            labels[node] = node.upper() # Caixa alta para o central
        else:
            # Quebra linha se for muito longo
            lbl = node
            if len(lbl) > 10 and ' ' in lbl:
                lbl = lbl.replace(' ', '\n', 1)
            labels[node] = lbl

    nx.draw_networkx_labels(
        G, pos,
        labels={central_node: labels[central_node]},
        font_size=35,
        font_weight='bold',
        font_family='sans-serif',
        font_color='black'
    )

    # Desenha rótulos periféricos
    other_labels = {n: l for n, l in labels.items() if n != central_node}

    pos_labels = {n: (x, y - 0.08) for n, (x, y) in pos.items()}

    size_map = dict(zip(G.nodes(), node_sizes))
    
    for node, label in other_labels.items():
        
        n_size = size_map.get(node, 2000)
        
        font_calc = 10 + (n_size / 1200)
        final_font_size = min(max(font_calc, 10), 24) # Limita entre 10 e 24
        
        nx.draw_networkx_labels(
            G, pos, 
            labels={node: label},
            font_size=final_font_size,
            font_weight='medium',
            font_color='#555555',
            # O bbox ajuda na leitura, especialmente se a fonte variar muito
            bbox=dict(facecolor='white', alpha=0.6, edgecolor='none', pad=0.5)
        )

    plt.title(title, size=18, color='#333333', loc='left')
    plt.axis('off') # Remove eixos
    plt.tight_layout()
    plt.savefig(output_filename, dpi=600, bbox_inches='tight')
    plt.close()
    print(f"\nGráfico '{output_filename}' guardado com estilo curvo e centralizado!")

## ----------------------------------------------------------------
## EXECUÇÃO
## ----------------------------------------------------------------
if __name__ == "__main__":
    # --- Configurações ---
    FILE_PATH = 'OBJETO_DE_COMPARAÇÃO.txt'
    TOP_N_NODES = 25 # Reduzi um pouco para ficar mais limpo como na imagem
    MIN_EDGE_WEIGHT_VIZ = 1
    GRAFICO_TITULO = ""
    GRAFICO_OUTPUT_FILE = "rede_estilo_imagem.png"
    MAPEO_ETIQUETAS_FILE = 'mapeo_terminos.csv'


    # --- 1. Flujo de trabajo estándar (hasta el filtrado) ---
    print("Iniciando análisis...")
    matriz_M = create_cooccurrence_matrix_from_file(FILE_PATH)
    grafo_base = nx.from_pandas_adjacency(matriz_M)
    grafo_com_metricas = calcular_e_associar_metricas(grafo_base, matriz_M)
    grafo_final = filtrar_rede(grafo_com_metricas, top_n=TOP_N_NODES, min_edge_weight_for_viz=MIN_EDGE_WEIGHT_VIZ)

    # --- 2. Exportar nodos para corrección de tildes ---

    # Obtener la lista de nodos del grafo final
    nodos_sin_tildes = list(grafo_final.nodes())

    # Crear un DataFrame de Pandas: original -> corregido
    # Inicialmente, ambas columnas son iguales.
    df_mapa = pd.DataFrame({
        'original_sin_tilde': nodos_sin_tildes,
        'corregido_con_tilde': nodos_sin_tildes
    })

    # Guardar en un archivo CSV
    df_mapa.to_csv(MAPEO_ETIQUETAS_FILE, index=False, encoding='utf-8-sig')

    # --- 3.  Pausa para la edición manual ---
    print("-" * 70)
    print(f"ARCHIVO CREADO: '{MAPEO_ETIQUETAS_FILE}'")
    print("Por favor, abre este archivo CSV (con Excel, Google Sheets, o un editor de texto).")
    print("Modifica la columna 'corregido_con_tilde' para añadir las tildes necesarias.")
    print("-" * 70)

    # Pausa el script y espera a que el usuario presione Enter
    input(">>> PRESIONA ENTER para continuar después de guardar tus cambios... ")

    # --- 4. Importar mapa corregido y re-etiquetar ---
    print("Leyendo el archivo de etiquetas corregido...")

    # Leer el archivo que acabas de editar
    try:
        df_mapa_editado = pd.read_csv(MAPEO_ETIQUETAS_FILE, encoding='utf-8-sig')
    except Exception as e:
        print(f"Error leyendo el archivo {MAPEO_ETIQUETAS_FILE}: {e}")
        print("Asegúrate de que el archivo esté guardado correctamente.")
        exit()

    # Crear el diccionario de mapeo
    mapa_de_etiquetas = pd.Series(
        df_mapa_editado.corregido_con_tilde.values,
        index=df_mapa_editado.original_sin_tilde
    ).to_dict()

    # Aplicar el re-etiquetado al grafo
    grafo_etiquetado = nx.relabel_nodes(grafo_final, mapa_de_etiquetas, copy=True)

    print("Nodos re-etiquetados con éxito.")

    # --- 5. Ejecución del flujo de trabajo (Visualización) ---
    visualizar_rede_estilizada(  
        grafo_etiquetado,
        GRAFICO_TITULO,
        GRAFICO_OUTPUT_FILE
    )
