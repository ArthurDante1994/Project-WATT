# WATT Consultoria - Desafio Técnico (Gateway IoT)

Este repositório contém a solução do processo seletivo da WATT Consultoria (Blocos 1, 2 e 3). O sistema atua como um Gateway de Borda (Edge Gateway), consumindo dados de energia via Google Pub/Sub, persistindo-os localmente e servindo-os para o chão de fábrica via protocolo Modbus TCP.

## 🛠️ Tecnologias e Decisões de Arquitetura

* **Ingestão:** `google-cloud-pubsub` (Consumo contínuo via streaming_pull).
* **Banco de Dados:** `SQLite3`. Escolhido pela reprodutibilidade imediata (não exige instalação de servidores de BD pelo avaliador) e suporte nativo a transações ACID e restrições relacionais.
* **Servidor Industrial:** `pyModbusTCP`. Escolhido por ser nativo em Python e permitir a execução não-bloqueante via *threads*.
* **Segurança:** Credenciais gerenciadas via `.env` (não comitadas).

## 🚀 Configuração Rápida (Execução do Zero)

### 1. Preparação do Ambiente
Abra o terminal na raiz do projeto e execute:
```bash
python -m venv venv
# Ative o ambiente (Windows)
.\venv\Scripts\activate
# Instale as dependências
pip install google-cloud-pubsub python-dotenv pyModbusTCP

2. Configuração de CredenciaisCrie um arquivo .env na raiz do projeto e aponte para o seu arquivo de credenciais do Google Cloud:PlaintextGOOGLE_APPLICATION_CREDENTIALS="C:\caminho\absoluto\para\sua\chave.json"
▶️ Como Executar o SistemaA arquitetura foi desenhada para rodar o ingestor, o banco de dados e o servidor Modbus TCP em um único processo principal.Passo 1: Iniciar o Gateway (Servidor)No terminal com o venv ativado, execute:Bashpython Project/ingestao_pubsub.py
O que acontece nos bastidores:O banco de dados watt_energia.db é inicializado automaticamente (Tabelas: ativos, leituras_historicas, estado_atual).O servidor Modbus TCP é iniciado no IP 127.0.0.1, porta 10502 (porta alta escolhida para evitar bloqueios de privilégio administrativo no Windows).A cada leitura recebida da nuvem, os dados são validados, os fatores de escala (RTC/RTP) são aplicados, salvos no banco SQLite (evitando duplicidade com chaves compostas) e os registradores Modbus são atualizados em tempo real.Passo 2: Validar a Comunicação Modbus (Cliente)Para atestar que os dados estão disponíveis para o supervisório (SCADA), abra um segundo terminal (mantenha o primeiro rodando), ative o venv e execute o script de teste de leitura:Bashpython Project/cliente_teste_modbus.py
Este script atuará como um CLP, conectando-se ao servidor local e lendo a Tensão (Va) diretamente da memória Modbus.📊 Mapa de Memória Modbus TCPTodos os dados elétricos foram convertidos para o padrão Float32 (IEEE 754), ocupando 2 registradores (Words) cada. Os fatores de escala (RTC e RTP) já são aplicados via software antes da disponibilização na memória, conforme a regra de negócio da documentação elétrica.GrandezaDescriçãoEndereço (Holding Register)Tipo de DadoRTCFator de Corrente0 e 1Float32RTPFator de Tensão2 e 3Float32VaTensão Fase A10 e 11Float32VbTensão Fase B12 e 13Float32VcTensão Fase C14 e 15Float32IaCorrente Fase A20 e 21Float32PdirPotência Ativa Direta36 e 37Float32fFrequência50 e 51Float32