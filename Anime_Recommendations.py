import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import tkinter as tk
from tkinter import ttk, messagebox

# Carregar os datasets
anime = pd.read_csv('anime.csv')
avaliacoes = pd.read_csv('rating.csv')

# Selecionar colunas relevantes
anime = anime[['anime_id', 'name', 'genre', 'type', 'episodes', 'rating']]
anime.rename(columns={'anime_id': 'ID_ANIME', 'name': 'TITULO', 'genre': 'GENERO',
                      'type': 'TIPO', 'episodes': 'EPISODIOS', 'rating': 'QT_AVALIACOES'}, inplace=True)

avaliacoes = avaliacoes[['user_id', 'anime_id', 'rating']]
avaliacoes.rename(columns={'user_id': 'ID_USUARIO', 'anime_id': 'ID_ANIME', 'rating': 'AVALIACOES'}, inplace=True)

# Remover valores nulos
anime.dropna(inplace=True)

# Filtrar usuários com mais de 500 avaliações
qt_avalicoes = avaliacoes['ID_USUARIO'].value_counts()
usuarios_ativos = qt_avalicoes[qt_avalicoes > 500].index
avaliacoes = avaliacoes[avaliacoes['ID_USUARIO'].isin(usuarios_ativos)]

# Filtrar animes com mais de 500 avaliações
contagem_avaliacoes = avaliacoes.groupby('ID_ANIME').count()['AVALIACOES']
anime = anime[anime['ID_ANIME'].isin(contagem_avaliacoes[contagem_avaliacoes > 500].index)]

# Unindo as avaliações com os animes
avaliacoes_e_anime = avaliacoes.merge(anime, on='ID_ANIME')
avaliacoes_e_anime.drop_duplicates(['ID_USUARIO', 'ID_ANIME'], inplace=True)
del avaliacoes_e_anime['ID_ANIME']

# Criar a matriz de pivotagem
anime_pivot = avaliacoes_e_anime.pivot_table(columns='ID_USUARIO', index='TITULO', values='AVALIACOES')
anime_pivot.fillna(0, inplace=True)

# Criando o modelo de recomendação KNN
modelo = NearestNeighbors(algorithm='brute', metric='cosine')
modelo.fit(anime_pivot)

# Função para recomendar animes e exibir na tabela
def recomendar():
    nome_anime = entrada.get().strip()
    tabela.delete(*tabela.get_children())  # Limpa os resultados anteriores

    if nome_anime in anime_pivot.index:
        distances, sugestions = modelo.kneighbors(anime_pivot.loc[[nome_anime]].values.reshape(1, -1))
        for i in sugestions[0][1:6]:  # Pegamos os 5 animes mais similares
            titulo = anime_pivot.index[i]
            genero = anime.loc[anime['TITULO'] == titulo, 'GENERO'].values[0] if titulo in anime['TITULO'].values else "Desconhecido"
            episodios = anime.loc[anime['TITULO'] == titulo, 'EPISODIOS'].values[0] if titulo in anime['TITULO'].values else "?"

            # Adiciona os dados na tabela
            tabela.insert("", "end", values=(titulo, genero, episodios))
    else:
        messagebox.showerror("Erro", f"Anime '{nome_anime}' não encontrado.")

# Criando a interface gráfica com Tkinter
janela = tk.Tk()
janela.title("Recomendador de Animes")
janela.geometry("700x500")
janela.configure(bg="#282c34")  # Cor de fundo escuro

# Estilo para os widgets
style = ttk.Style()
style.configure("TButton", font=("Arial", 12, "bold"), padding=5, foreground="black")
style.configure("TLabel", font=("Arial", 12, "bold"), foreground="black")
style.configure("TEntry", font=("Arial", 12))

# Criando os widgets
frame = ttk.Frame(janela, padding=20, style="TFrame")
frame.pack(expand=True)

label = ttk.Label(frame, text="Digite o nome do anime:", style="TLabel")
label.grid(row=0, column=0, padx=5, pady=5)

entrada = ttk.Entry(frame, width=40)
entrada.grid(row=1, column=0, padx=10, pady=5)

botao = ttk.Button(frame, text="Recomendar", command=recomendar, style="TButton")
botao.grid(row=2, column=0, padx=10, pady=10)

# Criando frame para a tabela
tabela_frame = ttk.Frame(janela)
tabela_frame.pack(pady=10)

# Criando barra de rolagem
scroll_y = ttk.Scrollbar(tabela_frame, orient="vertical")
scroll_x = ttk.Scrollbar(tabela_frame, orient="horizontal")

# Criando a tabela estilizada
colunas = ("Título", "Gênero", "Episódios")
tabela = ttk.Treeview(
    tabela_frame, columns=colunas, show="headings",
    height=8, yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set
)

# Configurar rolagem
scroll_y.config(command=tabela.yview)
scroll_x.config(command=tabela.xview)

# Posicionar rolagem
scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")

# Definir cabeçalhos das colunas em NEGRITO e centralizados
for col in colunas:
    tabela.heading(col, text=col, anchor="center")
    tabela.column(col, width=200, anchor="center")

# Criar cores alternadas nas linhas da tabela
style.configure("Treeview", font=("Arial", 11))
style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#4a4e69", foreground="black")
tabela.tag_configure('oddrow', background="#3a3d4a")  # Cinza escuro
tabela.tag_configure('evenrow', background="#232531")  # Azul escuro

tabela.pack()

# Iniciar a interface gráfica
janela.mainloop()
