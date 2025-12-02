"""国际象棋游戏"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, Adw
import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])
from i18n import _


class Chess:
    """国际象棋游戏"""

    # 棋子 Unicode 字符
    PIECES = {
        'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',  # 白棋
        'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟',  # 黑棋
    }

    # 棋子名称
    PIECE_NAMES = {
        'K': 'king', 'Q': 'queen', 'R': 'rook', 'B': 'bishop', 'N': 'knight', 'P': 'pawn',
        'k': 'king', 'q': 'queen', 'r': 'rook', 'b': 'bishop', 'n': 'knight', 'p': 'pawn',
    }

    def __init__(self, score_manager):
        self.score_manager = score_manager
        self.board = [[None] * 8 for _ in range(8)]
        self.selected = None  # (row, col)
        self.valid_moves = []  # 当前选中棋子的有效移动
        self.current_player = 'white'  # 'white' 或 'black'
        self.game_over = False
        self.move_count = 0
        self.captured_white = []  # 被吃的白棋
        self.captured_black = []  # 被吃的黑棋
        self.last_move = None  # 用于吃过路兵
        self.can_castle = {
            'white': {'king_side': True, 'queen_side': True},
            'black': {'king_side': True, 'queen_side': True}
        }

        self.widget = self.create_widget()
        self.new_game()

    def create_widget(self):
        """创建游戏界面"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(16)
        main_box.set_margin_bottom(16)
        main_box.set_margin_start(16)
        main_box.set_margin_end(16)
        main_box.set_halign(Gtk.Align.CENTER)
        main_box.set_valign(Gtk.Align.CENTER)

        # 状态显示
        self.status_label = Gtk.Label(label=_("white_turn"))
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
        for row in range(8):
            cell_row = []
            for col in range(8):
                cell = Gtk.Button()
                cell.set_size_request(56, 56)
                cell.add_css_class("flat")

                # 设置棋盘颜色
                is_light = (row + col) % 2 == 0
                self.set_cell_style(cell, is_light, False, False)

                # 点击事件
                cell.connect("clicked", self.on_cell_clicked, row, col)

                self.grid.attach(cell, col, row, 1, 1)
                cell_row.append(cell)
            self.cells.append(cell_row)

        # 被吃棋子显示（白方）
        self.captured_white_label = Gtk.Label(label="")
        self.captured_white_label.set_halign(Gtk.Align.CENTER)
        main_box.append(self.captured_white_label)

        # 提示
        hint_label = Gtk.Label(label=_("hint_chess"))
        hint_label.add_css_class("dim-label")
        main_box.append(hint_label)

        return main_box

    def set_cell_style(self, cell, is_light, is_selected, is_valid_move):
        """设置格子样式"""
        if is_selected:
            bg_color = "#7fc97f"  # 选中格高亮绿色
        elif is_valid_move:
            bg_color = "#ffeb3b"  # 可移动位置黄色
        elif is_light:
            bg_color = "#f0d9b5"  # 浅色格
        else:
            bg_color = "#b58863"  # 深色格

        css = f"""
            button {{
                background-color: {bg_color};
                border-radius: 0;
                font-size: 32px;
                min-width: 56px;
                min-height: 56px;
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

    def get_widget(self):
        return self.widget

    def new_game(self):
        """开始新游戏"""
        self.board = [[None] * 8 for _ in range(8)]
        self.selected = None
        self.valid_moves = []
        self.current_player = 'white'
        self.game_over = False
        self.move_count = 0
        self.captured_white = []
        self.captured_black = []
        self.last_move = None
        self.can_castle = {
            'white': {'king_side': True, 'queen_side': True},
            'black': {'king_side': True, 'queen_side': True}
        }

        # 初始化棋盘
        # 黑棋（顶部）
        self.board[0] = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
        self.board[1] = ['p'] * 8

        # 白棋（底部）
        self.board[6] = ['P'] * 8
        self.board[7] = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']

        self.update_display()

    def update_display(self):
        """更新显示"""
        # 更新状态
        if self.game_over:
            pass  # 状态在 check_game_over 中设置
        elif self.is_in_check(self.current_player):
            self.status_label.set_label(
                _("white_in_check") if self.current_player == 'white' else _("black_in_check")
            )
        else:
            self.status_label.set_label(
                _("white_turn") if self.current_player == 'white' else _("black_turn")
            )

        # 更新棋盘
        for row in range(8):
            for col in range(8):
                cell = self.cells[row][col]
                piece = self.board[row][col]

                if piece:
                    cell.set_label(self.PIECES[piece])
                else:
                    cell.set_label("")

                is_light = (row + col) % 2 == 0
                is_selected = self.selected == (row, col)
                is_valid = (row, col) in self.valid_moves

                self.set_cell_style(cell, is_light, is_selected, is_valid)

        # 更新被吃棋子
        self.captured_white_label.set_label(
            ''.join(self.PIECES[p] for p in self.captured_white)
        )
        self.captured_black_label.set_label(
            ''.join(self.PIECES[p] for p in self.captured_black)
        )

    def on_cell_clicked(self, button, row, col):
        """格子被点击"""
        if self.game_over:
            return

        piece = self.board[row][col]

        # 如果点击的是有效移动位置
        if (row, col) in self.valid_moves:
            self.make_move(self.selected[0], self.selected[1], row, col)
            self.selected = None
            self.valid_moves = []
            self.update_display()
            return

        # 如果点击自己的棋子
        if piece and self.is_own_piece(piece):
            if self.selected == (row, col):
                # 取消选择
                self.selected = None
                self.valid_moves = []
            else:
                # 选择新棋子
                self.selected = (row, col)
                self.valid_moves = self.get_valid_moves(row, col)
        else:
            # 点击空格或对方棋子，取消选择
            self.selected = None
            self.valid_moves = []

        self.update_display()

    def is_own_piece(self, piece):
        """判断是否是当前玩家的棋子"""
        if self.current_player == 'white':
            return piece.isupper()
        return piece.islower()

    def is_enemy_piece(self, piece):
        """判断是否是对方的棋子"""
        if self.current_player == 'white':
            return piece.islower()
        return piece.isupper()

    def get_valid_moves(self, row, col):
        """获取棋子的有效移动"""
        piece = self.board[row][col]
        if not piece:
            return []

        piece_type = piece.upper()
        moves = []

        if piece_type == 'P':
            moves = self.get_pawn_moves(row, col, piece.isupper())
        elif piece_type == 'R':
            moves = self.get_rook_moves(row, col)
        elif piece_type == 'N':
            moves = self.get_knight_moves(row, col)
        elif piece_type == 'B':
            moves = self.get_bishop_moves(row, col)
        elif piece_type == 'Q':
            moves = self.get_queen_moves(row, col)
        elif piece_type == 'K':
            moves = self.get_king_moves(row, col)

        # 过滤掉会导致自己被将军的移动
        valid_moves = []
        for move in moves:
            if not self.would_be_in_check(row, col, move[0], move[1]):
                valid_moves.append(move)

        return valid_moves

    def get_pawn_moves(self, row, col, is_white):
        """获取兵的移动"""
        moves = []
        direction = -1 if is_white else 1
        start_row = 6 if is_white else 1

        # 前进一格
        new_row = row + direction
        if 0 <= new_row < 8 and self.board[new_row][col] is None:
            moves.append((new_row, col))

            # 初始位置可以前进两格
            if row == start_row:
                new_row2 = row + 2 * direction
                if self.board[new_row2][col] is None:
                    moves.append((new_row2, col))

        # 斜向吃子
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

    def get_rook_moves(self, row, col):
        """获取车的移动"""
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for dr, dc in directions:
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

    def get_knight_moves(self, row, col):
        """获取马的移动"""
        moves = []
        offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]

        for dr, dc in offsets:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.board[new_row][new_col]
                if target is None or self.is_enemy_piece(target):
                    moves.append((new_row, new_col))

        return moves

    def get_bishop_moves(self, row, col):
        """获取象的移动"""
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        for dr, dc in directions:
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

    def get_queen_moves(self, row, col):
        """获取皇后的移动"""
        return self.get_rook_moves(row, col) + self.get_bishop_moves(row, col)

    def get_king_moves(self, row, col):
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
        player = self.current_player
        if not self.is_in_check(player):
            # 王翼易位
            if self.can_castle[player]['king_side']:
                if (self.board[row][5] is None and
                    self.board[row][6] is None and
                    not self.would_be_in_check(row, col, row, 5) and
                    not self.would_be_in_check(row, col, row, 6)):
                    moves.append((row, 6))

            # 后翼易位
            if self.can_castle[player]['queen_side']:
                if (self.board[row][1] is None and
                    self.board[row][2] is None and
                    self.board[row][3] is None and
                    not self.would_be_in_check(row, col, row, 3) and
                    not self.would_be_in_check(row, col, row, 2)):
                    moves.append((row, 2))

        return moves

    def would_be_in_check(self, from_row, from_col, to_row, to_col):
        """检查移动后是否会被将军"""
        # 临时执行移动
        piece = self.board[from_row][from_col]
        captured = self.board[to_row][to_col]
        self.board[from_row][from_col] = None
        self.board[to_row][to_col] = piece

        # 检查是否被将军
        in_check = self.is_in_check(self.current_player)

        # 恢复棋盘
        self.board[from_row][from_col] = piece
        self.board[to_row][to_col] = captured

        return in_check

    def is_in_check(self, player):
        """检查玩家是否被将军"""
        # 找到国王位置
        king = 'K' if player == 'white' else 'k'
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

        # 检查是否有敌方棋子可以攻击国王
        return self.is_under_attack(king_pos[0], king_pos[1], player)

    def is_under_attack(self, row, col, player):
        """检查位置是否被攻击"""
        enemy_player = 'black' if player == 'white' else 'white'
        original_player = self.current_player
        self.current_player = enemy_player

        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and self.is_own_piece(piece):
                    # 获取该棋子的基本移动（不检查将军）
                    piece_type = piece.upper()
                    moves = []
                    if piece_type == 'P':
                        # 兵的攻击是斜向的
                        direction = -1 if piece.isupper() else 1
                        for dc in [-1, 1]:
                            nr, nc = r + direction, c + dc
                            if 0 <= nr < 8 and 0 <= nc < 8:
                                moves.append((nr, nc))
                    elif piece_type == 'R':
                        moves = self.get_rook_moves(r, c)
                    elif piece_type == 'N':
                        moves = self.get_knight_moves(r, c)
                    elif piece_type == 'B':
                        moves = self.get_bishop_moves(r, c)
                    elif piece_type == 'Q':
                        moves = self.get_queen_moves(r, c)
                    elif piece_type == 'K':
                        # 国王的基本移动
                        for dr in [-1, 0, 1]:
                            for dc in [-1, 0, 1]:
                                if dr == 0 and dc == 0:
                                    continue
                                nr, nc = r + dr, c + dc
                                if 0 <= nr < 8 and 0 <= nc < 8:
                                    moves.append((nr, nc))

                    if (row, col) in moves:
                        self.current_player = original_player
                        return True

        self.current_player = original_player
        return False

    def make_move(self, from_row, from_col, to_row, to_col):
        """执行移动"""
        piece = self.board[from_row][from_col]
        captured = self.board[to_row][to_col]

        # 记录被吃的棋子
        if captured:
            if captured.isupper():
                self.captured_white.append(captured)
            else:
                self.captured_black.append(captured)

        # 吃过路兵
        if piece.upper() == 'P' and captured is None and from_col != to_col:
            # 这是斜向移动但目标是空的，说明是吃过路兵
            en_passant_row = from_row
            captured_pawn = self.board[en_passant_row][to_col]
            if captured_pawn:
                if captured_pawn.isupper():
                    self.captured_white.append(captured_pawn)
                else:
                    self.captured_black.append(captured_pawn)
                self.board[en_passant_row][to_col] = None

        # 王车易位
        if piece.upper() == 'K' and abs(to_col - from_col) == 2:
            if to_col == 6:  # 王翼
                self.board[to_row][5] = self.board[to_row][7]
                self.board[to_row][7] = None
            elif to_col == 2:  # 后翼
                self.board[to_row][3] = self.board[to_row][0]
                self.board[to_row][0] = None

        # 执行移动
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None

        # 兵升变
        if piece.upper() == 'P':
            if (piece.isupper() and to_row == 0) or (piece.islower() and to_row == 7):
                # 默认升变为皇后
                self.board[to_row][to_col] = 'Q' if piece.isupper() else 'q'

        # 更新易位权限
        player = self.current_player
        if piece.upper() == 'K':
            self.can_castle[player]['king_side'] = False
            self.can_castle[player]['queen_side'] = False
        elif piece.upper() == 'R':
            if from_col == 0:
                self.can_castle[player]['queen_side'] = False
            elif from_col == 7:
                self.can_castle[player]['king_side'] = False

        # 记录最后移动（用于吃过路兵）
        self.last_move = (piece, (from_row, from_col), (to_row, to_col))

        # 增加移动计数
        self.move_count += 1

        # 切换玩家
        self.current_player = 'black' if self.current_player == 'white' else 'white'

        # 检查游戏是否结束
        self.check_game_over()

    def check_game_over(self):
        """检查游戏是否结束"""
        # 检查当前玩家是否有合法移动
        has_legal_moves = False
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and self.is_own_piece(piece):
                    moves = self.get_valid_moves(row, col)
                    if moves:
                        has_legal_moves = True
                        break
            if has_legal_moves:
                break

        if not has_legal_moves:
            self.game_over = True
            if self.is_in_check(self.current_player):
                # 将死
                winner = 'black' if self.current_player == 'white' else 'white'
                self.status_label.set_label(
                    _("white_wins") if winner == 'white' else _("black_wins")
                )
                self.score_manager.record_score("chess", self.move_count)
                self.show_game_over_dialog(
                    _("checkmate"),
                    _("white_wins") if winner == 'white' else _("black_wins")
                )
            else:
                # 和棋（逼和）
                self.status_label.set_label(_("stalemate"))
                self.show_game_over_dialog(_("game_over"), _("stalemate"))

    def show_game_over_dialog(self, heading, body):
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
