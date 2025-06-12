# sistema_escola_pokemon.py

import json
import requests
import sqlite3
import streamlit as st
import pandas as pd
from ollama import Client

# ----------------------------------------------------------------------------------------------------------------------
# CRIAÇÃO DO BANCO E TABELAS
conexao = sqlite3.connect("escola_pokemon.db")
cursor = conexao.cursor()

#TABELA POKEMONS
cursor.execute("""
CREATE TABLE IF NOT EXISTS pokemons (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    tipo TEXT,
    altura INTEGER,
    peso INTEGER
)
""")

#TABELA ALUNO
cursor.execute("""
CREATE TABLE IF NOT EXISTS aluno (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    idade INTEGER,
    curso TEXT,
    email TEXT UNIQUE
)
""")

#TABELA ALUNO POKEMON
cursor.execute("""
CREATE TABLE IF NOT EXISTS aluno_pokemon (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER,
    pokemon_id INTEGER,
    FOREIGN KEY (aluno_id) REFERENCES aluno(id),
    FOREIGN KEY (pokemon_id) REFERENCES pokemons(id)
)
""")
conexao.commit()
conexao.close()

# ----------------------------------------------------------------------------------------------------------------------
# FUNÇÕES

#CADASTRO ALUNO
def cadastro_aluno():
    conexao = sqlite3.connect("escola_pokemon.db")
    cursor = conexao.cursor()

    nome = input("Nome do aluno: ")
    idade = int(input("Idade: "))
    curso = input("Curso: ")
    email = input("Email: ")

    try:
        cursor.execute("""
        INSERT INTO aluno(nome, idade, curso, email) VALUES(?, ?, ?, ?)""", (nome, idade, curso, email))
        conexao.commit()
        print("Aluno cadastrado com sucesso!")
    except Exception as e:
        print("Erro ao cadastrar aluno:", e)
    finally:
        conexao.close()

#CADASTRO POKEMON
def cadastrar_pokemon():
    conexao = sqlite3.connect("escola_pokemon.db")
    cursor = conexao.cursor()

    id_pokemon = int(input("ID do Pokemon: "))
    nome = input("Nome: ")
    tipo = input("Tipo: ")
    altura = int(input("Altura: "))
    peso = int(input("Peso: "))

    try:
        cursor.execute("""
        INSERT OR REPLACE INTO pokemons (id, nome, tipo, altura, peso)
        VALUES(?, ?, ?, ?, ?)
        """, (id_pokemon, nome, tipo, altura, peso))
        conexao.commit()
        print("Pokemon cadastrado com sucesso!")
    except Exception as e:
        print("Erro ao cadastrar Pokemon:", e)
    finally:
        conexao.close()

#CADASTRO POKEMON DA API
def cadastrar_pokemon_da_api():
    nome_ou_id = input("Digite o nome ou ID do Pokemon para cadastrar: ").lower()
    url = f"https://pokeapi.co/api/v2/pokemon/{nome_ou_id}"

    try:
        resposta = requests.get(url)
        if resposta.status_code == 200:
            dados = resposta.json()
            id_pokemon = dados["id"]
            nome = dados["name"]
            altura = dados["height"]
            peso = dados["weight"]
            tipos = ', '.join([t["type"]["name"] for t in dados["types"]])

            conexao = sqlite3.connect("escola_pokemon.db")
            cursor = conexao.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO pokemons (id, nome, tipo, altura, peso)
            VALUES (?, ?, ?, ?, ?)""", (id_pokemon, nome, tipos, altura, peso))
            conexao.commit()
            print(f"Pokemon '{nome}' cadastrado com sucesso via API!")
        else:
            print("Pokemon não encontrado na API.")
    except Exception as e:
        print("Erro ao cadastrar Pokemon via API:", e)
    finally:
        conexao.close()


#CONSULTA DE POKEMONS
def consultar_pokemons_api():
    nome_ou_id = input("Digite o nome ou ID do Pokemon: ").lower()
    url = f"https://pokeapi.co/api/v2/pokemon/{nome_ou_id}"

    try:
        resposta = requests.get(url)
        if resposta.status_code == 200:
            dados = resposta.json()
            print("\n====== INFORMAÇÕES POKEMON ======")
            print(f"ID: {dados['id']}")
            print(f"Nome: {dados['name']}")
            print(f"Tipos: {', '.join([t['type']['name'] for t in dados['types']])}")
            print(f"Altura: {dados['height']}")
            print(f"Peso: {dados['weight']}")
        else:
            print("Pokemon não encontrado na API.")
    except Exception as e:
        print("Erro ao consultar Pokemon:", e)


#VISUALIZAÇÃO DE POKEMONS
def visualizar_pokemons():
    conexao = sqlite3.connect("escola_pokemon.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM pokemons")
    pokemons = cursor.fetchall()
    conexao.close()

    if pokemons:
        print("\n==== Lista de Pokemons ====")
        for p in pokemons:
            print(f"ID: {p[0]}, Nome: {p[1]}, Tipo: {p[2]}, Altura: {p[3]}, Peso: {p[4]}")
    else:
        print("Nenhum Pokemon cadastrado.")


#ATRIBUIÇÃO DO POKEMON AO ALUNO
def atribuir_pokemon_a_aluno():
    conexao = sqlite3.connect("escola_pokemon.db")
    cursor = conexao.cursor()

    cursor.execute("SELECT id, nome FROM aluno")
    alunos = cursor.fetchall()
    print("\n==== Alunos ====")
    for aluno in alunos:
        print(f"{aluno[0]} - {aluno[1]}")
    aluno_id = int(input("Digite o ID do aluno que vai receber o Pokemon: "))

    cursor.execute("SELECT id, nome FROM pokemons")
    pokemons = cursor.fetchall()
    print("\n==== Pokemons ====")
    for p in pokemons:
        print(f"{p[0]} - {p[1]}")
    pokemon_id = int(input("Digite o ID do Pokemon a ser atribuído: "))

    try:
        cursor.execute("""
        INSERT INTO aluno_pokemon (aluno_id, pokemon_id)
        VALUES (?, ?)""", (aluno_id, pokemon_id))
        conexao.commit()
        print("Pokemon atribuído ao aluno com sucesso!")
    except Exception as e:
        print("Erro ao atribuir Pokemon:", e)
    finally:
        conexao.close()

#LISTA DE ALUNOS COM POKEMON
def listar_alunos_com_pokemons():
    conexao = sqlite3.connect("escola_pokemon.db")
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT a.id, a.nome, a.email, p.nome
        FROM aluno a
        LEFT JOIN aluno_pokemon ap ON a.id = ap.aluno_id
        LEFT JOIN pokemons p ON ap.pokemon_id = p.id
        ORDER BY a.id
    """)
    resultados = cursor.fetchall()
    conexao.close()

    if resultados:
        print("\n==== Alunos e seus Pokemons ====")
        ultimo_aluno_id = None
        for aluno_id, aluno_nome, email, pokemon_nome in resultados:
            if aluno_id != ultimo_aluno_id:
                print(f"\nAluno: {aluno_nome} ({email})\nPokemons:")
                ultimo_aluno_id = aluno_id
            print(f" - {pokemon_nome if pokemon_nome else 'Nenhum Pokemon atribuído.'}")
    else:
        print("Nenhum aluno encontrado.")

# ----------------------------------------------------------------------------------------------------------------------

#INTEGRAÇÃO DA IA

def perguntar_ia_ollama(pergunta):
    client = Client(host='http://localhost:11434')
    prompt = f"Responda em Português do Brasil: {pergunta}"
    resposta = client.chat(model='orca-mini',messages=[{"role": "user", "content": prompt}])
    return resposta['message']['content']

# ----------------------------------------------------------------------------------------------------------------------

st.set_page_config(page_title= "Escola Pokémon", layout="wide")

st.title("Escola Pokémon - Dashboard")

#CONECTAR BANCO
conn = sqlite3.connect("escola_pokemon.db")

#DADOS ALUNOS E POKEMONS
df = pd.read_sql_query("""
SELECT a.nome AS Aluno, a.curso AS Curso, p.nome AS Pokemon, p.tipo AS Tipo
FROM aluno a
LEFT JOIN aluno_pokemon ap ON a.id = ap.aluno_id
LEFT JOIN pokemons p ON ap.pokemon_id = p.id
""", conn)

#MOSTRA A TABELA
st.subheader("Aluno e seus Pokemons")
st.dataframe(df)

#GRAFICO DE POKEMONS MAIS COMUNS
if not df['Pokemon'].isnull().all():
    st.subheader("Pokemons Mais Atribuídos")
    grafico = df['Pokemon'].value_counts().head(10)
    st.bar_chart(grafico)

#RELATORIO COM IA
if st.button("Gerar Relatório com IA"):
    prompt = df.to_string(index=False)
    resposta = perguntar_ia_ollama("Gere relatório resumido com base nestes dados: \n" + prompt)
    st.markdown("### Relatório da IA")
    st.write(resposta)

conn.close()

# ----------------------------------------------------------------------------------------------------------------------
# MENU PRINCIPAL
while True:
    print("\n====== MENU ======")
    print("1 - Cadastrar Aluno")
    print("2 - Cadastrar Pokemon manualmente")
    print("3 - Cadastrar Pokemon da API")
    print("4 - Consultar Pokemon direto da API")
    print("5 - Visualizar Pokemons")
    print("6 - Atribuir Pokemon a Aluno")
    print("7 - Ver alunos e seus Pokemons")
    print("8 - Perguntar algo à IA?")
    print("0 - Sair")

    opcao = input("Escolha uma opção: ")

    if opcao == "1":
        cadastro_aluno()
    elif opcao == "2":
        cadastrar_pokemon()
    elif opcao == "3":
        cadastrar_pokemon_da_api()
    elif opcao == "4":
        consultar_pokemons_api()
    elif opcao == "5":
        visualizar_pokemons()
    elif opcao == "6":
        atribuir_pokemon_a_aluno()
    elif opcao == "7":
        listar_alunos_com_pokemons()
    elif opcao == "8":
        pergunta = input("Digita sua pergunta para IA: ")
        resposta = perguntar_ia_ollama(pergunta)
        print("\nIA respondeu: \n", resposta)
    elif opcao == "0":
        print("Encerrando programa.")
        break
    else:
        print("Opção inválida. Tente novamente.")
