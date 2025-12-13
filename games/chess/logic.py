"""国际象棋游戏逻辑模块"""

from enum import Enum
from typing import Optional, List, Tuple
import copy


class Player(Enum):
    """玩家枚举"""
    WHITE = 'white'
    BLACK = 'black'

    def opposite(self) -> 'Player':
        return Player.BLACK if self == Player.WHITE else Player.WHITE


class GameState(Enum):
    """游戏状态"""
    PLAYING = 0
    WHITE_WINS = 1
    BLACK_WINS = 2
    STALEMATE = 3


class ChessLogic:
    """国际象棋逻辑类"""

    PIECES = {
        'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
        'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟',
    }

    # 棋子价值（用于AI评估）
    PIECE_VALUES = {
        'P': 100, 'p': 100,
        'N': 320, 'n': 320,
        'B': 330, 'b': 330,
        'R': 500, 'r': 500,
        'Q': 900, 'q': 900,
        'K': 20000, 'k': 20000,
    }

    def __init__(self):
        self.reset()

    def reset(self):
        """重置游戏"""
        self.board: List[List[Optional[str]]] = [[None] * 8 for _ in range(8)]
        self.current_player = Player.WHITE
        self.state = GameState.PLAYING
        self.move_count = 0
        self.captured_white: List[str] = []
        self.captured_black: List[str] = []
        self.last_move: Optional[Tuple] = None
        self.can_castle = {
            Player.WHITE: {'king_side': True, 'queen_side': True},
            Player.BLACK: {'king_side': True, 'queen_side': True}
        }
        self.move_history: List[dict] = []  # 移动历史记录
        self._setup_board()

    def _setup_board(self):
        """初始化棋盘"""
        # 黑棋
        self.board[0] = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
        self.board[1] = ['p'] * 8
        # 白棋
        self.board[6] = ['P'] * 8
        self.board[7] = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']

    def get_board(self) -> List[List[Optional[str]]]:
        """获取棋盘状态"""
        return self.board

    def get_piece(self, row: int, col: int) -> Optional[str]:
        """获取指定位置的棋子"""
        return self.board[row][col]

    def get_piece_char(self, piece: str) -> str:
        """获取棋子的Unicode字符"""
        return self.PIECES.get(piece, '')

    def is_own_piece(self, piece: str, player: Optional[Player] = None) -> bool:
        """判断是否是指定玩家的棋子"""
        if player is None:
            player = self.current_player
        if player == Player.WHITE:
            return piece.isupper()
        return piece.islower()

    def is_enemy_piece(self, piece: str, player: Optional[Player] = None) -> bool:
        """判断是否是对方棋子"""
        if player is None:
            player = self.current_player
        if player == Player.WHITE:
            return piece.islower()
        return piece.isupper()

    def get_valid_moves(self, row: int, col: int) -> List[Tuple[int, int]]:
        """获取棋子的有效移动"""
        piece = self.board[row][col]
        if not piece:
            return []

        piece_type = piece.upper()
        moves = []

        if piece_type == 'P':
            moves = self._get_pawn_moves(row, col, piece.isupper())
        elif piece_type == 'R':
            moves = self._get_rook_moves(row, col)
        elif piece_type == 'N':
            moves = self._get_knight_moves(row, col)
        elif piece_type == 'B':
            moves = self._get_bishop_moves(row, col)
        elif piece_type == 'Q':
            moves = self._get_queen_moves(row, col)
        elif piece_type == 'K':
            moves = self._get_king_moves(row, col)

        # 过滤会导致被将的移动
        valid_moves = []
        for move in moves:
            if not self._would_be_in_check(row, col, move[0], move[1]):
                valid_moves.append(move)

        return valid_moves

    def _get_pawn_moves(self, row: int, col: int, is_white: bool) -> List[Tuple[int, int]]:
        """获取兵的移动"""
        moves = []
        direction = -1 if is_white else 1
        start_row = 6 if is_white else 1

        # 前进
        new_row = row + direction
        if 0 <= new_row < 8 and self.board[new_row][col] is None:
            moves.append((new_row, col))
            if row == start_row:
                new_row2 = row + 2 * direction
                if self.board[new_row2][col] is None:
                    moves.append((new_row2, col))

        # 斜吃
        for dc in [-1, 1]:
            new_col = col + dc
            if 0 <= new_col < 8 and 0 <= new_row < 8:
                target = self.board[new_row][new_col]
                if target and self.is_enemy_piece(target):
                    moves.append((new_row, new_col))

                # 吃过路兵
                if self.last_move:
                    last_piece, (from_r, from_c), (to_r, to_c) = self.last_move
                    if (last_piece.upper() == 'P' and
                        abs(from_r - to_r) == 2 and
                        to_r == row and to_c == new_col):
                        moves.append((new_row, new_col))

        return moves

    def _get_rook_moves(self, row: int, col: int) -> List[Tuple[int, int]]:
        """获取车的移动"""
        moves = []
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            for i in range(1, 8):
                new_row, new_col = row + dr * i, col + dc * i
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                target = self.board[new_row][new_col]
                if target is None:
                    moves.append((new_row, new_col))
                elif self.is_enemy_piece(target):
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        return moves

    def _get_knight_moves(self, row: int, col: int) -> List[Tuple[int, int]]:
        """获取马的移动"""
        moves = []
        offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                   (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in offsets:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.board[new_row][new_col]
                if target is None or self.is_enemy_piece(target):
                    moves.append((new_row, new_col))
        return moves

    def _get_bishop_moves(self, row: int, col: int) -> List[Tuple[int, int]]:
        """获取象的移动"""
        moves = []
        for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            for i in range(1, 8):
                new_row, new_col = row + dr * i, col + dc * i
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                target = self.board[new_row][new_col]
                if target is None:
                    moves.append((new_row, new_col))
                elif self.is_enemy_piece(target):
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        return moves

    def _get_queen_moves(self, row: int, col: int) -> List[Tuple[int, int]]:
        """获取皇后的移动"""
        return self._get_rook_moves(row, col) + self._get_bishop_moves(row, col)

    def _get_king_moves(self, row: int, col: int) -> List[Tuple[int, int]]:
        """获取国王的移动"""
        moves = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target = self.board[new_row][new_col]
                    if target is None or self.is_enemy_piece(target):
                        moves.append((new_row, new_col))

        # 王车易位
        if not self.is_in_check(self.current_player):
            castle = self.can_castle[self.current_player]
            if castle['king_side']:
                if (self.board[row][5] is None and
                    self.board[row][6] is None and
                    not self._would_be_in_check(row, col, row, 5) and
                    not self._would_be_in_check(row, col, row, 6)):
                    moves.append((row, 6))
            if castle['queen_side']:
                if (self.board[row][1] is None and
                    self.board[row][2] is None and
                    self.board[row][3] is None and
                    not self._would_be_in_check(row, col, row, 3) and
                    not self._would_be_in_check(row, col, row, 2)):
                    moves.append((row, 2))

        return moves

    def _would_be_in_check(self, from_row: int, from_col: int,
                           to_row: int, to_col: int) -> bool:
        """检查移动后是否会被将军"""
        piece = self.board[from_row][from_col]
        captured = self.board[to_row][to_col]
        self.board[from_row][from_col] = None
        self.board[to_row][to_col] = piece

        in_check = self.is_in_check(self.current_player)

        self.board[from_row][from_col] = piece
        self.board[to_row][to_col] = captured

        return in_check

    def is_in_check(self, player: Player) -> bool:
        """检查玩家是否被将军"""
        king = 'K' if player == Player.WHITE else 'k'
        king_pos = None
        for row in range(8):
            for col in range(8):
                if self.board[row][col] == king:
                    king_pos = (row, col)
                    break
            if king_pos:
                break

        if not king_pos:
            return False

        return self._is_under_attack(king_pos[0], king_pos[1], player)

    def _is_under_attack(self, row: int, col: int, player: Player) -> bool:
        """检查位置是否被攻击"""
        enemy = player.opposite()
        original = self.current_player
        self.current_player = enemy

        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and self.is_own_piece(piece):
                    piece_type = piece.upper()
                    moves = []
                    if piece_type == 'P':
                        direction = -1 if piece.isupper() else 1
                        for dc in [-1, 1]:
                            nr, nc = r + direction, c + dc
                            if 0 <= nr < 8 and 0 <= nc < 8:
                                moves.append((nr, nc))
                    elif piece_type == 'R':
                        moves = self._get_rook_moves(r, c)
                    elif piece_type == 'N':
                        moves = self._get_knight_moves(r, c)
                    elif piece_type == 'B':
                        moves = self._get_bishop_moves(r, c)
                    elif piece_type == 'Q':
                        moves = self._get_queen_moves(r, c)
                    elif piece_type == 'K':
                        for dr in [-1, 0, 1]:
                            for dc in [-1, 0, 1]:
                                if dr == 0 and dc == 0:
                                    continue
                                nr, nc = r + dr, c + dc
                                if 0 <= nr < 8 and 0 <= nc < 8:
                                    moves.append((nr, nc))

                    if (row, col) in moves:
                        self.current_player = original
                        return True

        self.current_player = original
        return False

    def make_move(self, from_row: int, from_col: int,
                  to_row: int, to_col: int) -> bool:
        """执行移动"""
        if (to_row, to_col) not in self.get_valid_moves(from_row, from_col):
            return False

        piece = self.board[from_row][from_col]
        captured = self.board[to_row][to_col]

        # 保存移动前的状态用于悔棋
        move_record = {
            'from_pos': (from_row, from_col),
            'to_pos': (to_row, to_col),
            'piece': piece,
            'captured': captured,
            'last_move': self.last_move,
            'can_castle': {
                Player.WHITE: dict(self.can_castle[Player.WHITE]),
                Player.BLACK: dict(self.can_castle[Player.BLACK])
            },
            'en_passant_capture': None,
            'castling': None,
            'promotion': None,
        }

        # 记录被吃棋子
        if captured:
            if captured.isupper():
                self.captured_white.append(captured)
            else:
                self.captured_black.append(captured)

        # 吃过路兵
        if piece.upper() == 'P' and captured is None and from_col != to_col:
            en_passant_pawn = self.board[from_row][to_col]
            if en_passant_pawn:
                move_record['en_passant_capture'] = (from_row, to_col, en_passant_pawn)
                if en_passant_pawn.isupper():
                    self.captured_white.append(en_passant_pawn)
                else:
                    self.captured_black.append(en_passant_pawn)
                self.board[from_row][to_col] = None

        # 王车易位
        if piece.upper() == 'K' and abs(to_col - from_col) == 2:
            if to_col == 6:
                move_record['castling'] = ('king_side', to_row)
                self.board[to_row][5] = self.board[to_row][7]
                self.board[to_row][7] = None
            elif to_col == 2:
                move_record['castling'] = ('queen_side', to_row)
                self.board[to_row][3] = self.board[to_row][0]
                self.board[to_row][0] = None

        # 执行移动
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None

        # 兵升变
        if piece.upper() == 'P':
            if (piece.isupper() and to_row == 0) or (piece.islower() and to_row == 7):
                move_record['promotion'] = piece
                self.board[to_row][to_col] = 'Q' if piece.isupper() else 'q'

        # 更新易位权限
        if piece.upper() == 'K':
            self.can_castle[self.current_player]['king_side'] = False
            self.can_castle[self.current_player]['queen_side'] = False
        elif piece.upper() == 'R':
            if from_col == 0:
                self.can_castle[self.current_player]['queen_side'] = False
            elif from_col == 7:
                self.can_castle[self.current_player]['king_side'] = False

        self.last_move = (piece, (from_row, from_col), (to_row, to_col))
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

        # 如果有升变，恢复原来的兵
        if record['promotion']:
            piece = record['promotion']

        # 恢复棋子位置
        self.board[from_row][from_col] = piece
        self.board[to_row][to_col] = captured

        # 恢复吃过路兵
        if record['en_passant_capture']:
            ep_row, ep_col, ep_pawn = record['en_passant_capture']
            self.board[ep_row][ep_col] = ep_pawn
            if ep_pawn.isupper():
                self.captured_white.pop()
            else:
                self.captured_black.pop()

        # 恢复王车易位
        if record['castling']:
            side, row = record['castling']
            if side == 'king_side':
                self.board[row][7] = self.board[row][5]
                self.board[row][5] = None
            else:
                self.board[row][0] = self.board[row][3]
                self.board[row][3] = None

        # 恢复被吃棋子的记录
        if captured:
            if captured.isupper():
                self.captured_white.pop()
            else:
                self.captured_black.pop()

        # 恢复其他状态
        self.last_move = record['last_move']
        self.can_castle = record['can_castle']
        self.move_count -= 1
        self.current_player = self.current_player.opposite()
        self.state = GameState.PLAYING

        return True

    def can_undo(self) -> bool:
        """是否可以悔棋"""
        return len(self.move_history) > 0

    def _check_game_over(self):
        """检查游戏是否结束"""
        has_legal_moves = False
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and self.is_own_piece(piece):
                    if self.get_valid_moves(row, col):
                        has_legal_moves = True
                        break
            if has_legal_moves:
                break

        if not has_legal_moves:
            if self.is_in_check(self.current_player):
                self.state = (GameState.BLACK_WINS
                              if self.current_player == Player.WHITE
                              else GameState.WHITE_WINS)
            else:
                self.state = GameState.STALEMATE

    def get_all_moves(self, player: Optional[Player] = None) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """获取指定玩家的所有合法移动"""
        if player is None:
            player = self.current_player
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and self.is_own_piece(piece, player):
                    for move in self.get_valid_moves(row, col):
                        moves.append(((row, col), move))
        return moves

    def clone(self) -> 'ChessLogic':
        """克隆游戏状态"""
        new_game = ChessLogic.__new__(ChessLogic)
        new_game.board = [row[:] for row in self.board]
        new_game.current_player = self.current_player
        new_game.state = self.state
        new_game.move_count = self.move_count
        new_game.captured_white = self.captured_white[:]
        new_game.captured_black = self.captured_black[:]
        new_game.last_move = self.last_move
        new_game.can_castle = {
            Player.WHITE: dict(self.can_castle[Player.WHITE]),
            Player.BLACK: dict(self.can_castle[Player.BLACK])
        }
        return new_game

    def evaluate(self) -> int:
        """评估棋盘局面（正值对白方有利）"""
        if self.state == GameState.WHITE_WINS:
            return 100000
        elif self.state == GameState.BLACK_WINS:
            return -100000
        elif self.state == GameState.STALEMATE:
            return 0

        score = 0
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    value = self.PIECE_VALUES.get(piece, 0)
                    if piece.isupper():
                        score += value
                        # 位置奖励
                        if piece == 'P':
                            score += (6 - row) * 10  # 兵越前越好
                    else:
                        score -= value
                        if piece == 'p':
                            score -= (row - 1) * 10

        return score

    def is_game_over(self) -> bool:
        return self.state != GameState.PLAYING

    def get_winner(self) -> Optional[Player]:
        if self.state == GameState.WHITE_WINS:
            return Player.WHITE
        elif self.state == GameState.BLACK_WINS:
            return Player.BLACK
        return None
