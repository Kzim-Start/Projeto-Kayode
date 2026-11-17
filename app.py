"""Projeto Kayode. Execute com python app.py."""
import tkinter as tk
from datetime import datetime, date
from decimal import Decimal, InvalidOperation

import pymysql

import banco
from interface import CLARO, FONTE, FUNDO, TEXTO, VERDE, botao, campo, linha, tabela, tema, texto, titulo


def nome(entrada, limite=100):
    valor = entrada.get().strip()
    if not valor or len(valor) > limite:
        raise ValueError(f"Preencha o campo de texto com até {limite} caracteres.")
    return valor


def numero(entrada, fator=1):
    # Em kg, 2,4 vira 2400 gramas. No cálculo só usamos números inteiros.
    try:
        valor = Decimal(entrada.get().strip().replace(",", ".")) * fator
    except (InvalidOperation, OverflowError):
        raise ValueError("Informe uma quantidade numérica válida.") from None
    if not valor.is_finite() or not 0 < valor <= 2147483647 or valor != int(valor):
        unidade = "quilogramas com até 3 casas decimais" if fator == 1000 else "unidades inteiras"
        raise ValueError(f"Informe uma quantidade positiva em {unidade}.")
    return int(valor)


def kg(gramas):
    valor = f"{Decimal(gramas) / 1000:.3f}".rstrip("0").rstrip(".")
    return valor.replace(".", ",") + " kg"


def data_br(valor):
    return valor.strftime("%d/%m/%Y") if valor else "Sem rótulo"


def id_selecionado(entrada, opcoes):
    indice = entrada.current()
    if indice < 0:
        raise ValueError("Cadastre e selecione uma opção antes de continuar.")
    return opcoes[indice][0]


class Kayode:
    def __init__(self, janela):
        self.janela = janela
        janela.title("Projeto Kayode • Pontes e Lacerda")
        janela.geometry("1160x720")
        janela.minsize(990, 660)
        janela.configure(bg=FUNDO)
        tema()
        menu = tk.Frame(janela, bg=VERDE, width=218)
        menu.pack(side="left", fill="y")
        menu.pack_propagate(False)
        marca = tk.Canvas(menu, width=58, height=35, bg=VERDE, highlightthickness=0)
        marca.pack(anchor="w", padx=24, pady=(25, 0))
        # Símbolo da ponte que liga os doadores à cozinha.
        for x in (3, 27):
            marca.create_arc(x, 6, x+24, 43, start=0, extent=180, style="arc", outline=CLARO, width=3)
        marca.create_line(2, 26, 53, 26, fill=CLARO, width=3)
        tk.Label(menu, text="Kayode", bg=VERDE, fg="#f3f4ce",
                 font=("Times", 28, "bold")).pack(anchor="w", padx=22, pady=(0, 20))
        self.botoes = {}
        telas = [("Parceiros", self.parceiros), ("Doações", self.doacoes),
                 ("Recebimento", self.recebimento), ("Estoque", self.estoque),
                 ("Receitas", self.receitas), ("Produção", self.producao),
                 ("Distribuição", self.distribuicao)]
        for rotulo, tela in telas:
            item = tk.Button(menu, text=rotulo, anchor="w", relief="flat", borderwidth=0,
                             highlightthickness=0, padx=15, pady=7, cursor="hand2", font=(FONTE, 12),
                             command=lambda t=tela: self.abrir(t))
            item.pack(fill="x", padx=14, pady=1)
            self.botoes[tela] = item
        tk.Label(menu, text="Pontes e Lacerda · MT", bg=VERDE, fg="#d4e5cd",
                 font=(FONTE, 10)).pack(side="bottom", pady=22)
        self.aviso = tk.Label(janela, bg=FUNDO, fg=VERDE, anchor="w", font=(FONTE, 11, "bold"))
        self.aviso.pack(side="bottom", fill="x", padx=28, pady=10)
        self.pagina = tk.Frame(janela, bg=FUNDO)
        self.pagina.pack(fill="both", expand=True, padx=28, pady=(25, 0))
        janela.report_callback_exception = self.erro
        self.abrir(self.parceiros)

    def erro(self, tipo, erro, rastreio):
        if isinstance(erro, pymysql.IntegrityError):
            mensagem = "Registro repetido ou dados incompatíveis. Confira os campos."
        elif isinstance(erro, pymysql.MySQLError):
            mensagem = f"Erro MySQL {erro.args[0]}. Confira o serviço, o config.ini e o banco.sql."
        elif isinstance(erro, (ValueError, KeyError)):
            mensagem = str(erro)
        else:
            raise erro.with_traceback(rastreio)
        self.aviso.config(text=mensagem, fg="#973b29")

    def abrir(self, tela, mensagem=""):
        for filho in self.pagina.winfo_children():
            filho.destroy()
        self.aviso.config(text=mensagem, fg=VERDE)
        for funcao, item in self.botoes.items():
            ativo = funcao == tela
            item.config(bg=CLARO if ativo else VERDE, fg=TEXTO if ativo else "white",
                        activebackground=CLARO, activeforeground=TEXTO)
        try:
            tela()
            if mensagem:
                self.aviso.config(text=mensagem, fg=VERDE)
        except (ValueError, KeyError, pymysql.MySQLError) as erro:
            self.erro(type(erro), erro, erro.__traceback__)

    def parceiros(self):
        p = self.pagina
        titulo(p, "Parceiros", "Cadastre quem oferece alimentos e os locais que recebem marmitas.")
        f = linha(p)
        pessoa = campo(f, "Nome do parceiro")
        tipo = campo(f, "Participação", ["Doador", "Destino"])

        def salvar():
            banco.gravar("INSERT INTO parceiro (nome, tipo) VALUES (%s, %s)", (nome(pessoa), tipo.get()))
            self.abrir(self.parceiros, "Parceiro cadastrado.")

        botao(linha(p), "Cadastrar parceiro", salvar)
        dados = banco.consultar("SELECT nome, tipo FROM parceiro ORDER BY nome")
        tabela(p, ("Parceiro", "Participação"), dados)

    def doacoes(self):
        p = self.pagina
        titulo(p, "Doações", "Registre um alimento por lote e informe onde ele pode ser retirado.")
        doadores = banco.consultar("SELECT id, nome FROM parceiro WHERE tipo='Doador' ORDER BY nome")
        alimentos = banco.consultar("SELECT nome FROM alimento ORDER BY nome")
        f = linha(p)
        doador = campo(f, "Doador", [r[1] for r in doadores])
        alimento = campo(f, "Alimento · escolha ou digite", [r[0] for r in alimentos], editavel=True)
        peso = campo(f, "Peso oferecido (kg)", largura=10)
        f = linha(p)
        local = campo(f, "Local de retirada")
        validade = campo(f, "Validade do rótulo (dd/mm/aaaa)")
        texto(p, "Para alimentos in natura sem data no rótulo, deixe a validade em branco.", 10).pack(anchor="w")

        def salvar():
            dia = None
            if validade.get().strip():
                try:
                    dia = datetime.strptime(validade.get().strip(), "%d/%m/%Y").date()
                except ValueError:
                    raise ValueError("Informe a validade no formato dd/mm/aaaa.") from None
                if dia < date.today():
                    raise ValueError("A validade informada já passou.")
            banco.oferecer(id_selecionado(doador, doadores), nome(alimento), numero(peso, 1000),
                           dia, nome(local, 160))
            self.abrir(self.doacoes, "Oferta registrada. O lote aguarda conferência.")

        botao(linha(p), "Registrar oferta", salvar)
        dados = banco.consultar("""SELECT l.id, a.nome, p.nome, l.oferecido_g, l.situacao FROM lote l
                                   JOIN alimento a ON a.id=l.alimento_id JOIN parceiro p ON p.id=l.doador_id
                                   ORDER BY l.id DESC""")
        tabela(p, ("Lote", "Alimento", "Doador", "Oferecido", "Situação"),
               [(i, a, d, kg(g), s) for i, a, d, g, s in dados])

    def recebimento(self):
        p = self.pagina
        titulo(p, "Recebimento", "Selecione um lote pendente e confira o peso que pode ser aproveitado.")
        dados = banco.consultar("""SELECT l.id, a.nome, l.retirada, l.oferecido_g, l.validade
                                   FROM lote l JOIN alimento a ON a.id=l.alimento_id
                                   WHERE l.situacao='Pendente' ORDER BY l.id""")
        grade = tabela(p, ("Lote", "Alimento", "Retirada", "Oferecido", "Validade"),
                       [(i, a, local, kg(g), data_br(v)) for i, a, local, g, v in dados])
        peso = campo(linha(p), "Peso aprovado na conferência (kg)")

        def registrar(recusar=False):
            if not grade.selection():
                raise ValueError("Selecione um lote na tabela.")
            lote = grade.item(grade.selection()[0], "values")[0]
            banco.conferir(lote, 0 if recusar else numero(peso, 1000))
            self.abrir(self.recebimento, "Lote recusado." if recusar else "Recebimento confirmado.")

        f = linha(p)
        botao(f, "Confirmar recebimento", registrar)
        botao(f, "Recusar lote", lambda: registrar(True), secundario=True)

    def estoque(self):
        p = self.pagina
        titulo(p, "Estoque", "Consulte os lotes recebidos e a prioridade de uso por validade.")
        dados = banco.consultar("""SELECT l.id, a.nome, l.saldo_g, l.validade,
                                   DATEDIFF(l.validade, CURRENT_DATE) FROM lote l
                                   JOIN alimento a ON a.id=l.alimento_id WHERE l.saldo_g > 0
                                   ORDER BY l.validade IS NULL, l.validade, l.id""")
        linhas = []
        for lote, alimento, saldo, validade, dias in dados:
            alerta = "Disponível"
            if dias is not None and dias < 0:
                alerta = "Vencido · bloqueado"
            elif dias is not None and dias <= 7:
                alerta = "Usar primeiro"
            linhas.append((lote, alimento, kg(saldo), data_br(validade), alerta))
        tabela(p, ("Lote", "Alimento", "Saldo", "Validade", "Prioridade"), linhas)

    def receitas(self):
        p = self.pagina
        titulo(p, "Receitas", "Monte a lista de ingredientes crus e informe o peso de cada um por marmita.")
        receita = campo(linha(p), "Nome da nova receita")
        alimentos = banco.consultar("SELECT nome FROM alimento ORDER BY nome")
        f = linha(p)
        alimento = campo(f, "Alimento · escolha ou digite", [r[0] for r in alimentos], editavel=True)
        gramas = campo(f, "Gramas por marmita")
        acoes = linha(p)
        itens = []
        grade = tabela(p, ("Ingrediente da nova receita", "Gramas por marmita"), [], altura=3)

        def adicionar():
            item = nome(alimento)
            peso = numero(gramas)
            if any(item.casefold() == anterior.casefold() for anterior, _ in itens):
                raise ValueError("Este ingrediente já está na receita.")
            itens.append((item, peso))
            grade.insert("", "end", values=(item, peso))
            alimento.set("")
            gramas.delete(0, "end")
            self.aviso.config(text="Ingrediente adicionado à receita em edição.", fg=VERDE)

        def remover():
            if not grade.selection():
                raise ValueError("Selecione um ingrediente da receita em edição.")
            item = grade.selection()[0]
            itens.pop(grade.index(item))
            grade.delete(item)

        def salvar():
            banco.salvar_receita(nome(receita), itens)
            self.abrir(self.receitas, "Receita salva. Consulte seu rendimento em Produção.")

        botao(acoes, "Adicionar ingrediente", adicionar, secundario=True)
        botao(acoes, "Remover selecionado", remover, secundario=True)
        botao(linha(p), "Salvar receita", salvar)
        existentes = banco.consultar("SELECT nome FROM receita ORDER BY nome")
        tabela(p, ("Receitas cadastradas",), existentes, altura=3)

    def producao(self):
        p = self.pagina
        titulo(p, "Produção", "Escolha a receita e compare o estoque com a meta da cozinha.")
        receitas = banco.consultar("SELECT id, nome FROM receita ORDER BY nome")
        f = linha(p)
        receita = campo(f, "Receita", [r[1] for r in receitas])
        meta = campo(f, "Meta de marmitas")
        meta.insert(0, "80")
        acoes = linha(p)
        faixa = tk.Frame(p, bg=CLARO, padx=18, pady=10)
        faixa.pack(fill="x", pady=(4, 8))
        faixa.configure(bg=VERDE)
        desenho = tk.Canvas(faixa, width=125, height=55, bg=VERDE, highlightthickness=0)
        desenho.pack(side="right")
        desenho.create_oval(28, 4, 97, 15, outline=CLARO, width=2)
        desenho.create_arc(28, -17, 97, 45, start=180, extent=180, style="arc", outline=CLARO, width=2)
        desenho.create_line(52, 46, 74, 46, fill=CLARO, width=2)
        resultado = texto(faixa, "Cadastre uma receita para calcular.", 23, True)
        resultado.configure(fg="#fff8df")
        resultado.pack(anchor="w")
        detalhe = texto(faixa, "", 11)
        detalhe.configure(fg="#dfeddd")
        detalhe.pack(anchor="w", pady=(3, 0))
        grade = tabela(p, ("Ingrediente", "Por marmita", "Em estoque", "Falta para a meta"), [])

        def calcular(evento=None):
            codigo = id_selecionado(receita, receitas)
            alvo = numero(meta)
            capacidade, ingredientes = banco.planejar(codigo)
            resultado.config(text=f"{capacidade} marmitas possíveis")
            restante = max(0, alvo - capacidade)
            detalhe.configure(text=f"Faltam ingredientes para {restante} marmitas da meta." if restante
                              else f"Há estoque suficiente para a meta de {alvo} marmitas.")
            grade.delete(*grade.get_children())
            for indice, (alimento, porcao, saldo) in enumerate(ingredientes):
                falta = max(0, alvo * porcao - saldo)
                grade.tag_configure("faltante", background="#fff0d4", foreground="#623c14")
                cor = "faltante" if falta else ("alternada" if indice % 2 else "")
                grade.insert("", "end", values=(alimento, f"{porcao} g", kg(saldo), kg(falta)), tags=(cor,))
            self.aviso.config(text=f"Estimativa para a meta de {alvo} marmitas.", fg=VERDE)

        def confirmar():
            quantidade = numero(meta)
            banco.produzir(id_selecionado(receita, receitas), quantidade)
            self.abrir(self.producao, f"Produção registrada · {quantidade} marmitas.")

        botao(acoes, "Calcular rendimento", calcular, secundario=True)
        botao(acoes, "Produzir a quantidade da meta", confirmar)
        receita.bind("<<ComboboxSelected>>", calcular)
        if receitas:
            calcular()

    def distribuicao(self):
        p = self.pagina
        titulo(p, "Distribuição", "Registre o destino e a quantidade de marmitas entregues.")
        producoes = banco.consultar("""
            SELECT p.id, r.nome, p.quantidade - COALESCE(SUM(e.quantidade),0) AS disponivel
            FROM producao p JOIN receita r ON r.id=p.receita_id
            LEFT JOIN entrega e ON e.producao_id=p.id
            GROUP BY p.id, r.nome, p.quantidade HAVING disponivel > 0 ORDER BY p.id
        """)
        destinos = banco.consultar("SELECT id, nome FROM parceiro WHERE tipo='Destino' ORDER BY nome")
        f = linha(p)
        producao = campo(f, "Produção com saldo", [f"#{i} · {r} · {s} disponíveis" for i, r, s in producoes], largura=26)
        destino = campo(f, "Destino", [r[1] for r in destinos], largura=15)
        quantia = campo(f, "Marmitas", largura=8)

        def salvar():
            quantidade = numero(quantia)
            banco.entregar(id_selecionado(producao, producoes), id_selecionado(destino, destinos), quantidade)
            self.abrir(self.distribuicao, f"Entrega registrada · {quantidade} marmitas.")

        botao(linha(p), "Registrar entrega", salvar)
        dados = banco.consultar("""SELECT e.dia, r.nome, d.nome, e.quantidade FROM entrega e
                                   JOIN parceiro d ON d.id=e.destino_id JOIN producao p ON p.id=e.producao_id
                                   JOIN receita r ON r.id=p.receita_id ORDER BY e.id DESC""")
        tabela(p, ("Data", "Receita", "Destino", "Marmitas"),
               [(data_br(dia), r, d, q) for dia, r, d, q in dados])


if __name__ == "__main__":
    raiz = tk.Tk()
    Kayode(raiz)
    raiz.mainloop()
