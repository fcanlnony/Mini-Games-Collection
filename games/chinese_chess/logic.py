"""中国象棋游戏逻辑模块"""

from enum import Enum
from typing import Optional, List, Tuple


# 棋盘尺寸
BOARD_COLS = 9
BOARD_ROWS = 10


class Player(Enum):
    """玩家枚举"""
    RED = 'red'
    BLACK = 'black'

    def opposite(self) -> 'Player':
        return Player.BLACK if self == Player.RED else Player.RED


class PieceType(Enum):
    """棋子类型"""
    GENERAL = 'general'   # 将/帅
    ADVISOR = 'advisor'   # 士/仕
    ELEPHANT = 'elephant' # 象/相
    HORSE = 'horse'       # 马
    CHARIOT = 'chariot'   # 车
    CANNON = 'cannon'     # 炮
    SOLDIER = 'soldier'   # 兵/卒


class GameState(Enum):
    """游戏状态"""
    PLAYING = 0
    RED_WINS = 1
    BLACK_WINS = 2
    STALEMATE = 3


# 棋子字符
PIECE_CHARS = {
    (Player.RED, PieceType.GENERAL): '帥',
    (Player.RED, PieceType.ADVISOR): '仕',
    (Player.RED, PieceType.ELEPHANT): '相',
    (Player.RED, PieceType.HORSE): '馬',
    (Player.RED, PieceType.CHARIOT): '車',
    (Player.RED, PieceType.CANNON): '炮',
    (Player.RED, PieceType.SOLDIER): '兵',
    (Player.BLACK, PieceType.GENERAL): '將',
    (Player.BLACK, PieceType.ADVISOR): '士',
    (Player.BLACK, PieceType.ELEPHANT): '象',
    (Player.BLACK, PieceType.HORSE): '馬',
    (Player.BLACK, PieceType.CHARIOT): '車',
    (Player.BLACK, PieceType.CANNON): '砲',
    (Player.BLACK, PieceType.SOLDIER): '卒',
}

# 棋子价值
PIECE_VALUES = {
    PieceType.GENERAL: 10000,
    PieceType.ADVISOR: 20,
    PieceType.ELEPHANT: 20,
    PieceType.HORSE: 40,
    PieceType.CHARIOT: 90,
    PieceType.CANNON: 45,
    PieceType.SOLDIER: 10,
}


class Piece:
    """棋子类"""

    def __init__(self, piece_type: PieceType, color: Player):
        self.piece_type = piece_type
        self.color = color

    @property
    def char(self) -> str:
        return PIECE_CHARS.get((self.color, self.piece_type), '?')

    @property
    def value(self) -> int:
        return PIECE_VALUES.get(self.piece_type, 0)

    def __repr__(self):
        return f"Piece({self.piece_type.value}, {self.color.value})"


class ChineseChessLogic:
    """中国象棋逻辑类"""

    def __init__(self):
        self.reset()

    def reset(self):
        """重置游戏"""
        self.board: List[List[Optional[Piece]]] = [
            [None] * BOARD_COLS for _ in range(BOARD_ROWS)
        ]
        self.current_player = Player.RED
        self.state = GameState.PLAYING
        self.move_count = 0
        self.captured_red: List[Piece] = []
        self.captured_black: List[Piece] = []
        self.move_history: List[dict] = []  # 移动历史记录
        self._setup_board()

    def _setup_board(self):
        """初始化棋盘"""
        # 黑方（顶部）
        self.board[0][0] = Piece(PieceType.CHARIOT, Player.BLACK)
        self.board[0][1] = Piece(PieceType.HORSE, Player.BLACK)
        self.board[0][2] = Piece(PieceType.ELEPHANT, Player.BLACK)
        self.board[0][3] = Piece(PieceType.ADVISOR, Player.BLACK)
        self.board[0][4] = Piece(PieceType.GENERAL, Player.BLACK)
        self.board[0][5] = Piece(PieceType.ADVISOR, Player.BLACK)
        self.board[0][6] = Piece(PieceType.ELEPHANT, Player.BLACK)
        self.board[0][7] = Piece(PieceType.HORSE, Player.BLACK)
        self.board[0][8] = Piece(PieceType.CHARIOT, Player.BLACK)
        self.board[2][1] = Piece(PieceType.CANNON, Player.BLACK)
        self.board[2][7] = Piece(PieceType.CANNON, Player.BLACK)
        for col in [0, 2, 4, 6, 8]:
            self.board[3][col] = Piece(PieceType.SOLDIER, Player.BLACK)

        # 红方（底部）
        self.board[9][0] = Piece(PieceType.CHARIOT, Player.RED)
        self.board[9][1] = Piece(PieceType.HORSE, Player.RED)
        self.board[9][2] = Piece(PieceType.ELEPHANT, Player.RED)
        self.board[9][3] = Piece(PieceType.ADVISOR, Player.RED)
        self.board[9][4] = Piece(PieceType.GENERAL, Player.RED)
        self.board[9][5] = Piece(PieceType.ADVISOR, Player.RED)
        self.board[9][6] = Piece(PieceType.ELEPHANT, Player.RED)
        self.board[9][7] = Piece(PieceType.HORSE, Player.RED)
        self.board[9][8] = Piece(PieceType.CHARIOT, Player.RED)
        self.board[7][1] = Piece(PieceType.CANNON, Player.RED)
        self.board[7][7] = Piece(PieceType.CANNON, Player.RED)
        for col in [0, 2, 4, 6, 8]:
            self.board[6][col] = Piece(PieceType.SOLDIER, Player.RED)

    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        return self.board[row][col]

    def _is_in_palace(self, row: int, col: int, color: Player) -> bool:
        """是否在九宫格内"""
        if col < 3 or col > 5:
            return False
        if color == Player.RED:
            return row >= 7
        return row <= 2

    def _is_on_own_side(self, row: int, color: Player) -> bool:
        """是否在己方区域"""
        if color == Player.RED:
            return row >= 5
        return row <= 4

    def _get_piece_moves(self, row: int, col: int, piece: Piece) -> List[Tuple[int, int]]:
        """获取棋子的基本移动（不考虑将军）"""
        moves = []
        color = piece.color

        if piece.piece_type == PieceType.GENERAL:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = row + dr, col + dc
                if 0 <= nr < BOARD_ROWS and 0 <= nc < BOARD_COLS:
                    if self._is_in_palace(nr, nc, color):
                        target = self.board[nr][nc]
                        if target is None or target.color != color:
                            moves.append((nr, nc))

        elif piece.piece_type == PieceType.ADVISOR:
            for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                nr, nc = row + dr, col + dc
                if 0 <= nr < BOARD_ROWS and 0 <= nc < BOARD_COLS:
                    if self._is_in_palace(nr, nc, color):
                        target = self.board[nr][nc]
                        if target is None or target.color != color:
                            moves.append((nr, nc))

        elif piece.piece_type == PieceType.ELEPHANT:
            for dr, dc, edr, edc in [(-2, -2, -1, -1), (-2, 2, -1, 1),
                                      (2, -2, 1, -1), (2, 2, 1, 1)]:
                nr, nc = row + dr, col + dc
                er, ec = row + edr, col + edc
                if 0 <= nr < BOARD_ROWS and 0 <= nc < BOARD_COLS:
                    if self._is_on_own_side(nr, color):
                        if self.board[er][ec] is None:
                            target = self.board[nr][nc]
                            if target is None or target.color != color:
                                moves.append((nr, nc))

        elif piece.piece_type == PieceType.HORSE:
            for dr, dc, lr, lc in [(-2, -1, -1, 0), (-2, 1, -1, 0),
                                    (-1, -2, 0, -1), (-1, 2, 0, 1),
                                    (1, -2, 0, -1), (1, 2, 0, 1),
                                    (2, -1, 1, 0), (2, 1, 1, 0)]:
                nr, nc = row + dr, col + dc
                leg_r, leg_c = row + lr, col + lc
                if 0 <= nr < BOARD_ROWS and 0 <= nc < BOARD_COLS:
                    if self.board[leg_r][leg_c] is None:
                        target = self.board[nr][nc]
                        if target is None or target.color != color:
                            moves.append((nr, nc))

        elif piece.piece_type == PieceType.CHARIOT:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                for i in range(1, max(BOARD_ROWS, BOARD_COLS)):
                    nr, nc = row + dr * i, col + dc * i
                    if not (0 <= nr < BOARD_ROWS and 0 <= nc < BOARD_COLS):
                        break
                    target = self.board[nr][nc]
                    if target is None:
                        moves.append((nr, nc))
                    elif target.color != color:
                        moves.append((nr, nc))
                        break
                    else:
                        break

        elif piece.piece_type == PieceType.CANNON:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                jumped = False
                for i in range(1, max(BOARD_ROWS, BOARD_COLS)):
                    nr, nc = row + dr * i, col + dc * i
                    if not (0 <= nr < BOARD_ROWS and 0 <= nc < BOARD_COLS):
                        break
                    target = self.board[nr][nc]
                    if not jumped:
                        if target is None:
                            moves.append((nr, nc))
                        else:
                            jumped = True
                    else:
                        if target is not None:
                            if target.color != color:
                                moves.append((nr, nc))
                            break

        elif piece.piece_type == PieceType.SOLDIER:
            forward = -1 if color == Player.RED else 1
            crossed = not self._is_on_own_side(row, color)

            nr = row + forward
            if 0 <= nr < BOARD_ROWS:
                target = self.board[nr][col]
                if target is None or target.color != color:
                    moves.append((nr, col))

            if crossed:
                for dc in [-1, 1]:
                    nc = col + dc
                    if 0 <= nc < BOARD_COLS:
                        target = self.board[row][nc]
                        if target is None or target.color != color:
                            moves.append((row, nc))

        return moves

    def _find_general(self, color: Player) -> Optional[Tuple[int, int]]:
        """找到将/帅位置"""
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = self.board[row][col]
                if piece and piece.color == color and piece.piece_type == PieceType.GENERAL:
                    return (row, col)
        return None

    def _generals_facing(self) -> bool:
        """两将是否对面"""
        red_pos = self._find_general(Player.RED)
        black_pos = self._find_general(Player.BLACK)

        if not red_pos or not black_pos:
            return False
        if red_pos[1] != black_pos[1]:
            return False

        col = red_pos[1]
        min_row = min(red_pos[0], black_pos[0])
        max_row = max(red_pos[0], black_pos[0])

        for row in range(min_row + 1, max_row):
            if self.board[row][col] is not None:
                return False
        return True

    def is_in_check(self, color: Player) -> bool:
        """检查是否被将军"""
        general_pos = self._find_general(color)
        if not general_pos:
            return True

        enemy = color.opposite()

        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = self.board[row][col]
                if piece and piece.color == enemy:
                    moves = self._get_piece_moves(row, col, piece)
                    if general_pos in moves:
                        return True

        if self._generals_facing():
            return True

        return False

    def _would_be_in_check(self, from_row: int, from_col: int,
                           to_row: int, to_col: int, color: Player) -> bool:
        """移动后是否会被将"""
        piece = self.board[from_row][from_col]
        captured = self.board[to_row][to_col]
        self.board[from_row][from_col] = None
        self.board[to_row][to_col] = piece

        in_check = self.is_in_check(color)

        self.board[from_row][from_col] = piece
        self.board[to_row][to_col] = captured

        return in_check

    def get_valid_moves(self, row: int, col: int) -> List[Tuple[int, int]]:
        """获取有效移动（排除被将）"""
        piece = self.board[row][col]
        if not piece:
            return []

        moves = self._get_piece_moves(row, col, piece)
        valid = []
        for move in moves:
            if not self._would_be_in_check(row, col, move[0], move[1], piece.color):
                valid.append(move)
        return valid

    def make_move(self, from_row: int, from_col: int,
                  to_row: int, to_col: int) -> bool:
        """执行移动"""
        if (to_row, to_col) not in self.get_valid_moves(from_row, from_col):
            return False

        piece = self.board[from_row][from_col]
        captured = self.board[to_row][to_col]

        # 保存移动记录用于悔棋
        move_record = {
            'from_pos': (from_row, from_col),
            'to_pos': (to_row, to_col),
            'piece': Piece(piece.piece_type, piece.color),
            'captured': Piece(captured.piece_type, captured.color) if captured else None,
        }

        if captured:
            if captured.color == Player.RED:
                self.captured_red.append(captured)
            else:
                self.captured_black.append(captured)

        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None

        self.move_count += 1
        self.current_player = self.current_player.opposite()

        # 保存移动记录
        self.move_history.append(move_record)

        self._check_game_over()
        return True

    def undo(self) -> bool:
        """悔棋，返回是否成功"""
        if not self.move_history:
            return False

        record = self.move_history.pop()

        from_row, from_col = record['from_pos']
        to_row, to_col = record['to_pos']
        piece = record['piece']
        captured = record['captured']

        # 恢复棋子位置
        self.board[from_row][from_col] = piece
        self.board[to_row][to_col] = captured

        # 恢复被吃棋子的记录
        if captured:
            if captured.color == Player.RED:
                self.captured_red.pop()
            else:
                self.captured_black.pop()

        # 恢复其他状态
        self.move_count -= 1
        self.current_player = self.current_player.opposite()
        self.state = GameState.PLAYING

        return True

    def can_undo(self) -> bool:
        """是否可以悔棋"""
        return len(self.move_history) > 0

    def _has_legal_moves(self, color: Player) -> bool:
        """是否有合法移动"""
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    if self.get_valid_moves(row, col):
                        return True
        return False

    def _check_game_over(self):
        """检查游戏结束"""
        if not self._has_legal_moves(self.current_player):
            winner = self.current_player.opposite()
            if self.is_in_check(self.current_player):
                self.state = (GameState.RED_WINS if winner == Player.RED
                              else GameState.BLACK_WINS)
            else:
                self.state = GameState.STALEMATE

    def get_all_moves(self, player: Optional[Player] = None) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """获取所有合法移动"""
        if player is None:
            player = self.current_player
        moves = []
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = self.board[row][col]
                if piece and piece.color == player:
                    for move in self.get_valid_moves(row, col):
                        moves.append(((row, col), move))
        return moves

    def clone(self) -> 'ChineseChessLogic':
        """克隆游戏状态"""
        new_game = ChineseChessLogic.__new__(ChineseChessLogic)
        new_game.board = [[None] * BOARD_COLS for _ in range(BOARD_ROWS)]
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                p = self.board[r][c]
                if p:
                    new_game.board[r][c] = Piece(p.piece_type, p.color)
        new_game.current_player = self.current_player
        new_game.state = self.state
        new_game.move_count = self.move_count
        new_game.captured_red = [Piece(p.piece_type, p.color) for p in self.captured_red]
        new_game.captured_black = [Piece(p.piece_type, p.color) for p in self.captured_black]
        return new_game

    def evaluate(self) -> int:
        """评估局面（正值对红方有利）"""
        if self.state == GameState.RED_WINS:
            return 100000
        elif self.state == GameState.BLACK_WINS:
            return -100000
        elif self.state == GameState.STALEMATE:
            return 0

        score = 0
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = self.board[row][col]
                if piece:
                    value = piece.value
                    # 位置奖励
                    if piece.piece_type == PieceType.SOLDIER:
                        if piece.color == Player.RED:
                            if row < 5:  # 过河
                                value += 20
                        else:
                            if row > 4:
                                value += 20

                    if piece.color == Player.RED:
                        score += value
                    else:
                        score -= value

        return score

    def is_game_over(self) -> bool:
        return self.state != GameState.PLAYING

    def get_winner(self) -> Optional[Player]:
        if self.state == GameState.RED_WINS:
            return Player.RED
        elif self.state == GameState.BLACK_WINS:
            return Player.BLACK
        return None
