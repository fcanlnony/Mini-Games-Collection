"""2048 游戏"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, GLib, Adw
import random
import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])
from i18n import _


class Game2048:
    COLORS = {
        0: "#cdc1b4",
        2: "#eee4da",
        4: "#ede0c8",
        8: "#f2b179",
        16: "#f59563",
        32: "#f67c5f",
        64: "#f65e3b",
        128: "#edcf72",
        256: "#edcc61",
        512: "#edc850",
        1024: "#edc53f",
        2048: "#edc22e",
    }

    TEXT_COLORS = {
        0: "#cdc1b4",
        2: "#776e65",
        4: "#776e65",
        8: "#f9f6f2",
        16: "#f9f6f2",
        32: "#f9f6f2",
        64: "#f9f6f2",
        128: "#f9f6f2",
        256: "#f9f6f2",
        512: "#f9f6f2",
        1024: "#f9f6f2",
        2048: "#f9f6f2",
    }

    def __init__(self, score_manager):
        self.score_manager = score_manager
        self.grid_size = 4
        self.grid = [[0] * self.grid_size for _ in range(self.grid_size)]
        self.score = 0
        self.game_over = False

        self.widget = self.create_widget()
        self.new_game()

    def create_widget(self):
        """创建游戏界面"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        main_box.set_margin_top(16)
        main_box.set_margin_bottom(16)
        main_box.set_margin_start(16)
        main_box.set_margin_end(16)
        main_box.set_halign(Gtk.Align.CENTER)
        main_box.set_valign(Gtk.Align.CENTER)

        # 分数显示
        self.score_label = Gtk.Label(label=f"{_('score')}: 0")
        self.score_label.add_css_class("title-2")
        main_box.append(self.score_label)

        # 游戏网格容器
        grid_frame = Gtk.Frame()
        grid_frame.add_css_class("card")
        main_box.append(grid_frame)

        self.grid_widget = Gtk.Grid()
        self.grid_widget.set_row_spacing(8)
        self.grid_widget.set_column_spacing(8)
        self.grid_widget.set_margin_top(16)
        self.grid_widget.set_margin_bottom(16)
        self.grid_widget.set_margin_start(16)
        self.grid_widget.set_margin_end(16)
        grid_frame.set_child(self.grid_widget)

        # 创建格子
        self.cells = []
        for i in range(self.grid_size):
            row = []
            for j in range(self.grid_size):
                cell = Gtk.Label(label="")
                cell.set_size_request(80, 80)
                cell.add_css_class("title-1")
                self.grid_widget.attach(cell, j, i, 1, 1)
                row.append(cell)
            self.cells.append(row)

        # 键盘事件控制器
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self.on_key_pressed)
        main_box.add_controller(key_controller)

        # 设置可获取焦点
        main_box.set_focusable(True)

        # 手势支持
        gesture = Gtk.GestureSwipe()
        gesture.connect("swipe", self.on_swipe)
        main_box.add_controller(gesture)

        # 提示标签
        hint_label = Gtk.Label(label=_("hint_2048"))
        hint_label.add_css_class("dim-label")
        main_box.append(hint_label)

        # 页面显示时自动获取焦点
        main_box.connect("map", lambda w: w.grab_focus())

        return main_box

    def get_widget(self):
        return self.widget

    def new_game(self):
        """开始新游戏"""
        self.grid = [[0] * self.grid_size for _ in range(self.grid_size)]
        self.score = 0
        self.game_over = False
        self.add_random_tile()
        self.add_random_tile()
        self.update_display()
        self.widget.grab_focus()

    def add_random_tile(self):
        """添加随机方块"""
        empty_cells = []
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i][j] == 0:
                    empty_cells.append((i, j))

        if empty_cells:
            i, j = random.choice(empty_cells)
            self.grid[i][j] = 4 if random.random() < 0.1 else 2

    def update_display(self):
        """更新显示"""
        self.score_label.set_label(f"{_('score')}: {self.score}")

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                value = self.grid[i][j]
                cell = self.cells[i][j]

                if value == 0:
                    cell.set_label("")
                else:
                    cell.set_label(str(value))

                # 设置颜色
                bg_color = self.COLORS.get(value, "#3c3a32")
                text_color = self.TEXT_COLORS.get(value, "#f9f6f2")

                css = f"""
                    label {{
                        background-color: {bg_color};
                        color: {text_color};
                        border-radius: 8px;
                        font-weight: bold;
                    }}
                """
                provider = Gtk.CssProvider()
                provider.load_from_string(css)
                cell.get_style_context().add_provider(
                    provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )

    def on_key_pressed(self, controller, keyval, keycode, state):
        """键盘按键处理"""
        if self.game_over:
            return False

        moved = False
        if keyval in (Gdk.KEY_w, Gdk.KEY_W, Gdk.KEY_Up):
            moved = self.move_up()
        elif keyval in (Gdk.KEY_s, Gdk.KEY_S, Gdk.KEY_Down):
            moved = self.move_down()
        elif keyval in (Gdk.KEY_a, Gdk.KEY_A, Gdk.KEY_Left):
            moved = self.move_left()
        elif keyval in (Gdk.KEY_d, Gdk.KEY_D, Gdk.KEY_Right):
            moved = self.move_right()

        if moved:
            self.add_random_tile()
            self.update_display()
            self.check_game_over()

        return True

    def on_swipe(self, gesture, vx, vy):
        """滑动手势处理"""
        if self.game_over:
            return

        moved = False
        if abs(vx) > abs(vy):
            if vx > 0:
                moved = self.move_right()
            else:
                moved = self.move_left()
        else:
            if vy > 0:
                moved = self.move_down()
            else:
                moved = self.move_up()

        if moved:
            self.add_random_tile()
            self.update_display()
            self.check_game_over()

    def compress(self, row):
        """压缩行（移除零）"""
        new_row = [x for x in row if x != 0]
        new_row.extend([0] * (self.grid_size - len(new_row)))
        return new_row

    def merge(self, row):
        """合并相邻相同的方块"""
        for i in range(self.grid_size - 1):
            if row[i] != 0 and row[i] == row[i + 1]:
                row[i] *= 2
                self.score += row[i]
                row[i + 1] = 0
        return row

    def move_left(self):
        """向左移动"""
        old_grid = [row[:] for row in self.grid]
        for i in range(self.grid_size):
            self.grid[i] = self.compress(self.grid[i])
            self.grid[i] = self.merge(self.grid[i])
            self.grid[i] = self.compress(self.grid[i])
        return old_grid != self.grid

    def move_right(self):
        """向右移动"""
        old_grid = [row[:] for row in self.grid]
        for i in range(self.grid_size):
            self.grid[i] = self.grid[i][::-1]
            self.grid[i] = self.compress(self.grid[i])
            self.grid[i] = self.merge(self.grid[i])
            self.grid[i] = self.compress(self.grid[i])
            self.grid[i] = self.grid[i][::-1]
        return old_grid != self.grid

    def move_up(self):
        """向上移动"""
        old_grid = [row[:] for row in self.grid]
        self.transpose()
        for i in range(self.grid_size):
            self.grid[i] = self.compress(self.grid[i])
            self.grid[i] = self.merge(self.grid[i])
            self.grid[i] = self.compress(self.grid[i])
        self.transpose()
        return old_grid != self.grid

    def move_down(self):
        """向下移动"""
        old_grid = [row[:] for row in self.grid]
        self.transpose()
        for i in range(self.grid_size):
            self.grid[i] = self.grid[i][::-1]
            self.grid[i] = self.compress(self.grid[i])
            self.grid[i] = self.merge(self.grid[i])
            self.grid[i] = self.compress(self.grid[i])
            self.grid[i] = self.grid[i][::-1]
        self.transpose()
        return old_grid != self.grid

    def transpose(self):
        """转置网格"""
        self.grid = [list(row) for row in zip(*self.grid)]

    def check_game_over(self):
        """检查游戏是否结束"""
        # 检查是否有空格
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i][j] == 0:
                    return

        # 检查是否有可合并的方块
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if j < self.grid_size - 1 and self.grid[i][j] == self.grid[i][j + 1]:
                    return
                if i < self.grid_size - 1 and self.grid[i][j] == self.grid[i + 1][j]:
                    return

        # 游戏结束
        self.game_over = True
        self.score_manager.record_score("2048", self.score)
        self.show_game_over()

    def show_game_over(self):
        """显示游戏结束对话框"""
        dialog = Adw.AlertDialog(
            heading=_("game_over"),
            body=_("your_score", score=self.score)
        )
        dialog.add_response("ok", _("ok"))
        dialog.set_default_response("ok")
        dialog.present(self.widget.get_root())

    def stop(self):
        """停止游戏"""
        if self.score > 0:
            self.score_manager.record_score("2048", self.score)
