# Implementação de Estruturas de Índice

Implementação de **Árvore B+** e **Linear Hashing** para indexação de registros compostos por campos inteiros.

##  Requisitos

- Python 3.7 ou superior
- Bibliotecas padrão Python (csv, logging, argparse)

## Estrutura do Projeto

```
projeto/
├── main.py              # Main centralizada
├── btree.py             # Implementação B-Tree
├── linear_hash.py       # Implementação Linear Hashing
├── experiments.py       # Scripts de experimentos
├── README.md            # Este arquivo
├── data/                # Arquivos de dados (criar se necessário)
│   └── *.csv           # Arquivos gerados pelo SIOgen
└── logs/               # Logs gerados (criado automaticamente)
    ├── btree.log
    └── linear_hash.log
```

## Como Usar

### Instalação

Não é necessária instalação. Basta ter Python 3.7+ instalado.

```bash
# Verificar versão do Python
python --version
```

### Uso Básico

#### 1. Modo Interativo

**B-Tree:**
```bash
python main.py -t btree
```

**Linear Hash:**
```bash
python main.py -t linear
```

#### 2. Com Arquivo de Dados (formato SIOgen)

**B-Tree:**
```bash
python main.py -t btree -f data/dataset.csv -p 512 -D
```

**Linear Hash:**
```bash
python main.py -t linear -f data/dataset.csv -p 512 -b 4 -u 0.8 -D
```

### Parâmetros da Linha de Comando

#### Parâmetros Comuns

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `-t, --type` | Tipo de índice: `btree`, `b`, `linear`, `l` | **Obrigatório** |
| `-f, --file` | Arquivo CSV de entrada (formato SIOgen) | Nenhum (modo interativo) |
| `-p, --page-size` | Tamanho da página em bytes | 512 |
| `-D, --debug` | Ativa modo debug com logs detalhados | Desativado |
| `-s, --stats` | Exibe estatísticas após operações | Desativado |

#### Parâmetros Específicos - Linear Hash

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `-b, --buckets` | Número inicial de buckets | 4 |
| `-u, --utilization` | Limiar de fator de carga (0.0-1.0) | 0.8 |

#### Parâmetros Específicos - B-Tree

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `--range MIN MAX` | Busca por intervalo [MIN, MAX] | Nenhum |

### Formato do Arquivo de Entrada (SIOgen)

O arquivo deve seguir o formato gerado pelo [SIOgen](https://ribeiromarcos.github.io/siogen/):

```csv
operation,key,attr2,attr3,...
+,10,100,200
+,25,150,250
+,5,50,75
?,25
-,10
```

**Operações:**
- `+` : Inserção de registro
- `-` : Remoção de registro (pela chave)
- `?` : Busca por registro (pela chave)

**Campos:**
- Primeiro campo após operação: **chave única** (A1)
- Demais campos: atributos adicionais (A2, A3, ...)

## Gerando Dados de Teste com SIOgen

### Instalação do SIOgen

```bash
# Clone o repositório
git clone https://github.com/ribeiromarcos/siogen.git
cd siogen

# Compile (se necessário)
make
```

### Gerando Datasets

```bash
# Exemplo: 3 atributos, 1000 inserções, 200 remoções
./siogen -a 3 -i 1000 -d 200 -f data/dataset_1000.csv

# Exemplo: 5 atributos, 10000 inserções, 2000 remoções
./siogen -a 5 -i 10000 -d 2000 -f data/dataset_10000.csv

# Exemplo: 10 atributos, 100000 inserções, 10000 remoções
./siogen -a 10 -i 100000 -d 10000 -f data/dataset_100000.csv
```

## Executando Experimentos

### Script de Experimentos Automatizado

```bash
# Rodar experimentos com diferentes configurações
python experiments.py

# Rodar experimentos específicos
python experiments.py --structures btree linear --page-sizes 256 512 1024
```

### Experimentos Manuais

**Variando tamanho da página:**
```bash
python main.py -t btree -f data/dataset.csv -p 256 -s
python main.py -t btree -f data/dataset.csv -p 512 -s
python main.py -t btree -f data/dataset.csv -p 1024 -s
```

**Variando número de campos:**
```bash
# Gerar datasets com diferentes números de atributos
./siogen -a 3 -i 10000 -d 1000 -f data/attrs_3.csv
./siogen -a 5 -i 10000 -d 1000 -f data/attrs_5.csv
./siogen -a 10 -i 10000 -d 1000 -f data/attrs_10.csv

# Testar com cada dataset
python main.py -t btree -f data/attrs_3.csv -s
python main.py -t btree -f data/attrs_5.csv -s
python main.py -t btree -f data/attrs_10.csv -s
```

**Variando número de buckets (Linear Hash):**
```bash
python main.py -t linear -f data/dataset.csv -b 2 -s
python main.py -t linear -f data/dataset.csv -b 4 -s
python main.py -t linear -f data/dataset.csv -b 8 -s
python main.py -t linear -f data/dataset.csv -b 16 -s
```

## Operações

### B-Tree
- ✅ Inserção
- ✅ Remoção
- ✅ Busca por igualdade
- ✅ **Busca por intervalo**

### Linear Hashing
- ✅ Inserção
- ✅ Remoção
- ✅ Busca por igualdade
- 
### Busca por Intervalo (B-Tree)

```bash
# Buscar registros com chaves entre 10 e 50
python main.py -t btree -f data/dataset.csv --range 10 50
```

## Estatísticas Coletadas

### B-Tree
- Número de nós (internos e folhas)
- Altura da árvore
- Número de registros
- Fator de ocupação médio
- Tempo de carregamento

### Linear Hash
- Número de buckets
- Número de registros
- Nível atual (d)
- Próximo split (sp)
- Número de splits realizados
- Páginas de overflow
- Fator de carga médio
- Tempo de carregamento

## Exemplos de Uso Completo

### Exemplo 1: Teste Básico com B-Tree

```bash
# 1. Gerar dados
./siogen -a 3 -i 1000 -d 100 -f test.csv

# 2. Executar B-Tree
python main.py -t btree -f test.csv -p 512 -s -D

# 3. Busca por intervalo
python main.py -t btree -f test.csv --range 100 500
```

### Exemplo 2: Teste de Performance - Linear Hash

```bash
# 1. Gerar dataset grande
./siogen -a 5 -i 50000 -d 5000 -f big_test.csv

# 2. Testar diferentes configurações
python main.py -t linear -f big_test.csv -p 512 -b 4 -u 0.8 -s
python main.py -t linear -f big_test.csv -p 512 -b 8 -u 0.8 -s
python main.py -t linear -f big_test.csv -p 1024 -b 4 -u 0.8 -s
```

### Exemplo 3: Comparação B-Tree vs Linear Hash

```bash
# Mesmo dataset para ambas estruturas
./siogen -a 4 -i 10000 -d 1000 -f comparison.csv

# B-Tree
python main.py -t btree -f comparison.csv -p 512 -s

# Linear Hash
python main.py -t linear -f comparison.csv -p 512 -b 4 -s
```

## Debug e Logs

### Ativar Modo Debug

```bash
python main.py -t btree -f data.csv -D
```

### Arquivos de Log

Os logs são salvos automaticamente em:
- `btree.log` - Logs da B-Tree
- `linear_hash.log` - Logs do Linear Hash

### Analisar Logs

```bash
# Ver últimas linhas do log
tail -n 50 btree.log

# Filtrar erros
grep "ERROR" btree.log

# Filtrar operações específicas
grep "Inserting" linear_hash.log
```

## Solução de Problemas

### Erro: "Page size must be at least 256 bytes"
```bash
# Use tamanho mínimo de 256 bytes
python main.py -t btree -f data.csv -p 256
```

### Erro: "File not found"
```bash
# Verifique se o arquivo existe
ls -la data/dataset.csv

# Use caminho absoluto se necessário
python main.py -t btree -f /caminho/completo/data/dataset.csv
```

### Performance ruim
```bash
# Aumente o tamanho da página
python main.py -t btree -f data.csv -p 1024

# Para Linear Hash, aumente buckets iniciais
python main.py -t linear -f data.csv -b 16
```

## Referências

- SIOgen: https://ribeiromarcos.github.io/siogen/
- B+ Tree: Silberschatz, Korth, Sudarshan - "Database System Concepts"
- Linear Hashing: Litwin, W. (1980) - "Linear Hashing: A New Tool for File and Table Addressing"

## Autor

- César Nogueira Rodrigues
- Instituto Federal de Minas Gerais - IFMG
- Banco de Dados - II

---

**23** Novembro 2025  
