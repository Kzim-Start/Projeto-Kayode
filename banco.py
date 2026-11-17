"""Conexão com o MySQL e operações que precisam ser salvas juntas."""
from configparser import ConfigParser
from contextlib import contextmanager
from pathlib import Path

import pymysql


@contextmanager
def transacao():
    config = ConfigParser(interpolation=None)
    if not config.read(Path(__file__).with_name("config.ini"), encoding="utf-8"):
        raise ValueError("Copie config.exemplo.ini para config.ini e informe os dados do MySQL.")
    dados = config["mysql"]
    conexao = pymysql.connect(host=dados["host"], port=dados.getint("porta"),
                              user=dados["usuario"], password=dados["senha"],
                              database=dados["banco"], charset="utf8mb4", connect_timeout=5)
    try:
        with conexao.cursor() as cursor:
            yield cursor
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def consultar(sql, valores=()):
    with transacao() as cursor:
        cursor.execute(sql, valores)
        return cursor.fetchall()


def gravar(sql, valores):
    with transacao() as cursor:
        cursor.execute(sql, valores)


def id_alimento(cursor, nome):
    # A mesma grafia identifica o alimento nas doações e nas receitas.
    cursor.execute("""INSERT INTO alimento (nome) VALUES (%s)
                      ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)""", (nome,))
    return cursor.lastrowid


def oferecer(doador, alimento, peso, validade, retirada):
    with transacao() as cursor:
        codigo = id_alimento(cursor, alimento)
        cursor.execute("""INSERT INTO lote (doador_id, alimento_id, oferecido_g, validade, retirada)
                          VALUES (%s, %s, %s, %s, %s)""", (doador, codigo, peso, validade, retirada))


def conferir(lote, peso):
    with transacao() as cursor:
        cursor.execute("""SELECT oferecido_g, validade < CURRENT_DATE, situacao
                          FROM lote WHERE id = %s FOR UPDATE""", (lote,))
        oferecido, vencido, situacao = cursor.fetchone()
        if situacao != "Pendente":
            raise ValueError("Este lote já foi conferido.")
        if peso > oferecido or (peso > 0 and vencido):
            raise ValueError("Confira a validade e o peso oferecido antes de receber.")
        situacao = "Recebido" if peso else "Recusado"
        cursor.execute("""UPDATE lote SET recebido_g=%s, saldo_g=%s, situacao=%s
                          WHERE id=%s""", (peso, peso, situacao, lote))


def salvar_receita(nome, itens):
    if not itens:
        raise ValueError("Adicione pelo menos um ingrediente.")
    with transacao() as cursor:
        cursor.execute("INSERT INTO receita (nome) VALUES (%s)", (nome,))
        receita = cursor.lastrowid
        for alimento, gramas in itens:
            codigo = id_alimento(cursor, alimento)
            cursor.execute("INSERT INTO ingrediente VALUES (%s, %s, %s)", (receita, codigo, gramas))


def planejar(receita):
    linhas = consultar("""
        SELECT a.nome, i.gramas, COALESCE(SUM(l.saldo_g), 0)
        FROM ingrediente i JOIN alimento a ON a.id = i.alimento_id
        LEFT JOIN lote l ON l.alimento_id = a.id AND l.situacao = 'Recebido'
             AND (l.validade IS NULL OR l.validade >= CURRENT_DATE)
        WHERE i.receita_id = %s GROUP BY a.id, a.nome, i.gramas ORDER BY a.nome
    """, (receita,))
    # Cada ingrediente rende uma quantidade. O menor rendimento limita a receita.
    rendimentos = [int(saldo) // gramas for nome, gramas, saldo in linhas]
    return min(rendimentos, default=0), linhas


def produzir(receita, quantidade):
    with transacao() as cursor:
        cursor.execute("""SELECT alimento_id, gramas FROM ingrediente
                          WHERE receita_id=%s ORDER BY alimento_id""", (receita,))
        ingredientes = cursor.fetchall()
        if not ingredientes or quantidade <= 0:
            raise ValueError("Selecione uma receita e informe uma quantidade positiva.")
        cursor.execute("""INSERT INTO producao (receita_id, quantidade, dia)
                          VALUES (%s, %s, CURRENT_DATE)""", (receita, quantidade))
        producao = cursor.lastrowid
        for alimento, gramas in ingredientes:
            falta = gramas * quantidade
            # Bloqueia os lotes durante a baixa. Os que vencem primeiro saem primeiro.
            cursor.execute("""SELECT id, saldo_g FROM lote WHERE alimento_id=%s
                              AND situacao='Recebido' AND saldo_g > 0
                              AND (validade IS NULL OR validade >= CURRENT_DATE)
                              ORDER BY validade IS NULL, validade, id FOR UPDATE""", (alimento,))
            for lote, saldo in cursor.fetchall():
                usado = min(falta, saldo)
                cursor.execute("UPDATE lote SET saldo_g=saldo_g-%s WHERE id=%s", (usado, lote))
                cursor.execute("INSERT INTO consumo VALUES (%s, %s, %s)", (producao, lote, usado))
                falta -= usado
                if falta == 0:
                    break
            if falta:
                raise ValueError("Estoque insuficiente. Consulte o rendimento disponível.")


def entregar(producao, destino, quantidade):
    with transacao() as cursor:
        cursor.execute("SELECT quantidade FROM producao WHERE id=%s FOR UPDATE", (producao,))
        preparado = cursor.fetchone()[0]
        cursor.execute("SELECT COALESCE(SUM(quantidade),0) FROM entrega WHERE producao_id=%s", (producao,))
        entregue = cursor.fetchone()[0]
        if quantidade <= 0 or quantidade > preparado - entregue:
            raise ValueError("A quantidade deve estar dentro do saldo desta produção.")
        cursor.execute("""INSERT INTO entrega (producao_id, destino_id, quantidade, dia)
                          VALUES (%s, %s, %s, CURRENT_DATE)""", (producao, destino, quantidade))
