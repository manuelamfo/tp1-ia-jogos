from curses import window
import enum
from hmac import new
from typing import List, Tuple, Optional, Dict
import time
import math
import random

ROWS, COLS = 6, 7
EMPTY, P1, P2 = 0, 1, 2

# -----------------------------------------------------------------------------
# Utilidades de tabuleiro (PRONTAS)
# -----------------------------------------------------------------------------
def copy_board(board: List[List[int]]) -> List[List[int]]:
    return [row[:] for row in board]

def valid_moves(board: List[List[int]]) -> List[int]:
    """Retorna as colunas ainda jogáveis (topo vazio)."""
    return [c for c in range(COLS) if board[0][c] == EMPTY]

def make_move(board: List[List[int]], col: int, player: int) -> Optional[List[List[int]]]:
    """Retorna um novo tabuleiro aplicando a gravidade na coluna col; None se inválido."""
    if col < 0 or col >= COLS or board[0][col] != EMPTY:
        return None
    nb = copy_board(board)
    for r in reversed(range(ROWS)):
        if nb[r][col] == EMPTY:
            nb[r][col] = player
            return nb
    return None

def winner(board: List[List[int]]) -> int:
    """0 se ninguém venceu; 1 ou 2 se há 4 em linha."""
    # Horizontais
    for r in range(ROWS):
        for c in range(COLS - 3):
            x = board[r][c]
            if x != EMPTY and x == board[r][c+1] == board[r][c+2] == board[r][c+3]:
                return x
    # Verticais
    for c in range(COLS):
        for r in range(ROWS - 3):
            x = board[r][c]
            if x != EMPTY and x == board[r+1][c] == board[r+2][c] == board[r+3][c]:
                return x
    # Diag ↘
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            x = board[r][c]
            if x != EMPTY and x == board[r+1][c+1] == board[r+2][c+2] == board[r+3][c+3]:
                return x
    # Diag ↗
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            x = board[r][c]
            if x != EMPTY and x == board[r-1][c+1] == board[r-2][c+2] == board[r-3][c+3]:
                return x
    return 0

def is_full(board: List[List[int]]) -> bool:
    return all(board[0][c] != EMPTY for c in range(COLS))

def terminal(board: List[List[int]]) -> Tuple[bool, int]:
    """(é_terminal, vencedor) com vencedor=0 para empate/indefinido."""
    w = winner(board)
    if w != 0:
        return True, w
    if is_full(board):
        return True, 0
    return False, 0

def other(player: int) -> int:
    return P1 if player == P2 else P2

# -----------------------------------------------------------------------------
# ÚNICO PONTO A SER IMPLEMENTADO PELOS ALUNOS
# -----------------------------------------------------------------------------
class Agent(enum.Enum): #? possível sugestão: retirar a classe Agent e usar P1 e P2 no lugar (variáveis globais já existentes)
    MAX = 1 # Jogador que tenta maximizar a heurística
    MIN = 2 # Jogador que tenta minimizar a heurística

def score_window(window: List[int], turn:int) -> int:
    player = turn
    opponent = other(turn)

    player_count = window.count(player)
    opponent_count = window.count(opponent)
    empty_count = window.count(EMPTY)

    score_window = 0
    if player_count == 4: 
        score_window += 1000
    if player_count == 3 and empty_count == 1: 
        score_window += 50
    if player_count == 2 and empty_count == 2: 
        score_window += 10

    if opponent_count == 3 and empty_count == 1: 
        score_window -= 80 # penalidade para oportunidades do oponente
    if opponent_count == 2 and empty_count == 2: 
        score_window -= 5

    return score_window

def evaluate(board: List[List[int]], turn: int):
    total_score = 0

    eval_board = [[3, 4, 5, 7, 5, 4, 3],
                 [4, 6, 8, 10, 8, 6, 4],
                 [5, 7, 11, 13, 11, 7, 5],
                 [5, 7, 11, 13, 11, 7, 5],
                 [4, 6, 8, 10, 8, 6, 4],
                 [3, 4, 5, 7, 5, 4, 3]]

    # faz uma avaliação inicial baseada em todas as peças já presente no tabuleiro
    for r in range(ROWS):
        for c in range(COLS):
            # se há uma peça na posição [r][c] e o turno é de max/min, aplica  a avaliação para aquela posição
            if board[r][c] ==  turn:
                total_score += eval_board[r][c]
            elif board[r][c] == other(turn):
                total_score -= eval_board[r][c]
    
    # dá uma pontuação extra caso haja duplas/triplas/quádruplas no tabuleiro
    # duplas/triplas/quádruplas horizontais
    for r in range(ROWS):
        for c in range(COLS - 3):
            window = [board[r][c+i] for i in range (4)]
            total_score += score_window(window, turn)

    # duplas/triplas/quádruplas verticais
    for c in range(COLS):
        for r in range(ROWS - 3):
            window = [board[r+i][c] for i in range(4)]
            total_score += score_window(window, turn)

    # duplas/triplas/quádruplas diagonais ↘
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r+i][c+i] for i in range(4)]
            total_score += score_window(window, turn)
            
    # duplas/triplas/quádruplas diagonais ↗
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            window = [board[r-i][c+i] for i in range(4)]
            total_score += score_window(window, turn)

    return total_score

def choose_move(board: List[List[int]], turn: int, config: Dict) -> Tuple[int, Dict]:
    """
    Decide a coluna (0..6) para jogar agora.

    Parâmetros:
      - board: matriz 6x7 com valores {0,1,2}
      - turn: 1 ou 2
      - config: {"max_time_ms": int, "max_depth": int}

    Retorna:
      - col: int (0..6)
    """
    max_time_ms = int(config.get("max_time_ms"))
    max_depth = int(config.get("max_depth"))
    turn = int(turn)

    print(f"AI choose_move called with max_time_ms={max_time_ms}, max_depth={max_depth}, player={turn}")
    
    start = time.time()

    # Função auxiliar para checar tempo decorrido   
    def time_exceeded():
        return max_time_ms > 0 and (time.time() - start) * 1000.0 >= max_time_ms
    
    legal = valid_moves(board)

    move = 0
    if not legal:
        # Sem jogadas: devolve 0 por convenção (servidor lida com isso)
        return move
    
    # minimax apenas calcula a melhor jogada possível.
    # é a função choose_move que deve guardar a melhor jogada encontrada e retornar no final, depois de avaliar todas as jogadas possíveis (dentro do limite de tempo)
    def minimax(board: List[List[int]], agent: Agent, depth: int, legal_moves: List[int], config: Dict): # passando o dicionário config pra conseguir pegar 
        
        #if winner(board) != 0: #! está desconsiderando o empate
        is_terminal = terminal(board)[0]
        winner_player = terminal(board)[1]

        if is_terminal:
            if winner_player == turn:
                return 1500
            elif winner_player == other(turn):
                return -1500
            elif winner_player == 0:
                return 0
            
        elif depth == 0 or time_exceeded():
            return evaluate(board, turn)
        
        if (agent == Agent.MAX):
            best_score_turn = -math.inf
            for move in legal_moves:
                new_board = make_move(board, move, turn) # usando turn ao invés de agent porque o make_move precisa do número do jogador (1 ou 2) e não do MAX/MIN
                score = minimax(new_board, Agent.MIN, depth - 1, valid_moves(new_board), config)
                best_score_turn = max(score, best_score_turn)
        else:
            best_score_turn = math.inf
            for move in legal_moves:
                new_board = make_move(board, move, other(turn)) # usando other(turn) para passar o número do jogador adversário
                score = minimax(new_board, Agent.MAX, depth - 1, valid_moves(new_board), config)       
                best_score_turn = min(score, best_score_turn)
        
        return best_score_turn
    
    # loop para escolher a melhor jogada possível, usando a função minimax para avaliar cada jogada
    best_move = None
    best_score = -math.inf
    for move in legal:
        new_board = make_move(board, move, turn)
        score = minimax(new_board, Agent.MIN, max_depth - 1, valid_moves(new_board), config)
        if score > best_score:
            best_score = score
            best_move = move

    return best_move

def choose_move_pruning(board: List[List[int]], turn: int, config: Dict) -> Tuple[int, Dict]:
    max_time_ms = int(config.get("max_time_ms"))
    max_depth = int(config.get("max_depth"))
    turn = int(turn)

    print(f"AI choose_move called with max_time_ms={max_time_ms}, max_depth={max_depth}, player={turn}")
    
    start = time.time()

    # Função auxiliar para checar tempo decorrido   
    def time_exceeded():
        return max_time_ms > 0 and (time.time() - start) * 1000.0 >= max_time_ms
    
    legal = valid_moves(board)

    move = 0
    if not legal:
        # Sem jogadas: devolve 0 por convenção (servidor lida com isso)
        return move
    
    # minimax apenas calcula a melhor jogada possível.
    # é a função choose_move que deve guardar a melhor jogada encontrada e retornar no final, depois de avaliar todas as jogadas possíveis (dentro do limite de tempo)
    def minimax_prune(board: List[List[int]], agent: Agent, depth: int, legal_moves: List[int], alpha: float, beta: float, config: Dict): # passando o dicionário config pra conseguir pegar 
        
        #if winner(board) != 0: #! está desconsiderando o empate
        is_terminal = terminal(board)[0]
        winner_player = terminal(board)[1]

        if is_terminal:
            if winner_player == turn:
                return 1500
            elif winner_player == other(turn):
                return -1500
            elif winner_player == 0:
                return 0
            
        elif depth == 0 or time_exceeded():
            return evaluate(board, turn)
        
        if (agent == Agent.MAX):
            best_score_turn = -math.inf
            for move in legal_moves:
                new_board = make_move(board, move, turn) # usando turn ao invés de agent porque o make_move precisa do número do jogador (1 ou 2) e não do MAX/MIN
                score = minimax_prune(new_board, Agent.MIN, depth - 1, valid_moves(new_board), alpha, beta, config)
                best_score_turn = max(score, best_score_turn)
                alpha = max(alpha, best_score_turn)
                if beta <= alpha:
                    break
        else:
            best_score_turn = math.inf
            for move in legal_moves:
                new_board = make_move(board, move, other(turn)) # usando other(turn) para passar o número do jogador adversário
                score = minimax_prune(new_board, Agent.MAX, depth - 1, valid_moves(new_board), alpha, beta, config)       
                best_score_turn = min(score, best_score_turn)
                beta = min(beta, best_score_turn)
                if beta <= alpha:  
                    break
        
        return best_score_turn
    
    # loop para escolher a melhor jogada possível, usando a função minimax para avaliar cada jogada
    best_move = None
    best_score = -math.inf
    for move in legal:
        new_board = make_move(board, move, turn)
        score = minimax_prune(new_board, Agent.MIN, max_depth - 1, valid_moves(new_board), -math.inf, math.inf, config)
        if score > best_score:
            best_score = score
            best_move = move

    return best_move

def choose_move_iterative(board: List[List[int]], turn: int, config: Dict) -> Tuple[int, Dict]:
    max_time_ms = int(config.get("max_time_ms"))
    max_depth = int(config.get("max_depth"))
    turn = int(turn)

    print(f"AI choose_move called with max_time_ms={max_time_ms}, max_depth={max_depth}, player={turn}")
    
    start = time.time()

    # Função auxiliar para checar tempo decorrido   
    def time_exceeded():
        return max_time_ms > 0 and (time.time() - start) * 1000.0 >= max_time_ms
    
    unordered_legal = valid_moves(board)

    move = 0
    if not unordered_legal:
        # Sem jogadas: devolve 0 por convenção (servidor lida com isso)
        return move

    def order_moves(moves: List[int]) -> List[int]:
        # Prioriza as colunas centrais, depois as adjacentes, e assim por diante
        center = COLS // 2
        return sorted(moves, key=lambda x: abs(x - center))
    
    legal = order_moves(unordered_legal)
    
    # minimax apenas calcula a melhor jogada possível.
    # é a função choose_move que deve guardar a melhor jogada encontrada e retornar no final, depois de avaliar todas as jogadas possíveis (dentro do limite de tempo)
    def minimax_iterative(board: List[List[int]], agent: Agent, depth: int, legal_moves: List[int], alpha: float, beta: float, config: Dict): # passando o dicionário config pra conseguir pegar 
        
        #if winner(board) != 0: #! está desconsiderando o empate
        is_terminal = terminal(board)[0]
        winner_player = terminal(board)[1]

        if is_terminal:
            if winner_player == turn:
                return 1500
            elif winner_player == other(turn):
                return -1500
            elif winner_player == 0:
                return 0
            
        elif depth == 0 or time_exceeded():
            return evaluate(board, turn)
        
        if (agent == Agent.MAX):
            best_score_turn = -math.inf
            for move in legal_moves:
                new_board = make_move(board, move, turn) # usando turn ao invés de agent porque o make_move precisa do número do jogador (1 ou 2) e não do MAX/MIN
                score = minimax_iterative(new_board, Agent.MIN, depth - 1, valid_moves(new_board), alpha, beta, config)
                best_score_turn = max(score, best_score_turn)
                alpha = max(alpha, best_score_turn)
                if beta <= alpha:
                    break
        else:
            best_score_turn = math.inf
            for move in legal_moves:
                new_board = make_move(board, move, other(turn)) # usando other(turn) para passar o número do jogador adversário
                score = minimax_iterative(new_board, Agent.MAX, depth - 1, valid_moves(new_board), alpha, beta, config)       
                best_score_turn = min(score, best_score_turn)
                beta = min(beta, best_score_turn)
                if beta <= alpha:  
                    break
        
        return best_score_turn
    
    # loop para escolher a melhor jogada possível, usando a função minimax para avaliar cada jogada
    best_move = legal[0] # default para o caso de não conseguir avaliar nenhuma jogada dentro do limite de tempo
    best_score = -math.inf
    for current_depth in range(1, max_depth + 1):
        if time_exceeded():
            break

        iteration_best_move = None
        iteration_best_score = -math.inf

        for move in legal:
            if time_exceeded():
                break

            new_board = make_move(board, move, turn)
            score = minimax_iterative(new_board, Agent.MIN, current_depth - 1, valid_moves(new_board), -math.inf, math.inf, config)
            if score > iteration_best_score:
                iteration_best_score = score
                iteration_best_move = move

        if iteration_best_move is not None: 
            best_move = iteration_best_move
            best_score = iteration_best_score

    return best_move

def choose_move_randomly(board: List[List[int]], turn: int, config: Dict) -> Tuple[int, Dict]:
    max_time_ms = int(config.get("max_time_ms"))
    max_depth = int(config.get("max_depth"))
    turn = int(turn)

    print(f"AI choose_move called with max_time_ms={max_time_ms}, max_depth={max_depth}, player={turn}")
    
    legal = valid_moves(board)

    move = 0
    if not legal:
        return move
    
    move = random.choice(legal)
    return move


def choose_move_infinity(board: List[List[int]], turn: int, config: Dict) -> Tuple[int, Dict]:
    """
    Decide a coluna (0..6) para jogar agora.

    Parâmetros:
      - board: matriz 6x7 com valores {0,1,2}
      - turn: 1 ou 2
      - config: {"max_time_ms": int, "max_depth": int}

    Retorna:
      - col: int (0..6)
    """
    max_time_ms = int(config.get("max_time_ms"))
    max_depth = int(config.get("max_depth"))
    turn = int(turn)

    print(f"AI choose_move called with max_time_ms={max_time_ms}, max_depth={max_depth}, player={turn}")
    
    start = time.time()

    # Função auxiliar para checar tempo decorrido   
    def time_exceeded():
        return max_time_ms > 0 and (time.time() - start) * 1000.0 >= max_time_ms
    
    legal = valid_moves(board)

    move = 0
    if not legal:
        # Sem jogadas: devolve 0 por convenção (servidor lida com isso)
        return move
    
    # VERSÃO INICIAL: escolhe aleatoriamente entre as jogadas legais
    i = 0
    while True:
        i += 1

    return move