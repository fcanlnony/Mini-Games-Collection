"""三子棋游戏UI模块"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib

import sys
sys.path.insert(0, str(__file__).rsplit('/', 3)[0])
from i18n import _

from .logic import TicTacToeLogic, Player, GameState
from .ai import TicTacToeAI


class GameMode:
    PVP = 'pvp'
    PVE = 'pve'


class TicTacToeUI:
    """三子棋游戏UI类"""

    def __init__(self, logic: TicTacToeLogic, on_game_over=None):
        self.logic = logic
        self.on_game_over = on_game_over
        self.mode = GameMode.PVP
        self.ai = TicTacToeAI(difficulty=2)
        self.player_symbol = Player.X
        self.ai_thinking = False

        self.buttons: list[list[Gtk.Button]] = []
        self.widget = self._create_widget()

    def _create_widget(self) -> Gtk.Widget:
        """创建游戏界面"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
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

        # 难度选择
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

        # 状态标签
        self.status_label = Gtk.Label(label=_("ttt_x_turn"))
        self.status_label.add_css_class("title-2")
        main_box.append(self.status_label)

        # 游戏网格
        grid_frame = Gtk.Frame()
        grid_frame.add_css_class("card")
        main_box.append(grid_frame)

        grid = Gtk.Grid()
        grid.set_row_spacing(4)
        grid.set_column_spacing(4)
        grid.set_margin_top(16)
        grid.set_margin_bottom(16)
        grid.set_margin_start(16)
        grid.set_margin_end(16)
        grid_frame.set_child(grid)

        for row in range(3):
            row_buttons = []
            for col in range(3):
                button = Gtk.Button(label="")
                button.set_size_request(80, 80)
                button.add_css_class("flat")
                button.connect("clicked", self._on_button_clicked, row, col)
                self._apply_button_style(button, Player.NONE, False)
                grid.attach(button, col, row, 1, 1)
                row_buttons.append(button)
            self.buttons.append(row_buttons)

        # 提示
        hint_label = Gtk.Label(label=_("hint_ttt"))
        hint_label.add_css_class("dim-label")
        main_box.append(hint_label)

        return main_box

    def get_widget(self) -> Gtk.Widget:
        return self.widget

    def _on_mode_changed(self, button: Gtk.ToggleButton, mode: str):
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
        self.ai.difficulty = combo.get_active() + 1
        self.reset()

    def _on_undo_clicked(self, button: Gtk.Button):
        """悔棋按钮点击"""
        if self.ai_thinking or self.logic.is_game_over():
            return

        # PVE模式下悔两步（玩家和AI各一步）
        if self.mode == GameMode.PVE:
            if self.logic.can_undo():
                self.logic.undo()
            if self.logic.can_undo():
                self.logic.undo()
        else:
            self.logic.undo()

        self._update_display()

    def _on_button_clicked(self, button: Gtk.Button, row: int, col: int):
        if self.logic.is_game_over() or self.ai_thinking:
            return

        # PVE模式下，非玩家回合不响应
        if self.mode == GameMode.PVE:
            if self.logic.current_player != self.player_symbol:
                return

        if self.logic.make_move(row, col):
            self._update_display()

            if self.logic.is_game_over():
                self._show_game_over()
            elif self.mode == GameMode.PVE:
                self._ai_move()

    def _ai_move(self):
        """AI执行移动"""
        self.ai_thinking = True
        self.status_label.set_label(_("ai_thinking"))

        def do_ai_move():
            move = self.ai.get_best_move(self.logic)
            GLib.idle_add(self._apply_ai_move, move)
            return False

        GLib.timeout_add(300, do_ai_move)

    def _apply_ai_move(self, move):
        self.ai_thinking = False
        if move:
            self.logic.make_move(move[0], move[1])
        self._update_display()

        if self.logic.is_game_over():
            self._show_game_over()

    def _update_display(self):
        """更新显示"""
        # 更新悔棋按钮状态
        self.undo_btn.set_sensitive(self.logic.can_undo() and not self.ai_thinking)

        winning_cells = set()
        if self.logic.winning_line:
            winning_cells = set(self.logic.winning_line)

        for row in range(3):
            for col in range(3):
                player = self.logic.get_cell(row, col)
                button = self.buttons[row][col]
                is_winning = (row, col) in winning_cells
                self._update_button(button, player, is_winning)

        self._update_status()

    def _update_button(self, button: Gtk.Button, player: Player, is_winning: bool):
        if player == Player.X:
            button.set_label("X")
        elif player == Player.O:
            button.set_label("O")
        else:
            button.set_label("")

        self._apply_button_style(button, player, is_winning)

    def _apply_button_style(self, button: Gtk.Button, player: Player, is_winning: bool):
        if player == Player.X:
            text_color = "#e74c3c"
        elif player == Player.O:
            text_color = "#3498db"
        else:
            text_color = "#888888"

        bg_color = "#a8e6cf" if is_winning else "#f5f5f5"

        css = f"""
            button {{
                background-color: {bg_color};
                color: {text_color};
                font-size: 32px;
                font-weight: bold;
                border-radius: 8px;
            }}
        """
        provider = Gtk.CssProvider()
        provider.load_from_string(css)
        button.get_style_context().add_provider(
            provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _update_status(self):
        state = self.logic.state
        if state == GameState.PLAYING:
            if self.logic.current_player == Player.X:
                self.status_label.set_label(_("ttt_x_turn"))
            else:
                self.status_label.set_label(_("ttt_o_turn"))
        elif state == GameState.X_WINS:
            self.status_label.set_label(_("ttt_x_wins"))
        elif state == GameState.O_WINS:
            self.status_label.set_label(_("ttt_o_wins"))
        elif state == GameState.DRAW:
            self.status_label.set_label(_("ttt_draw"))

    def _show_game_over(self):
        state = self.logic.state

        if state == GameState.X_WINS:
            heading = _("ttt_x_wins")
            body = _("ttt_x_wins_msg")
        elif state == GameState.O_WINS:
            heading = _("ttt_o_wins")
            body = _("ttt_o_wins_msg")
        else:
            heading = _("ttt_draw")
            body = _("ttt_draw_msg")

        dialog = Adw.AlertDialog(heading=heading, body=body)
        dialog.add_response("ok", _("ok"))
        dialog.set_default_response("ok")
        dialog.present(self.widget.get_root())

        if self.on_game_over:
            self.on_game_over()

    def reset(self):
        self.logic.reset()
        self.ai_thinking = False

        for row in range(3):
            for col in range(3):
                button = self.buttons[row][col]
                button.set_label("")
                self._apply_button_style(button, Player.NONE, False)

        self._update_status()
