# Trabalho Prático 1 - Introdução à Inteligência Artificial(DCC642/UFMG)

Implementação do algoritmo Minimax com poda alfa-beta e iterative deepening para partidas de Connect4/Lig4, para a disciplina de Introdução à Inteligência Artificial.

_Integrantes: Daniel Vitor Rabelo Rodrigues e Manuela Monteiro Fernandes de Oliveira_

## 1. Introdução

Neste projeto (TP1), você irá implementar um agente de IA para jogar Ligue-4 (Connect Four) utilizando algoritmos de busca adversarial. Você utilizará uma página web acessada por meio de um servidor web local (executado em seu computador). A partir dessa página, será possível jogar humano vs IA, observar partidas IA vs IA, e realizar testes controlando parâmetros como profundidade máxima e tempo máximo por jogada. O objetivo principal é praticar a implementação de Minimax, poda Alfa-Beta e Iterative Deepening com uma função heurística de avaliação. Além de codificar o agente, você deverá redigir um relatório descrevendo sua metodologia e analisando resultados experimentais.

## 2. Código-base
### 2.1. Executar servidor

Baixe o código-base do TP1, disponibilizado na tarefa do moodle, que inclui o cliente em JavaScript (p5.js) para visualizar e jogar Ligue-4, bem como o servidor em Python (Flask) e o arquivo search.py onde você implementará o agente. Para executar o servidor, instale as dependências e inicie o servidor com os seguintes comandos:

```
python -m venv tp1-env          # Criar ambiente virtual Python
source tp1-env/bin/activate     # Ativar ambiente virtual
pip install -r requirements.txt # instalar bibliotecas necessárias
python server.py                # Executar o servidor (porta padrão: 5001)
```

Assim que o servidor iniciar, abra no navegador: http://localhost:5001. Essa URL deve mostrar a interface do jogo Ligue-4 como na figura a seguir:

### 2.2. Interface do Jogo

A interface exibe o tabuleiro 6×7, indicadores de vez e vencedor, além dos controles:

- Selecionar jogadores: jogador 1 (P1) e jogador 2 (P2) podem ser tanto IA quanto humanos.
- Tempo por jogada: limite de tempo (em ms) que seu agente deve respeitar.
- Novo jogo: reinicia a partida.

Existem quatro comportamentos que podem ser selecionados na interface para simular uma partida. 

- Human: Espera input humano através da interface gráfica.
- AI Random: Seleciona ações aleatórias válidas.
- AI Dummy: Seleciona a primeira ação válida possível.
- AI Student: Sua solução.

### 2.3. Estados e Ponto de Entrada

Todo o seu trabalho será realizado no arquivo search.py. O servidor chamará a função:

```
choose_move(board, player, config) -> (coluna, info)
```

onde:
- board é uma matriz 6×7 com valores {0,1,2} (0 = vazio, 1 = Jogador 1, 2 = Jogador 2);
- player é o jogador da vez (1 ou 2);
- config contém o tempo máximo da jogada em seguntos max_time_ms e a profundidade máxima max_depth.

O código inicial do search.py escolhe uma jogada aleatória válida apenas para validação do ambiente. Você deverá substituir essa lógica por uma busca adversarial com heurística.
 
## 3. Tarefas
### 3.1. Baseline (Agente Aleatório)

Valide o funcionamento do ambiente executando partidas Humano vs IA (aleatória) e IA aleatória vs IA aleatória. Essa etapa serve apenas para confirmar a comunicação cliente-servidor e a atualização do estado do jogo.
 
### 3.2. Minimax com Profundidade Limitada e Heurística

Implemente o algoritmo Minimax com profundidade limitada. Para estados terminais, atribua valores extremos (vitória/derrota) e 0 para empate. Para estados não terminais (quando a profundidade limite é atingida), utilize uma função heurística que estime a “vantagem” do jogador da vez. Sugestões de componentes heurísticos:

- Valorização do centro do tabuleiro;
- Contagem de sequências (duplas, triplas abertas) e ameaças;
- Penalidades para oportunidades do oponente.

Experimente diferentes profundidades (por exemplo, 2, 3, 4, 5) e observe o impacto em tempo e qualidade de decisão.
 
### 3.3. Minimax com Poda Alfa-Beta

Acrescente a poda Alfa-Beta à sua implementação. A poda deve reduzir o número de nós avaliados sem alterar a decisão ótima do Minimax. Registre o número de nós expandidos para comparação com a versão sem poda.

### 3.4. Iterative Deepening com Limite de Tempo

Implemente Iterative Deepening: execute sucessivamente profundidades 1, 2, 3, … até atingir max_depth ou estourar max_time_ms. Mantenha sempre a melhor jogada conhecida. Recomenda-se combinar Iterative Deepening com poda Alfa-Beta e, se possível, ordenação de jogadas (por ex., tentar coluna central primeiro) para aumentar a profundidade atingida no mesmo tempo.
 
### 3.5. Competição

Depois de implementar a busca Iterative Deepening, pense em técnicas para melhorar (transposições, funções de avaliação melhores, ordenação dos movimentos, etc.), pois haverá uma competição entre as IAs dos alunos! Os 3 primeiros lugares receberão pontos extras! As regras da competição são as seguintes:

- Tempo por jogada: 3s (definido pelo professor). O servidor aplica limite rígido de
- Rodadas duplas: dois jogos por confronto (invertendo quem começa). Pontuação: vitória=1, empate=0.5, derrota=0.
- Desclassificação técnica: agentes que travarem ou violarem o tempo repetidamente podem receber jogada aleatória de fallback ou WO daquela jogada.

## 4. Relatório

Após concluir a implementação dos algoritmos de busca, você irá excutar expertimentos e reportar os resultados encontrados. Os experimentos são os seguintes:
 
Minimax vs Aleatório

    Profundidades: 2, 3, 4 e 5.
    Métricas: taxa de vitória, tempo médio por jogada, média de estados visitados.

Alfa-Beta vs Minimax (sem poda)

    Profundidades: 2, 3, 4 e 5
    Métricas: taxa de vitória, tempo médio por jogada e média de estados visitados.

Iterative Deepening vs Alfa-Beta

    Limites de tempo: 1s e 2s.
    Métricas: taxa de vitória, tempo médio por jogada, profundidade média atingida e média de estados visitados.

IA do Aluno vs Jogador Humano

    Jogue pelo menos 5 partidas contra a sua melhor IA
    Descreva percepções qualitativas (forças e fraquezas observadas)

O seu relatório deve conter no máximo 5 páginas no formato da Association for the Advancement of Artificial Intelligence (AAAI) (disponível também no Overleaf). O relatório deve conter:

- Introdução e Objetivo
- Metodologia: evolução do agente (Minimax → Alfa-Beta → Iterative Deepening), heurística e decisões de projeto.
- Experimentos e Resultados: tabelas e (opcional) gráficos com as métricas propostas.
- Discussão: análise crítica dos resultados, trade-offs e limitações.
- Conclusão: síntese do que funcionou melhor e ideias de melhorias.
