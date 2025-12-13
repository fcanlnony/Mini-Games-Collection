"""国际象棋UI模块"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib

import sys
import threading
sys.path.insert(0, str(__file__).rsplit('/', 3)[0])
from i18n import _

from .logic import ChessLogic, Player, GameState
from .ai import ChessAI


class GameMode:
    """游戏模式"""
    PVP = 'pvp'  # 双人对战
    PVE = 'pve'  # 人机对战


class ChessUI:
    """国际象棋UI类"""

    CELL_SIZE = 56  # 格子大小
    ANIMATION_STEPS = 10  # 动画步数
    ANIMATION_INTERVAL = 15  # 动画间隔(ms)

    def __init__(self, logic: ChessLogic, on_game_over=None):
        self.logic = logic
        self.on_game_over = on_game_over
        self.selected = None
        self.valid_moves = []
        self.mode = GameMode.PVP
        self.ai = ChessAI(difficulty=2)
        self.player_color = Player.WHITE  # 玩家颜色
        self.ai_thinking = False
        self.animating = False  # 动画进行中

        self.cells = []
        self.widget = self._create_widget()

    def _create_widget(self) -> Gtk.Widget:
        """创建游戏界面"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(16)
        main_box.set_margin_bottom(16)
        main_box.set_margin_start(16)
        main_box.set_margin_end(16)
        main_box.set_halign(Gtk.Align.CENTER)
        main_box.set_valign(Gtk.Align.CENTER)

        # 模式选择
        mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        mode_box.set_halign(Gtk.Align.CENTER)
        main_box.append(mode_box)

        self.pvp_btn = Gtk.ToggleButton(label=_("mode_pvp"))
        self.pvp_btn.set_active(True)
        self.pvp_btn.connect("toggled", self._on_mode_changed, GameMode.PVP)
        mode_box.append(self.pvp_btn)

        self.pve_btn = Gtk.ToggleButton(label=_("mode_pve"))
        self.pve_btn.connect("toggled", self._on_mode_changed, GameMode.PVE)
        mode_box.append(self.pve_btn)

        # 难度选择（仅PVE模式显示）
        self.difficulty_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.difficulty_box.set_halign(Gtk.Align.CENTER)
        self.difficulty_box.set_visible(False)
        main_box.append(self.difficulty_box)

        diff_label = Gtk.Label(label=_("difficulty") + ":")
        self.difficulty_box.append(diff_label)

        self.difficulty_combo = Gtk.ComboBoxText()
        self.difficulty_combo.append_text(_("easy"))
        self.difficulty_combo.append_text(_("medium"))
        self.difficulty_combo.append_text(_("hard"))
        self.difficulty_combo.set_active(1)
        self.difficulty_combo.connect("changed", self._on_difficulty_changed)
        self.difficulty_box.append(self.difficulty_combo)

        # 悔棋按钮
        self.undo_btn = Gtk.Button(label=_("undo"))
        self.undo_btn.connect("clicked", self._on_undo_clicked)
        self.undo_btn.set_sensitive(False)
        main_box.append(self.undo_btn)

        # 状态显示
        self.status_label = Gtk.Label(label=_("white_turn"))
        self.status_label.add_css_class("title-3")
        main_box.append(self.status_label)

        # 被吃棋子（黑）
        self.captured_black_label = Gtk.Label(label="")
        self.captured_black_label.set_halign(Gtk.Align.CENTER)
        main_box.append(self.captured_black_label)

        # 棋盘容器 - 使用 Overlay 实现动画层
        board_frame = Gtk.Frame()
        board_frame.add_css_class("card")
        main_box.append(board_frame)

        board_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        board_box.set_margin_top(8)
        board_box.set_margin_bottom(8)
        board_box.set_margin_start(8)
        board_box.set_margin_end(8)
        board_frame.set_child(board_box)

        # 使用 Overlay 叠加动画层
        self.overlay = Gtk.Overlay()
        board_box.append(self.overlay)

        # 棋盘网格
        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(0)
        self.grid.set_column_spacing(0)
        self.overlay.set_child(self.grid)

        # 动画层 - 使用 Fixed 布局
        self.animation_layer = Gtk.Fixed()
        self.animation_layer.set_can_target(False)  # 不接收输入事件
        self.overlay.add_overlay(self.animation_layer)

        for row in range(8):
            cell_row = []
            for col in range(8):
                cell = Gtk.Button()
                cell.set_size_request(self.CELL_SIZE, self.CELL_SIZE)
                cell.add_css_class("flat")
                cell.connect("clicked", self._on_cell_clicked, row, col)
                self.grid.attach(cell, col, row, 1, 1)
                cell_row.append(cell)
            self.cells.append(cell_row)

        # 被吃棋子（白）
        self.captured_white_label = Gtk.Label(label="")
        self.captured_white_label.set_halign(Gtk.Align.CENTER)
        main_box.append(self.captured_white_label)

        # 提示
        hint_label = Gtk.Label(label=_("hint_chess"))
        hint_label.add_css_class("dim-label")
        main_box.append(hint_label)

        return main_box

    def get_widget(self) -> Gtk.Widget:
        return self.widget

    def _on_mode_changed(self, button: Gtk.ToggleButton, mode: str):
        """模式切换"""
        if button.get_active():
            self.mode = mode
            if mode == GameMode.PVP:
                self.pve_btn.set_active(False)
                self.difficulty_box.set_visible(False)
            else:
                self.pvp_btn.set_active(False)
                self.difficulty_box.set_visible(True)
            self.reset()

    def _on_difficulty_changed(self, combo: Gtk.ComboBoxText):
        """难度切换"""
        self.ai.difficulty = combo.get_active() + 1
        self.reset()

    def _on_undo_clicked(self, button: Gtk.Button):
        """悔棋按钮点击"""
        if self.ai_thinking or self.logic.is_game_over() or self.animating:
            return

        # PVE模式下悔两步（玩家和AI各一步）
        if self.mode == GameMode.PVE:
            if self.logic.can_undo():
                self.logic.undo()
            if self.logic.can_undo():
                self.logic.undo()
        else:
            self.logic.undo()

        self.selected = None
        self.valid_moves = []
        self.update_display()

    def _set_cell_style(self, cell: Gtk.Button, row: int, col: int,
                        is_selected: bool, is_valid_move: bool, is_last_move: bool = False):
        """设置格子样式"""
        if is_selected:
            bg_color = "#7fc97f"
        elif is_valid_move:
            bg_color = "#ffeb3b"
        elif is_last_move:
            bg_color = "#aed581"  # 上一步移动的高亮
        elif (row + col) % 2 == 0:
            bg_color = "#f0d9b5"
        else:
            bg_color = "#b58863"

        css = f"""
            button {{
                background-color: {bg_color};
                border-radius: 0;
                font-size: 32px;
                min-width: {self.CELL_SIZE}px;
                min-height: {self.CELL_SIZE}px;
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

    def _animate_move(self, from_row: int, from_col: int, to_row: int, to_col: int,
                      piece_char: str, callback=None):
        """执行移动动画"""
        self.animating = True

        # 创建动画棋子
        anim_label = Gtk.Label(label=piece_char)
        anim_label.set_size_request(self.CELL_SIZE, self.CELL_SIZE)

        # 设置动画棋子样式
        css = f"""
            label {{
                font-size: 32px;
                font-weight: bold;
                background-color: rgba(255, 235, 59, 0.8);
                border-radius: 4px;
            }}
        """
        provider = Gtk.CssProvider()
        provider.load_from_string(css)
        anim_label.get_style_context().add_provider(
            provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # 计算起点和终点位置
        start_x = from_col * self.CELL_SIZE
        start_y = from_row * self.CELL_SIZE
        end_x = to_col * self.CELL_SIZE
        end_y = to_row * self.CELL_SIZE

        # 添加到动画层
        self.animation_layer.put(anim_label, start_x, start_y)

        # 隐藏起点的棋子
        self.cells[from_row][from_col].set_label("")

        # 动画状态
        step = [0]
        dx = (end_x - start_x) / self.ANIMATION_STEPS
        dy = (end_y - start_y) / self.ANIMATION_STEPS

        def animate_step():
            step[0] += 1
            if step[0] <= self.ANIMATION_STEPS:
                new_x = start_x + dx * step[0]
                new_y = start_y + dy * step[0]
                self.animation_layer.move(anim_label, new_x, new_y)
                return True
            else:
                # 动画结束，清理
                self.animation_layer.remove(anim_label)
                self.animating = False
                if callback:
                    callback()
                return False

        GLib.timeout_add(self.ANIMATION_INTERVAL, animate_step)

    def _on_cell_clicked(self, button: Gtk.Button, row: int, col: int):
        """格子点击"""
        if self.logic.is_game_over() or self.ai_thinking or self.animating:
            return

        # PVE模式下，非玩家回合不响应
        if self.mode == GameMode.PVE:
            if self.logic.current_player != self.player_color:
                return

        piece = self.logic.get_piece(row, col)

        # 点击有效移动位置
        if (row, col) in self.valid_moves:
            from_row, from_col = self.selected
            piece_at_from = self.logic.get_piece(from_row, from_col)
            piece_char = self.logic.get_piece_char(piece_at_from)

            # 执行逻辑移动
            self.logic.make_move(from_row, from_col, row, col)
            self.selected = None
            self.valid_moves = []

            # 播放动画
            def on_animation_done():
                self.update_display()
                if self.logic.is_game_over():
                    self._show_game_over()
                elif self.mode == GameMode.PVE:
                    self._ai_move()

            self._animate_move(from_row, from_col, row, col, piece_char, on_animation_done)
            return

        # 点击自己的棋子
        if piece and self.logic.is_own_piece(piece):
            if self.selected == (row, col):
                self.selected = None
                self.valid_moves = []
            else:
                self.selected = (row, col)
                self.valid_moves = self.logic.get_valid_moves(row, col)
        else:
            self.selected = None
            self.valid_moves = []

        self.update_display()

    def _ai_move(self):
        """AI执行移动"""
        self.ai_thinking = True
        self.status_label.set_label(_("ai_thinking"))
        self.undo_btn.set_sensitive(False)

        def do_ai_move():
            game_clone = self.logic.clone()
            move = self.ai.get_best_move(game_clone)
            GLib.idle_add(self._apply_ai_move, move)

        thread = threading.Thread(target=do_ai_move, daemon=True)
        thread.start()

    def _apply_ai_move(self, move):
        """应用AI移动"""
        self.ai_thinking = False
        if move:
            (from_pos, to_pos) = move
            from_row, from_col = from_pos
            to_row, to_col = to_pos

            piece = self.logic.get_piece(from_row, from_col)
            piece_char = self.logic.get_piece_char(piece)

            # 执行逻辑移动
            self.logic.make_move(from_row, from_col, to_row, to_col)

            # 播放动画
            def on_animation_done():
                self.update_display()
                if self.logic.is_game_over():
                    self._show_game_over()

            self._animate_move(from_row, from_col, to_row, to_col, piece_char, on_animation_done)
        else:
            self.update_display()
            if self.logic.is_game_over():
                self._show_game_over()

    def update_display(self):
        """更新显示"""
        # 更新悔棋按钮状态
        self.undo_btn.set_sensitive(
            self.logic.can_undo() and not self.ai_thinking and not self.animating
        )

        # 获取上一步移动位置
        last_from = None
        last_to = None
        if self.logic.last_move:
            _piece, last_from, last_to = self.logic.last_move

        # 状态
        if self.logic.is_game_over():
            pass
        elif self.logic.is_in_check(self.logic.current_player):
            label = (_("white_in_check") if self.logic.current_player == Player.WHITE
                     else _("black_in_check"))
            self.status_label.set_label(label)
        else:
            label = (_("white_turn") if self.logic.current_player == Player.WHITE
                     else _("black_turn"))
            self.status_label.set_label(label)

        # 棋盘
        for row in range(8):
            for col in range(8):
                cell = self.cells[row][col]
                piece = self.logic.get_piece(row, col)

                if piece:
                    cell.set_label(self.logic.get_piece_char(piece))
                else:
                    cell.set_label("")

                is_selected = self.selected == (row, col)
                is_valid = (row, col) in self.valid_moves
                is_last_move = (last_from == (row, col) or last_to == (row, col))
                self._set_cell_style(cell, row, col, is_selected, is_valid, is_last_move)

        # 被吃棋子
        self.captured_white_label.set_label(
            ''.join(self.logic.get_piece_char(p) for p in self.logic.captured_white)
        )
        self.captured_black_label.set_label(
            ''.join(self.logic.get_piece_char(p) for p in self.logic.captured_black)
        )

    def _show_game_over(self):
        """显示游戏结束"""
        winner = self.logic.get_winner()
        if winner:
            heading = _("checkmate")
            body = _("white_wins") if winner == Player.WHITE else _("black_wins")
        else:
            heading = _("game_over")
            body = _("stalemate")

        self.status_label.set_label(body)

        dialog = Adw.AlertDialog(heading=heading, body=body)
        dialog.add_response("ok", _("ok"))
        dialog.set_default_response("ok")
        dialog.present(self.widget.get_root())

        if self.on_game_over:
            self.on_game_over()

    def reset(self):
        """重置游戏"""
        self.logic.reset()
        self.selected = None
        self.valid_moves = []
        self.ai_thinking = False
        self.animating = False
        self.update_display()
