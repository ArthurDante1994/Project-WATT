# WATT Consultoria - Desafio Técnico (Gateway IoT)

Este repositório contém a solução do processo seletivo da WATT Consultoria (Blocos 1, 2 e 3). O sistema atua como um Gateway de Borda (Edge Gateway), consumindo dados de energia via Google Pub/Sub, persistindo-os localmente e servindo-os para o chão de fábrica via protocolo Modbus TCP.

## 🛠️ Tecnologias e Decisões de Arquitetura

* **Ingestão:** `google-cloud-pubsub` (Consumo contínuo via streaming_pull).
* **Banco de Dados:** `SQLite3`. Escolhido pela reprodutibilidade imediata (não exige instalação de servidores de BD pelo avaliador) e suporte nativo a transações ACID e restrições relacionais.
* **Servidor Industrial:** `pyModbusTCP`. Escolhido por ser nativo em Python e permitir a execução não-bloqueante via *threads*.
* **Segurança:** Credenciais gerenciadas via `.env` (não comitadas).

## 🚀 Configuração Rápida (Execução do Zero)

### 1. Preparação do Ambiente
```bash
python -m venv venv
# Ative o ambiente (Windows)
.\venv\Scripts\activate
# Instale as dependências
pip install google-cloud-pubsub python-dotenv pyModbusTCP

2. Configuração de CredenciaisCrie um arquivo .env na raiz do projeto e aponte para o seu arquivo de credenciais do Google Cloud:PlaintextGOOGLE_APPLICATION_CREDENTIALS="C:\caminho\absoluto\para\sua\chave.json"

No terminal com o venv ativado, execute:

▶️ Como Executar o SistemaA arquitetura foi desenhada para rodar o ingestor, o banco de dados e o servidor Modbus TCP em um único processo principal

Passo 1: Iniciar o Gateway (Servidor)No terminal com o venv ativado, execute:Bashpython Project/ingestao_pubsub.py

O que acontece nos bastidores:O banco de dados watt_energia.db é inicializado automaticamente (Tabelas: ativos, leituras_historicas, estado_atual).O servidor Modbus TCP é iniciado no IP 127.0.0.1, porta 10502 (porta alta escolhida para evitar bloqueios de privilégio administrativo no Windows).A cada leitura recebida da nuvem, os dados são validados, os fatores de escala (RTC/RTP) são aplicados, salvos no banco SQLite (evitando duplicidade com chaves compostas) e os registradores Modbus são atualizados em tempo real.Passo 2: Validar a Comunicação Modbus (Cliente)Para atestar que os dados estão disponíveis para o supervisório (SCADA), abra um segundo terminal (mantenha o primeiro rodando), ative o venv e execute o script de teste de leitura:Bashpython Project/cliente_teste_modbus.py
Este script atuará como um CLP, conectando-se ao servidor local e lendo a Tensão (Va) diretamente da memória Modbus.📊 Mapa de Memória Modbus TCPTodos os dados elétricos foram convertidos para o padrão Float32 (IEEE 754), ocupando 2 registradores (Words) cada. Os fatores de escala (RTC e RTP) já são aplicados via software antes da disponibilização na memória, conforme a regra de negócio da documentação elétrica.GrandezaDescriçãoEndereço (Holding Register)Tipo de DadoRTCFator de Corrente0 e 1Float32RTPFator de Tensão2 e 3Float32VaTensão Fase A10 e 11Float32VbTensão Fase B12 e 13Float32VcTensão Fase C14 e 15Float32IaCorrente Fase A20 e 21Float32PdirPotência Ativa Direta36 e 37Float32fFrequência50 e 51Float32

Passo 2: instalar o sqliteodbc.exe

No site baixar o sqliteodbc.exe
http://www.ch-werner.de/sqliteodbc/

Você precisará baixar e instalar um pequeno componente gratuito chamado SQLite ODBC Driver no seu computador. (Geralmente é um arquivo chamado sqliteodbc.exe, mantido por Christian Werner no site oficial do projeto).

Atenção: Como o Elipse Studio geralmente roda em 32-bits, você precisará instalar a versão 32-bits do driver, mesmo que o seu Windows seja 64-bits.

O próximo passo é criar uma "ponte nomeada" (chamada de DSN) dentro do Windows. É essa ponte que o Elipse vai usar para achar o seu arquivo do Python.

Como o Elipse E3 Studio é um software de 32 bits, nós precisamos obrigatoriamente usar o configurador de 32 bits do Windows (mesmo que o seu computador seja de 64 bits).

Aqui está o passo a passo exato para criar essa ponte:

1
Abra o Administrador ODBC (32 bits)
A busca do Windows
Clique no menu Iniciar do seu computador e digite ODBC.
O Windows vai te mostrar duas opções. Clique obrigatoriamente em "Fontes de Dados ODBC (32 bits)" ou "ODBC Data Sources (32-bit)".

2
Adicione a Nova Ponte
Aba DSN de Sistema
Na janela que abrir, vá para a aba DSN de Sistema (System DSN) na parte superior e clique no botão Adicionar.

3
Selecione o Driver do SQLite
O que você acabou de instalar
Uma lista com vários nomes vai aparecer. Role até o final e procure por SQLite3 ODBC Driver. Selecione ele e clique em Concluir.

4
Aponte para o Banco do Python
A configuração final
Uma pequena janela de configuração vai se abrir. Preencha apenas dois campos:

Data Source Name: Digite WATT_DB (este será o nome oficial da nossa ponte).

Database Name: Clique no botão Browse (Procurar) e navegue pelas suas pastas até encontrar o arquivo .db (ou .sqlite) que o seu script Python está alimentando. Selecione ele.

Deixe o resto em branco e clique em OK para salvar e fechar tudo.


O que acabou de acontecer: Você acabou de dizer para o Windows: "Toda vez que um programa pedir para falar com o WATT_DB, traduza a conversa e mande para aquele arquivo específico do Python."


## 🚀 Configuração NOVAS (Execução do Zero)

## 📘 Documentação de Arquitetura

**Estado atual:** Parcial (complementado nesta seção).

### 1. Visão Geral da Solução
O projeto implementa um **Gateway IoT de Borda** para integrar medições elétricas vindas da nuvem com sistemas industriais locais.

Fluxo macro:
1. Mensagens de telemetria chegam via Google Pub/Sub.
2. O processo de ingestão valida e normaliza os dados recebidos.
3. Os dados são persistidos no banco local SQLite.
4. O estado mais recente é publicado na memória Modbus TCP.
5. Clientes industriais (CLP/SCADA) leem os registradores Modbus em tempo real.

### 2. Decisões de Projeto

**Por que SQLite (e não PostgreSQL)?**
- Reprodutibilidade imediata para avaliação: não exige instalação/configuração de servidor externo.
- Banco embarcado com suporte a transações ACID, suficiente para o volume esperado neste desafio.
- Facilidade de distribuição e execução local em ambiente Windows/Linux.

**Quando PostgreSQL seria melhor?**
- Escalabilidade horizontal/vertical maior.
- Melhor concorrência para múltiplos escritores e cenários de alta taxa de ingestão.
- Recursos avançados de observabilidade, replicação e administração.

**Por que pyModbusTCP?**
- Biblioteca simples e estável para disponibilizar dados em protocolo industrial padrão.
- Integração direta com Python e atualização de registradores em tempo real.

**Por que Google Pub/Sub na ingestão?**
- Consumo assíncrono e contínuo via `streaming_pull`.
- Desacoplamento entre produtor de dados e gateway de borda.

### 3. Estrutura do Fluxo de Dados

1. **Ingestão** ([ingestao_pubsub.py](ingestao_pubsub.py))
- Lê credenciais via `.env`.
- Assina tópico/subscrição no Pub/Sub.
- Processa payload JSON de telemetria.

2. **Persistência** ([database.py](database.py))
- Inicializa estrutura local do banco `watt_energia.db`.
- Salva histórico e atualiza estado mais recente.
- Mantém consistência com regras de chave/duplicidade do domínio.

3. **Camada Industrial** ([servidor_modbus.py](servidor_modbus.py))
- Inicializa servidor Modbus TCP local.
- Converte valores para Float32 (IEEE 754) em 2 holding registers por grandeza.
- Atualiza mapa de memória para leitura por cliente externo.

4. **Validação de Integração** ([cliente_teste_modbus.py](cliente_teste_modbus.py))
- Atua como cliente de teste para confirmar leitura correta dos registradores.

### 4. Dependências Externas

Dependências efetivamente utilizadas no código:
- `google-cloud-pubsub`: consumo das mensagens de telemetria.
- `python-dotenv`: carregamento de variáveis de ambiente e credenciais.
- `pyModbusTCP`: servidor e cliente Modbus TCP.

Dependências nativas (stdlib Python) relevantes:
- `sqlite3`, `json`, `logging`, `os`, `datetime`, `time`, `copy`, `random`, `tkinter`.

Observação sobre alternativas citadas:
- `SQLAlchemy` e `paho-mqtt` **não são utilizados atualmente** neste repositório.
- Caso o projeto evolua para MQTT, `paho-mqtt` é uma opção natural para substituir/complementar o Pub/Sub.
- Caso o projeto evolua para múltiplos bancos e ORM, `SQLAlchemy` pode facilitar portabilidade e modelagem.

### 5. Segurança e Configuração

- Credenciais do Google Cloud ficam fora do código-fonte e são referenciadas via `.env`.
- O arquivo `.env` não deve ser versionado.
- Em ambiente produtivo, recomenda-se secret manager e rotação de chaves.

### 6. Limitações Conhecidas

- Arquitetura focada em execução local e simplicidade de setup.
- Sem camada de filas local para retry/reprocessamento avançado.
- Sem autenticação/criptografia no Modbus (característica do protocolo base), devendo ser mitigado por segmentação de rede/ACLs em produção.

### 7. Mapeamento com Outros Itens do Desafio

Este capítulo de arquitetura também ajuda a atender outros entregáveis do desafio.

- **Documentação do Protocolo Industrial (item 6):** o capítulo com o mapa de memória Modbus já serve como base direta. A tabela de registradores (por exemplo, `Va` em HR 10 e 11) pode ser mantida nesta documentação e referenciada no entregável específico.
- **Schema do Banco (item específico):** a decisão de usar SQLite já está documentada aqui. Para completar o entregável de schema, basta detalhar as tabelas do `watt_energia.db` (campos, tipos de dados, chaves e restrições).

Observação importante:
- A tabela de registradores Modbus já cobre exatamente o que é esperado para a documentação de protocolo industrial.
- Esta documentação de arquitetura já adianta parte relevante do entregável de banco de dados.

### 8. Conclusão

O documento já está em nível profissional e cobre as principais decisões e fluxos técnicos.

Para ficar completo para o item 3, recomenda-se adicionar um diagrama visual da arquitetura contendo:
- origem dos dados (Pub/Sub),
- camada de ingestão,
- persistência SQLite,
- exposição via servidor Modbus TCP,
- cliente industrial (CLP/SCADA) consumidor dos registradores.

### 9. Schema do Banco (ER + Descrição)

Banco local utilizado: `watt_energia.db`.

#### 9.1 Diagrama ER (simplificado)

```mermaid
erDiagram
	ATIVOS ||--o{ LEITURAS_HISTORICAS : possui
	ATIVOS ||--|| ESTADO_ATUAL : mantem

	ATIVOS {
		INTEGER id PK
		TEXT device_id UNIQUE
		TIMESTAMP criado_em
	}

	LEITURAS_HISTORICAS {
		INTEGER id PK
		INTEGER ativo_id FK
		TIMESTAMP timestamp
		REAL rtc
		REAL rtp
		TEXT payload_completo
	}

	ESTADO_ATUAL {
		INTEGER ativo_id PK, FK
		TIMESTAMP timestamp_ultima_leitura
		TEXT payload_completo
	}
```

#### 9.2 Tabela `ativos`
Propósito: cadastrar cada equipamento/dispositivo monitorado uma única vez.

- `id` (INTEGER, PK, AUTOINCREMENT): identificador interno do ativo.
- `device_id` (TEXT, UNIQUE, NOT NULL): identificador lógico vindo da telemetria.
- `criado_em` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP): momento de criação do cadastro.

#### 9.3 Tabela `leituras_historicas`
Propósito: armazenar o histórico de leituras para auditoria, rastreabilidade e análises futuras.

- `id` (INTEGER, PK, AUTOINCREMENT): identificador interno da leitura.
- `ativo_id` (INTEGER, FK -> ativos.id): referência ao ativo de origem.
- `timestamp` (TIMESTAMP, NOT NULL): instante da leitura recebida.
- `rtc` (REAL): fator de corrente aplicado na normalização.
- `rtp` (REAL): fator de tensão aplicado na normalização.
- `payload_completo` (TEXT, NOT NULL): payload JSON completo da mensagem.

Regras importantes:
- `UNIQUE(ativo_id, timestamp)`: evita gravação duplicada da mesma leitura no mesmo instante.

#### 9.4 Tabela `estado_atual`
Propósito: manter apenas a leitura mais recente de cada ativo para consulta rápida e atualização do Modbus.

- `ativo_id` (INTEGER, PK e FK -> ativos.id): garante 1 linha por ativo.
- `timestamp_ultima_leitura` (TIMESTAMP, NOT NULL): timestamp da última leitura válida.
- `payload_completo` (TEXT, NOT NULL): payload JSON da leitura mais recente.

Regras importantes:
- Upsert por `ativo_id` atualiza a linha existente quando chega uma nova leitura.

#### 9.5 Observação sobre campos de negócio (ex.: consumo_kwh, tensao)
Campos elétricos como `consumo_kwh`, `tensao`, `corrente`, `potencia` e outros podem vir no JSON e são preservados dentro de `payload_completo`.

Isso mantém flexibilidade para variações do payload sem migração frequente de schema e permite evolução futura para colunas dedicadas, caso necessário para performance analítica.

### 10. Documentação do Protocolo Industrial (Modbus TCP)

Esta seção atende ao requisito de mapeamento de variáveis para protocolo industrial.

Referência de implementação:
- servidor: [servidor_modbus.py](servidor_modbus.py)
- cliente de teste: [cliente_teste_modbus.py](cliente_teste_modbus.py)

#### 10.1 Parâmetros de comunicação

- Protocolo: Modbus TCP
- Host padrão: `127.0.0.1`
- Porta padrão: `10502`
- Área de dados utilizada: Holding Registers (4x)
- Operação principal de cliente: leitura com função `0x03` (Read Holding Registers)

#### 10.2 Convenção de codificação dos valores

Na implementação atual, cada variável ocupa **2 Holding Registers** (32 bits), com o seguinte processo:

1. valor de engenharia (após fatores de escala) -> multiplicação por `100`;
2. conversão para inteiro de 32 bits;
3. armazenamento em duas words de 16 bits (High Word, Low Word).

Valor de engenharia para leitura no cliente:

`valor_real = valor_int32 / 100.0`

#### 10.3 Regras de escala antes da publicação Modbus

- Tensões (`Va`, `Vb`, `Vc`) -> multiplicadas por `RTP`
- Correntes (`Ia`, `Ib`, `Ic`, `In`) -> multiplicadas por `RTC`
- Potências/energias (`P*`, `E*`, além de `Q`, `S`, `Ph`) -> multiplicadas por `RTC * RTP`
- Demais variáveis -> sem escala adicional

#### 10.4 Mapa de registradores (Holding Registers)

| Variável | Descrição | Endereço inicial (HR) | Endereço final (HR) | Tamanho |
|---|---|---:|---:|---|
| RTC | Fator de corrente | 0 | 1 | 2 regs (32 bits) |
| RTP | Fator de tensão | 2 | 3 | 2 regs (32 bits) |
| Va | Tensão fase A | 10 | 11 | 2 regs (32 bits) |
| Vb | Tensão fase B | 12 | 13 | 2 regs (32 bits) |
| Vc | Tensão fase C | 14 | 15 | 2 regs (32 bits) |
| Ia | Corrente fase A | 20 | 21 | 2 regs (32 bits) |
| Ib | Corrente fase B | 22 | 23 | 2 regs (32 bits) |
| Ic | Corrente fase C | 24 | 25 | 2 regs (32 bits) |
| In | Corrente de neutro | 26 | 27 | 2 regs (32 bits) |
| Pa | Potência ativa fase A | 30 | 31 | 2 regs (32 bits) |
| Pb | Potência ativa fase B | 32 | 33 | 2 regs (32 bits) |
| Pc | Potência ativa fase C | 34 | 35 | 2 regs (32 bits) |
| Pdir | Potência ativa direta | 36 | 37 | 2 regs (32 bits) |
| fpa | Fator de potência fase A | 40 | 41 | 2 regs (32 bits) |
| fpb | Fator de potência fase B | 42 | 43 | 2 regs (32 bits) |
| fpc | Fator de potência fase C | 44 | 45 | 2 regs (32 bits) |
| fpt | Fator de potência total | 46 | 47 | 2 regs (32 bits) |
| f | Frequência | 50 | 51 | 2 regs (32 bits) |
| t | Temperatura | 52 | 53 | 2 regs (32 bits) |
| Ea | Energia fase A | 60 | 61 | 2 regs (32 bits) |
| Eb | Energia fase B | 62 | 63 | 2 regs (32 bits) |
| Ec | Energia fase C | 64 | 65 | 2 regs (32 bits) |

#### 10.5 Exemplo de leitura no cliente

Para ler `Va`:
- endereço inicial: `10`
- quantidade: `2` registradores
- recomposição: unir High/Low word em `int32`
- conversão final: dividir por `100`

#### 10.6 Escopo atual e observações

- O gateway **disponibiliza** os valores em Modbus TCP para consumo de CLP/SCADA.
- Não há, neste escopo, escrita de setpoints pelo cliente industrial.
- Este mapeamento pode ser referenciado diretamente no entregável "Documentação do Protocolo Industrial".