# WATT Consultoria - Desafio Técnico (Bloco 1: Ingestão de Dados)

Este repositório contém a solução inicial para o processo seletivo da WATT Consultoria. O serviço implementado neste bloco consome continuamente mensagens de energia elétrica via Google Pub/Sub, realiza a validação da estrutura, normaliza os fatores de escala e exibe os dados em tempo real.

## 🛠️ Pré-requisitos

Antes de iniciar, certifique-se de ter em sua máquina:
* [Python 3.8+](https://www.python.org/downloads/) instalado e adicionado ao PATH.
* O arquivo de credenciais do Google Cloud (`.json`) com permissões para acessar a assinatura do projeto.

## 🚀 Configuração do Ambiente

Siga os passos estritamente na ordem abaixo para configurar e executar o projeto do zero de forma isolada e segura.

### 1. Criação do Ambiente Virtual
Abra o terminal na pasta raiz do projeto e crie um ambiente virtual para isolar as dependências:
```bash
# No Windows
python -m venv venv
2. Ativação do Ambiente Virtual
Ative o ambiente criado. Seu terminal deverá mostrar um (venv) no início da linha:

Bash
# No Windows (PowerShell)
.\venv\Scripts\activate
3. Instalação das Dependências
Com o ambiente ativado, instale as bibliotecas exigidas pelo script:

Bash
pip install google-cloud-pubsub python-dotenv
🔐 Configuração de Segurança e Credenciais
Cumprindo os requisitos de segurança da arquitetura, nenhuma credencial foi inserida diretamente no código-fonte. A autenticação é feita via variáveis de ambiente.

Salve o seu arquivo de chaves do Google Cloud na raiz do projeto com o nome credenciais.json.

Na raiz do projeto, crie um arquivo vazio chamado exatamente .env.

Adicione a seguinte linha dentro do arquivo .env, substituindo o caminho de exemplo pelo caminho absoluto do seu computador até o arquivo JSON:

Plaintext
GOOGLE_APPLICATION_CREDENTIALS="C:\caminho\absoluto\para\o\seu\credenciais.json"
Nota de Segurança: Os arquivos venv/, .env e credenciais.json estão mapeados no .gitignore e não devem ser comitados no repositório público.

▶️ Execução do Serviço de Ingestão
Com o ambiente ativado e as credenciais configuradas, inicie o serviço executando:

Bash
python Project/ingestao_pubsub.py
📊 Resultado Esperado e Comportamento
Ao executar o comando acima, o sistema iniciará a conexão de forma contínua e não-bloqueante. O comportamento esperado no terminal é:

Confirmação de Conexão: Um log inicial informando que o serviço está escutando o tópico configurado.

Processamento: A cada nova mensagem publicada pelos medidores simulados, o sistema extrairá e validará o identificador do dispositivo (tratando os aliases permitidos) e normalizará os fatores de escala RTC e RTP (assumindo 1.0 em caso de dados inválidos ou ausentes).

Exibição: Um log de sucesso será emitido junto com a impressão do payload elétrico completo em formato JSON para inspeção em tempo real.

Para interromper o serviço graciosamente, pressione Ctrl + C no terminal.