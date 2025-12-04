"""中国象棋游戏 - 模块化设计"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, Adw
import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])
from i18n import _


# =============================================================================
# 常量定义
# =============================================================================

# 棋盘尺寸: 9列 x 10行
BOARD_COLS = 9
BOARD_ROWS = 10

# 棋子类型
class PieceType:
    """棋子类型枚举"""
    GENERAL = 'general'  # 将/帅
    ADVISOR = 'advisor'  # 士/仕
    ELEPHANT = 'elephant'  # 象/相
    HORSE = 'horse'  # 马
    CHARIOT = 'chariot'  # 车
    CANNON = 'cannon'  # 炮
    SOLDIER = 'soldier'  # 兵/卒


# 棋子显示字符
PIECE_CHARS = {
    ('red', PieceType.GENERAL): '帥',
    ('red', PieceType.ADVISOR): '仕',
    ('red', PieceType.ELEPHANT): '相',
    ('red', PieceType.HORSE): '馬',
    ('red', PieceType.CHARIOT): '車',
    ('red', PieceType.CANNON): '炮',
    ('red', PieceType.SOLDIER): '兵',
    ('black', PieceType.GENERAL): '將',
    ('black', PieceType.ADVISOR): '士',
    ('black', PieceType.ELEPHANT): '象',
    ('black', PieceType.HORSE): '馬',
    ('black', PieceType.CHARIOT): '車',
    ('black', PieceType.CANNON): '砲',
    ('black', PieceType.SOLDIER): '卒',
}


# =============================================================================
# 棋子类
# =============================================================================

class Piece:
    """棋子类"""

    def __init__(self, piece_type, color):
        """
        Args:
            piece_type: PieceType 枚举值
            color: 'red' 或 'black'
        """
        self.piece_type = piece_type
        self.color = color

    def __repr__(self):
        return f"Piece({self.piece_type}, {self.color})"

    @property
    def char(self):
        """获取棋子显示字符"""
        return PIECE_CHARS.get((self.color, self.piece_type), '?')


# =============================================================================
# 规则引擎
# =============================================================================

class ChineseChessRules:
    """中国象棋规则引擎"""

    @staticmethod
    def is_in_palace(row, col, color):
        """检查位置是否在九宫格内"""
        if col < 3 or col > 5:
            return False
        if color == 'red':
            return row >= 7
        else:
            return row <= 2

    @staticmethod
    def is_on_own_side(row, color):
        """检查是否在己方区域（未过河）"""
        if color == 'red':
            return row >= 5
        else:
            return row <= 4

    @staticmethod
    def get_general_moves(board, row, col, color):
        """获取将/帅的合法移动"""
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if not (0 <= new_row < BOARD_ROWS and 0 <= new_col < BOARD_COLS):
                continue
            if not ChineseChessRules.is_in_palace(new_row, new_col, color):
                continue
            target = board[new_row][new_col]
            if target is None or target.color != color:
                moves.append((new_row, new_col))

        return moves

    @staticmethod
    def get_advisor_moves(board, row, col, color):
        """获取士/仕的合法移动"""
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if not (0 <= new_row < BOARD_ROWS and 0 <= new_col < BOARD_COLS):
                continue
            if not ChineseChessRules.is_in_palace(new_row, new_col, color):
                continue
            target = board[new_row][new_col]
            if target is None or target.color != color:
                moves.append((new_row, new_col))

        return moves

    @staticmethod
    def get_elephant_moves(board, row, col, color):
        """获取象/相的合法移动（走田字，不能过河，有塞象眼）"""
        moves = []
        # 田字的四个方向：(行偏移, 列偏移, 象眼行偏移, 象眼列偏移)
        directions = [
            (-2, -2, -1, -1),
            (-2, 2, -1, 1),
            (2, -2, 1, -1),
            (2, 2, 1, 1)
        ]

        for dr, dc, eye_dr, eye_dc in directions:
            new_row, new_col = row + dr, col + dc
            eye_row, eye_col = row + eye_dr, col + eye_dc

            if not (0 <= new_row < BOARD_ROWS and 0 <= new_col < BOARD_COLS):
                continue
            # 不能过河
            if not ChineseChessRules.is_on_own_side(new_row, color):
                continue
            # 检查象眼是否被塞
            if board[eye_row][eye_col] is not None:
                continue
            target = board[new_row][new_col]
            if target is None or target.color != color:
                moves.append((new_row, new_col))

        return moves

    @staticmethod
    def get_horse_moves(board, row, col, color):
        """获取马的合法移动（走日字，有蹩马腿）"""
        moves = []
        # 马的八个方向：(行偏移, 列偏移, 马腿行偏移, 马腿列偏移)
        directions = [
            (-2, -1, -1, 0),
            (-2, 1, -1, 0),
            (-1, -2, 0, -1),
            (-1, 2, 0, 1),
            (1, -2, 0, -1),
            (1, 2, 0, 1),
            (2, -1, 1, 0),
            (2, 1, 1, 0)
        ]

        for dr, dc, leg_dr, leg_dc in directions:
            new_row, new_col = row + dr, col + dc
            leg_row, leg_col = row + leg_dr, col + leg_dc

            if not (0 <= new_row < BOARD_ROWS and 0 <= new_col < BOARD_COLS):
                continue
            # 检查是否蹩马腿
            if board[leg_row][leg_col] is not None:
                continue
            target = board[new_row][new_col]
            if target is None or target.color != color:
                moves.append((new_row, new_col))

        return moves

    @staticmethod
    def get_chariot_moves(board, row, col, color):
        """获取车的合法移动（直线任意格）"""
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            for i in range(1, max(BOARD_ROWS, BOARD_COLS)):
                new_row, new_col = row + dr * i, col + dc * i
                if not (0 <= new_row < BOARD_ROWS and 0 <= new_col < BOARD_COLS):
                    break
                target = board[new_row][new_col]
                if target is None:
                    moves.append((new_row, new_col))
                elif target.color != color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break

        return moves

    @staticmethod
    def get_cannon_moves(board, row, col, color):
        """获取炮的合法移动（直线移动，吃子需要翻山）"""
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            jumped = False
            for i in range(1, max(BOARD_ROWS, BOARD_COLS)):
                new_row, new_col = row + dr * i, col + dc * i
                if not (0 <= new_row < BOARD_ROWS and 0 <= new_col < BOARD_COLS):
                    break
                target = board[new_row][new_col]

                if not jumped:
                    # 还没翻山
                    if target is None:
                        moves.append((new_row, new_col))
                    else:
                        jumped = True  # 遇到棋子，准备翻山
                else:
                    # 已经翻山
                    if target is not None:
                        if target.color != color:
                            moves.append((new_row, new_col))
                        break  # 无论是否吃子，都停止

        return moves

    @staticmethod
    def get_soldier_moves(board, row, col, color):
        """获取兵/卒的合法移动（未过河只能前进，过河后可横走）"""
        moves = []
        forward = -1 if color == 'red' else 1
        crossed_river = not ChineseChessRules.is_on_own_side(row, color)

        # 前进
        new_row = row + forward
        if 0 <= new_row < BOARD_ROWS:
            target = board[new_row][col]
            if target is None or target.color != color:
                moves.append((new_row, col))

        # 过河后可以横走
        if crossed_river:
            for dc in [-1, 1]:
                new_col = col + dc
                if 0 <= new_col < BOARD_COLS:
                    target = board[row][new_col]
                    if target is None or target.color != color:
                        moves.append((row, new_col))

        return moves

    @staticmethod
    def get_piece_moves(board, row, col, piece):
        """根据棋子类型获取合法移动"""
        if piece.piece_type == PieceType.GENERAL:
            return ChineseChessRules.get_general_moves(board, row, col, piece.color)
        elif piece.piece_type == PieceType.ADVISOR:
            return ChineseChessRules.get_advisor_moves(board, row, col, piece.color)
        elif piece.piece_type == PieceType.ELEPHANT:
            return ChineseChessRules.get_elephant_moves(board, row, col, piece.color)
        elif piece.piece_type == PieceType.HORSE:
            return ChineseChessRules.get_horse_moves(board, row, col, piece.color)
        elif piece.piece_type == PieceType.CHARIOT:
            return ChineseChessRules.get_chariot_moves(board, row, col, piece.color)
        elif piece.piece_type == PieceType.CANNON:
            return ChineseChessRules.get_cannon_moves(board, row, col, piece.color)
        elif piece.piece_type == PieceType.SOLDIER:
            return ChineseChessRules.get_soldier_moves(board, row, col, piece.color)
        return []

    @staticmethod
    def find_general(board, color):
        """找到指定颜色的将/帅位置"""
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = board[row][col]
                if piece and piece.color == color and piece.piece_type == PieceType.GENERAL:
                    return (row, col)
        return None

    @staticmethod
    def generals_facing(board):
        """检查两个将/帅是否对面（同一列且中间无子）"""
        red_pos = ChineseChessRules.find_general(board, 'red')
        black_pos = ChineseChessRules.find_general(board, 'black')

        if not red_pos or not black_pos:
            return False

        if red_pos[1] != black_pos[1]:
            return False

        col = red_pos[1]
        min_row = min(red_pos[0], black_pos[0])
        max_row = max(red_pos[0], black_pos[0])

        for row in range(min_row + 1, max_row):
            if board[row][col] is not None:
                return False

        return True

    @staticmethod
    def is_in_check(board, color):
        """检查指定颜色是否被将军"""
        general_pos = ChineseChessRules.find_general(board, color)
        if not general_pos:
            return True  # 将/帅不存在，认为被将

        enemy_color = 'black' if color == 'red' else 'red'

        # 检查是否有敌方棋子可以攻击将/帅
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = board[row][col]
                if piece and piece.color == enemy_color:
                    moves = ChineseChessRules.get_piece_moves(board, row, col, piece)
                    if general_pos in moves:
                        return True

        # 检查两将对面
        if ChineseChessRules.generals_facing(board):
            return True

        return False

    @staticmethod
    def would_be_in_check(board, from_row, from_col, to_row, to_col, color):
        """检查移动后是否会被将军"""
        # 模拟移动
        piece = board[from_row][from_col]
        captured = board[to_row][to_col]
        board[from_row][from_col] = None
        board[to_row][to_col] = piece

        in_check = ChineseChessRules.is_in_check(board, color)

        # 恢复棋盘
        board[from_row][from_col] = piece
        board[to_row][to_col] = captured

        return in_check

    @staticmethod
    def get_valid_moves(board, row, col):
        """获取棋子的所有有效移动（排除会导致被将的移动）"""
        piece = board[row][col]
        if not piece:
            return []

        moves = ChineseChessRules.get_piece_moves(board, row, col, piece)
        valid_moves = []

        for move in moves:
            if not ChineseChessRules.would_be_in_check(board, row, col, move[0], move[1], piece.color):
                valid_moves.append(move)

        return valid_moves

    @staticmethod
    def has_legal_moves(board, color):
        """检查指定颜色是否还有合法移动"""
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = board[row][col]
                if piece and piece.color == color:
                    if ChineseChessRules.get_valid_moves(board, row, col):
                        return True
        return False


# =============================================================================
# 游戏主类
# =============================================================================

class ChineseChess:
    """中国象棋游戏"""

    def __init__(self, score_manager):
        self.score_manager = score_manager
        self.board = [[None] * BOARD_COLS for _ in range(BOARD_ROWS)]
        self.selected = None
        self.valid_moves = []
        self.current_player = 'red'
        self.game_over = False
        self.move_count = 0
        self.captured_red = []
        self.captured_black = []

        self.widget = self._create_widget()
        self.new_game()

    def _create_widget(self):
        """创建游戏界面"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(16)
        main_box.set_margin_bottom(16)
        main_box.set_margin_start(16)
        main_box.set_margin_end(16)
        main_box.set_halign(Gtk.Align.CENTER)
        main_box.set_valign(Gtk.Align.CENTER)

        # 状态显示
        self.status_label = Gtk.Label(label=_("xiangqi_red_turn"))
        self.status_label.add_css_class("title-3")
        main_box.append(self.status_label)

        # 被吃棋子显示（黑方）
        self.captured_black_label = Gtk.Label(label="")
        self.captured_black_label.set_halign(Gtk.Align.CENTER)
        main_box.append(self.captured_black_label)

        # 棋盘容器
        board_frame = Gtk.Frame()
        board_frame.add_css_class("card")
        main_box.append(board_frame)

        board_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        board_box.set_margin_top(8)
        board_box.set_margin_bottom(8)
        board_box.set_margin_start(8)
        board_box.set_margin_end(8)
        board_frame.set_child(board_box)

        # 创建棋盘网格
        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(0)
        self.grid.set_column_spacing(0)
        board_box.append(self.grid)

        # 创建棋盘格子
        self.cells = []
        for row in range(BOARD_ROWS):
            cell_row = []
            for col in range(BOARD_COLS):
                cell = Gtk.Button()
                cell.set_size_request(48, 48)
                cell.add_css_class("flat")
                self._set_cell_style(cell, row, col, False, False)
                cell.connect("clicked", self._on_cell_clicked, row, col)
                self.grid.attach(cell, col, row, 1, 1)
                cell_row.append(cell)
            self.cells.append(cell_row)

        # 被吃棋子显示（红方）
        self.captured_red_label = Gtk.Label(label="")
        self.captured_red_label.set_halign(Gtk.Align.CENTER)
        main_box.append(self.captured_red_label)

        # 提示
        hint_label = Gtk.Label(label=_("hint_xiangqi"))
        hint_label.add_css_class("dim-label")
        main_box.append(hint_label)

        return main_box

    def _set_cell_style(self, cell, row, col, is_selected, is_valid_move):
        """设置格子样式"""
        # 楚河汉界区域
        is_river = row in (4, 5)

        if is_selected:
            bg_color = "#7fc97f"  # 选中高亮
        elif is_valid_move:
            bg_color = "#ffeb3b"  # 可移动位置
        elif is_river:
            bg_color = "#e8d4a8"  # 河界颜色
        else:
            bg_color = "#f5deb3"  # 棋盘颜色

        css = f"""
            button {{
                background-color: {bg_color};
                border-radius: 0;
                font-size: 24px;
                font-weight: bold;
                min-width: 48px;
                min-height: 48px;
                border: 1px solid #8b7355;
            }}
            button:hover {{
                background-color: {bg_color};
                opacity: 0.9;
            }}
        """
        provider = Gtk.CssProvider()
        provider.load_from_string(css)
        cell.get_style_context().add_provider(
            provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _set_piece_style(self, cell, piece):
        """设置棋子文字样式"""
        if piece:
            color = "#c00000" if piece.color == 'red' else "#000000"
            cell.set_label(piece.char)
            # 更新文字颜色
            css = f"""
                button {{
                    color: {color};
                }}
            """
            provider = Gtk.CssProvider()
            provider.load_from_string(css)
            cell.get_style_context().add_provider(
                provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
            )
        else:
            cell.set_label("")

    def get_widget(self):
        return self.widget

    def new_game(self):
        """开始新游戏"""
        self.board = [[None] * BOARD_COLS for _ in range(BOARD_ROWS)]
        self.selected = None
        self.valid_moves = []
        self.current_player = 'red'
        self.game_over = False
        self.move_count = 0
        self.captured_red = []
        self.captured_black = []

        self._setup_board()
        self._update_display()

    def _setup_board(self):
        """初始化棋盘布局"""
        # 黑方（顶部，row 0-4）
        self.board[0][0] = Piece(PieceType.CHARIOT, 'black')
        self.board[0][1] = Piece(PieceType.HORSE, 'black')
        self.board[0][2] = Piece(PieceType.ELEPHANT, 'black')
        self.board[0][3] = Piece(PieceType.ADVISOR, 'black')
        self.board[0][4] = Piece(PieceType.GENERAL, 'black')
        self.board[0][5] = Piece(PieceType.ADVISOR, 'black')
        self.board[0][6] = Piece(PieceType.ELEPHANT, 'black')
        self.board[0][7] = Piece(PieceType.HORSE, 'black')
        self.board[0][8] = Piece(PieceType.CHARIOT, 'black')
        self.board[2][1] = Piece(PieceType.CANNON, 'black')
        self.board[2][7] = Piece(PieceType.CANNON, 'black')
        for col in [0, 2, 4, 6, 8]:
            self.board[3][col] = Piece(PieceType.SOLDIER, 'black')

        # 红方（底部，row 5-9）
        self.board[9][0] = Piece(PieceType.CHARIOT, 'red')
        self.board[9][1] = Piece(PieceType.HORSE, 'red')
        self.board[9][2] = Piece(PieceType.ELEPHANT, 'red')
        self.board[9][3] = Piece(PieceType.ADVISOR, 'red')
        self.board[9][4] = Piece(PieceType.GENERAL, 'red')
        self.board[9][5] = Piece(PieceType.ADVISOR, 'red')
        self.board[9][6] = Piece(PieceType.ELEPHANT, 'red')
        self.board[9][7] = Piece(PieceType.HORSE, 'red')
        self.board[9][8] = Piece(PieceType.CHARIOT, 'red')
        self.board[7][1] = Piece(PieceType.CANNON, 'red')
        self.board[7][7] = Piece(PieceType.CANNON, 'red')
        for col in [0, 2, 4, 6, 8]:
            self.board[6][col] = Piece(PieceType.SOLDIER, 'red')

    def _update_display(self):
        """更新显示"""
        # 更新状态标签
        if self.game_over:
            pass  # 状态在 _check_game_over 中设置
        elif ChineseChessRules.is_in_check(self.board, self.current_player):
            self.status_label.set_label(
                _("xiangqi_red_in_check") if self.current_player == 'red' else _("xiangqi_black_in_check")
            )
        else:
            self.status_label.set_label(
                _("xiangqi_red_turn") if self.current_player == 'red' else _("xiangqi_black_turn")
            )

        # 更新棋盘
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                cell = self.cells[row][col]
                piece = self.board[row][col]

                is_selected = self.selected == (row, col)
                is_valid = (row, col) in self.valid_moves

                self._set_cell_style(cell, row, col, is_selected, is_valid)
                self._set_piece_style(cell, piece)

        # 更新被吃棋子
        self.captured_red_label.set_label(
            ''.join(p.char for p in self.captured_red)
        )
        self.captured_black_label.set_label(
            ''.join(p.char for p in self.captured_black)
        )

    def _on_cell_clicked(self, button, row, col):
        """格子被点击"""
        if self.game_over:
            return

        piece = self.board[row][col]

        # 如果点击的是有效移动位置
        if (row, col) in self.valid_moves:
            self._make_move(self.selected[0], self.selected[1], row, col)
            self.selected = None
            self.valid_moves = []
            self._update_display()
            return

        # 如果点击自己的棋子
        if piece and piece.color == self.current_player:
            if self.selected == (row, col):
                # 取消选择
                self.selected = None
                self.valid_moves = []
            else:
                # 选择新棋子
                self.selected = (row, col)
                self.valid_moves = ChineseChessRules.get_valid_moves(self.board, row, col)
        else:
            # 点击空格或对方棋子，取消选择
            self.selected = None
            self.valid_moves = []

        self._update_display()

    def _make_move(self, from_row, from_col, to_row, to_col):
        """执行移动"""
        piece = self.board[from_row][from_col]
        captured = self.board[to_row][to_col]

        # 记录被吃的棋子
        if captured:
            if captured.color == 'red':
                self.captured_red.append(captured)
            else:
                self.captured_black.append(captured)

        # 执行移动
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None

        # 增加移动计数
        self.move_count += 1

        # 切换玩家
        self.current_player = 'black' if self.current_player == 'red' else 'red'

        # 检查游戏是否结束
        self._check_game_over()

    def _check_game_over(self):
        """检查游戏是否结束"""
        # 检查当前玩家是否还有合法移动
        if not ChineseChessRules.has_legal_moves(self.board, self.current_player):
            self.game_over = True
            winner = 'black' if self.current_player == 'red' else 'red'

            if ChineseChessRules.is_in_check(self.board, self.current_player):
                # 将死
                self.status_label.set_label(
                    _("xiangqi_red_wins") if winner == 'red' else _("xiangqi_black_wins")
                )
                self.score_manager.record_score("chinese_chess", self.move_count)
                self._show_game_over_dialog(
                    _("xiangqi_checkmate"),
                    _("xiangqi_red_wins") if winner == 'red' else _("xiangqi_black_wins")
                )
            else:
                # 困毙（无子可动但未被将军）
                self.status_label.set_label(_("xiangqi_stalemate"))
                self._show_game_over_dialog(_("game_over"), _("xiangqi_stalemate"))

    def _show_game_over_dialog(self, heading, body):
        """显示游戏结束对话框"""
        dialog = Adw.AlertDialog(
            heading=heading,
            body=body
        )
        dialog.add_response("ok", _("ok"))
        dialog.set_default_response("ok")
        dialog.present(self.widget.get_root())

    def stop(self):
        """停止游戏"""
        pass
