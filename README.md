# Projeto Kayode

Sistema de doação de alimentos e planejamento de marmitas em Pontes e Lacerda (MT). Um pequeno produtor, mercado ou comerciante informa o que pode doar. A equipe da cozinha confere a quantidade recebida, calcula quantas marmitas consegue preparar e registra a entrega a uma entidade ou ponto de distribuição.

Em Pontes e Lacerda, o Centro de Tecnologia Alternativa já relatou o fornecimento de alimentos da agricultura familiar à APAE pelo Programa de Aquisição de Alimentos. Essa experiência ajuda a contextualizar a proposta acadêmica. Os nomes usados no tutorial são fictícios. [Relato do CTA](https://ctamt.org.br/toda-terca-feira-paa-apae)

![Tela de produção com estoque para 50 marmitas](docs/planejamento.png)

[Assistir à demonstração das sete telas](docs/demonstracao.mp4)

## Instalação

É um aplicativo de computador feito em Python com Tkinter. Use Python 3.10 ou superior e MySQL Server 8.0.16 ou superior. A interface e o servidor podem rodar no mesmo computador durante a apresentação.

1. Baixe o repositório, abra o terminal na pasta do projeto e instale o conector.

   ```sh
   python -m pip install -r requirements.txt
   ```

2. Inicie o MySQL Server. No MySQL Workbench, abra **banco.sql** na conexão local e execute o script inteiro. Ele cria o banco `kayode` e suas oito tabelas. A conta usada para esta etapa precisa ter permissão para criar o banco e as tabelas.
3. Faça uma cópia de **config.exemplo.ini** chamada **config.ini** na mesma pasta. Informe o usuário, a senha e a porta do seu MySQL. Para usar o aplicativo, a conta precisa consultar, inserir e atualizar registros do banco `kayode`. O arquivo com sua senha está no `.gitignore`.
4. Inicie o Kayode.

   ```sh
   python app.py
   ```

No Windows, se o comando disponível for `py`, use `py -m pip install -r requirements.txt` e `py app.py`. No Debian/Ubuntu, use um ambiente virtual Python e instale o pacote `python3-tk` se o Tkinter estiver ausente.

## Onde encontrar cada parte

| Arquivo | Conteúdo |
| --- | --- |
| [app.py](app.py) | Janela principal e sete telas. Cada tela corresponde a um método com nome em português. |
| [interface.py](interface.py) | Campos, botões e tabelas usados nas telas. |
| [banco.py](banco.py) | Conexão MySQL, conferência de lotes, cálculo de rendimento, produção e entrega. |
| [banco.sql](banco.sql) | Tabelas, chaves e restrições. |
| [Diagrama ER](docs/diagrama-er.md) | Entidades, campos e relacionamentos do banco. |
| [Tutorial e roteiro da defesa](docs/tutorial.md) | Exemplo completo com os valores para digitar e os resultados esperados. |

## Como o Kayode calcula

A receita indica o peso cru aproveitável de cada ingrediente por marmita. Para cada ingrediente, o programa divide o saldo em gramas pelo peso da porção e considera só as marmitas inteiras. A menor dessas quantidades define o rendimento da receita. O cálculo apenas consulta o estoque. Confirmar a produção dá baixa nos lotes e cria o saldo de marmitas para a distribuição.

O aviso de sete dias ajuda a cozinha a priorizar lotes próximos da validade. A equipe registra a conferência no recebimento. Lotes pendentes, recusados ou com validade vencida ficam fora do cálculo.
