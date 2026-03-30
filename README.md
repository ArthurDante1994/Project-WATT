# Project-WATT
Projeto de Automação Industrial end-to-end com ingestão de dados via Google Pub/Sub, persistência em banco de dados, integração via Modbus TCP/Ethernet-IP e supervisão no Elipse E3. Inclui simulador, análise energética e documentação completa da arquitetura.

⚡ Projeto de Automação Industrial e Supervisão

Este repositório apresenta o desenvolvimento de uma solução completa de engenharia voltada para Automação Industrial e Supervisão, proposta como desafio pela Watt Consultoria.

O objetivo principal deste projeto é implementar uma arquitetura end-to-end, contemplando desde a aquisição de dados em tempo real até a visualização supervisória, passando por camadas de processamento, armazenamento e integração industrial.

A proposta simula um cenário real de aplicação em campo, exigindo a integração de múltiplas tecnologias amplamente utilizadas na indústria, com foco em confiabilidade, organização e escalabilidade.

🎯 Objetivos
Desenvolver um pipeline completo de dados industriais
Integrar sistemas de comunicação e protocolos industriais
Garantir persistência estruturada dos dados
Implementar supervisão operacional funcional
Produzir análises técnicas com foco energético
Documentar toda a arquitetura de forma reproduzível

🧩 Escopo da Solução

A solução contempla os seguintes componentes:

📡 Ingestão de Dados
Serviço de coleta de dados em tempo real utilizando Google Pub/Sub
💾 Persistência de Dados
Armazenamento em banco de dados (relacional ou séries temporais)
🔌 Integração Industrial
Implementação de servidor utilizando protocolos industriais como:
Modbus TCP
Ethernet/IP
🖥️ Supervisório
Desenvolvimento de interface no Elipse E3, com tela operacional funcional
📊 Análise Técnica
Elaboração de relatório com interpretações energéticas dos dados coletados
🔄 Simulação de Dados
Criação de um simulador de mensagens compatível com o payload especificado
📚 Documentação
README detalhado com instruções de execução e descrição da arquitetura do sistema

🏗️ Arquitetura

O projeto segue uma arquitetura modular, onde cada componente depende do anterior, formando um fluxo contínuo:

Simulador → Pub/Sub → Processamento → Banco de Dados → Servidor Industrial → Supervisório

⚠️ Observações
O projeto foi estruturado de forma organizada e modular, visando facilitar manutenção e escalabilidade.
Recomenda-se a leitura completa do enunciado antes da execução, pois os componentes são interdependentes.
A proposta enfatiza não apenas a implementação, mas também a capacidade de integração ponta a ponta, essencial em projetos reais de engenharia.

🚀 Conclusão

Este projeto demonstra a capacidade de desenvolver soluções completas em automação industrial, integrando tecnologias modernas de dados com protocolos industriais clássicos, resultando em uma aplicação robusta e alinhada às demandas do mercado.
