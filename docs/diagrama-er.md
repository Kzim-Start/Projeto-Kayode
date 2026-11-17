# Diagrama entidade-relacionamento

Cada lote identifica um alimento oferecido por um doador. Uma receita contém vários ingredientes. Ao preparar uma receita, a cozinha registra quanto retirou de cada lote. As entregas ligam a produção aos parceiros que recebem as marmitas.

```mermaid
erDiagram
    parceiro ||--o{ lote : oferece
    alimento ||--o{ lote : identifica
    receita ||--|{ ingrediente : contem
    alimento ||--o{ ingrediente : compoe
    receita ||--o{ producao : orienta
    producao ||--|{ consumo : utiliza
    lote ||--o{ consumo : fornece
    producao ||--o{ entrega : origina
    parceiro ||--o{ entrega : recebe

    parceiro {
        int id PK
        varchar nome
        enum tipo
    }
    alimento {
        int id PK
        varchar nome UK
    }
    lote {
        int id PK
        int doador_id FK
        int alimento_id FK
        varchar retirada
        date validade
        int oferecido_g
        int recebido_g
        int saldo_g
        enum situacao
    }
    receita {
        int id PK
        varchar nome UK
    }
    ingrediente {
        int receita_id PK,FK
        int alimento_id PK,FK
        int gramas
    }
    producao {
        int id PK
        int receita_id FK
        int quantidade
        date dia
    }
    consumo {
        int producao_id PK,FK
        int lote_id PK,FK
        int gramas
    }
    entrega {
        int id PK
        int producao_id FK
        int destino_id FK
        int quantidade
        date dia
    }
```

**PK** identifica a chave primária. **FK** identifica uma referência a outra tabela. **UK** indica um valor único. Em `parceiro`, a combinação de nome e tipo é única. Em `ingrediente` e `consumo`, a chave primária é formada pelos dois campos marcados. Em `lote`, a validade pode ficar vazia quando o alimento in natura não possui data no rótulo.

[Consultar o script MySQL](../banco.sql)
