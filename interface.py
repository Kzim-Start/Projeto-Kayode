"""Componentes visuais compartilhados pelas sete telas."""
import tkinter as tk
from tkinter import ttk

FUNDO = "#f5f5ed"
TEXTO = "#20392e"
VERDE = "#234d3c"
CLARO = "#dce9c4"
FONTE = "Arial"


def tema():
    estilo = ttk.Style()
    estilo.theme_use("clam")
    estilo.configure(".", font=(FONTE, 11))
    estilo.configure("TEntry", padding=7, fieldbackground="white")
    estilo.configure("TCombobox", padding=6, fieldbackground="white")
    estilo.map("TCombobox", fieldbackground=[("readonly", "white")])
    estilo.configure("Treeview", background="white", fieldbackground="white",
                     foreground=TEXTO, rowheight=35, borderwidth=0)
    estilo.configure("Treeview.Heading", background="#e0e8db", foreground=TEXTO,
                     padding=8, font=(FONTE, 10, "bold"), relief="flat")
    estilo.map("Treeview", background=[("selected", VERDE)], foreground=[("selected", "white")])


def texto(pai, mensagem, tamanho=11, negrito=False):
    estilo = "bold" if negrito else "normal"
    return tk.Label(pai, text=mensagem, bg=pai["bg"], fg=TEXTO, anchor="w",
                    font=(FONTE, tamanho, estilo), justify="left")


def titulo(pai, nome, instrucao):
    texto(pai, nome, 29, True).pack(fill="x", pady=(0, 5))
    texto(pai, instrucao).pack(fill="x", pady=(0, 18))


def linha(pai):
    caixa = tk.Frame(pai, bg=pai["bg"])
    caixa.pack(fill="x", pady=(0, 10))
    return caixa


def campo(pai, nome, opcoes=None, editavel=False, largura=18):
    caixa = tk.Frame(pai, bg=pai["bg"])
    caixa.pack(side="left", fill="x", expand=True, padx=(0, 10))
    texto(caixa, nome, 10, True).pack(fill="x", pady=(0, 4))
    if opcoes is None:
        entrada = ttk.Entry(caixa, width=largura)
    else:
        estado = "normal" if editavel else "readonly"
        entrada = ttk.Combobox(caixa, width=largura, values=opcoes, state=estado)
        if opcoes and not editavel:
            entrada.current(0)
    entrada.pack(fill="x")
    return entrada


def botao(pai, nome, comando, secundario=False):
    fundo = CLARO if secundario else VERDE
    cor = TEXTO if secundario else "white"
    tk.Button(pai, text=nome, command=comando, bg=fundo, fg=cor, relief="flat",
              activebackground="#c1d7b4", activeforeground=TEXTO, padx=14, pady=8,
              cursor="hand2", font=(FONTE, 10, "bold")).pack(side="left", padx=(0, 8))


def tabela(pai, colunas, linhas, altura=6):
    caixa = tk.Frame(pai, bg=FUNDO)
    caixa.pack(fill="both", expand=True, pady=(4, 10))
    grade = ttk.Treeview(caixa, columns=colunas, show="headings", height=altura, selectmode="browse")
    barra = ttk.Scrollbar(caixa, orient="vertical", command=grade.yview)
    grade.configure(yscrollcommand=barra.set)
    barra.pack(side="right", fill="y")
    grade.pack(fill="both", expand=True)
    for coluna in colunas:
        grade.heading(coluna, text=coluna, anchor="w")
        grade.column(coluna, width=110, minwidth=50, anchor="w")
    for registro in linhas:
        grade.insert("", "end", values=registro)
    return grade
