# Projeto Kayode

Aplicativo em **Python (Tkinter + MySQL)** para registrar doações de alimentos, controlar estoque e calcular a produção de marmitas.

## Vídeo de demonstração

[Assistir à demonstração das sete telas](demonstracao.mp4)

## Instalação

**Requisitos:** Python 3.10+ e MySQL Server 8.0.16+ instalado e em execução.

1. Baixe o ZIP do repositório e extraia a pasta.
2. Abra o **MySQL Workbench**, conecte ao servidor e execute o arquivo `banco.sql`.
3. Copie `config.exemplo.ini`, renomeie a cópia para `config.ini` e preencha o usuário e a senha do seu MySQL.
4. Abra o terminal na pasta do projeto e execute:

```bash
python -m pip install -r requirements.txt
python app.py
```

No Windows, se o comando `python` não funcionar, use `py`.

## Funcionalidades

- **Parceiros:** doadores e locais de entrega
- **Doações:** cadastro de alimentos e lotes
- **Recebimento:** conferência e aprovação
- **Estoque:** saldos e validade
- **Receitas:** ingredientes e porções
- **Produção:** cálculo e preparo de marmitas
- **Distribuição:** registro de entregas

## Arquivos

- `app.py` — telas e navegação.
- `interface.py` — aparência e componentes.
- `banco.py` — consultas e regras do banco.
- `banco.sql` — estrutura das tabelas.
- `config.exemplo.ini` — modelo da conexão (crie `config.ini`).
- `requirements.txt` — dependência Python.
- [`DOCUMENTACAO.md`](DOCUMENTACAO.md) — diagrama ER e tutorial de uso.

Projeto acadêmico. O sistema precisa de conexão com o MySQL local para funcionar.
