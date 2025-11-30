"""俄罗斯方块游戏"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, GLib, Adw
import random
import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])
from i18n import _


class Tetris:
    # 方块形状
    SHAPES = {
        'I': [[1, 1, 1, 1]],
        'O': [[1, 1], [1, 1]],
        'T': [[0, 1, 0], [1, 1, 1]],
        'S': [[0, 1, 1], [1, 1, 0]],
        'Z': [[1, 1, 0], [0, 1, 1]],
        'J': [[1, 0, 0], [1, 1, 1]],
        'L': [[0, 0, 1], [1, 1, 1]]
    }

    COLORS = {
        'I': '#00f0f0',
        'O': '#f0f000',
        'T': '#a000f0',
        'S': '#00f000',
        'Z': '#f00000',
        'J': '#0000f0',
        'L': '#f0a000'
    }

    def __init__(self, score_manager):
        self.score_manager = score_manager
        self.cols = 10
        self.rows = 20
        self.cell_size = 24

        self.board = []
        self.board_colors = []
        self.current_piece = None
        self.current_shape = None
        self.current_x = 0
        self.current_y = 0
        self.score = 0
        self.level = 1
        self.lines = 0
        self.game_over = False
        self.paused = False
        self.timer_id = None

        self.widget = self.create_widget()
        self.new_game()

    def create_widget(self):
        """创建游戏界面"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=24)
        main_box.set_margin_top(16)
        main_box.set_margin_bottom(16)
        main_box.set_margin_start(16)
        main_box.set_margin_end(16)
        main_box.set_halign(Gtk.Align.CENTER)
        main_box.set_valign(Gtk.Align.CENTER)

        # 游戏区域
        game_frame = Gtk.Frame()
        game_frame.add_css_class("card")
        main_box.append(game_frame)

        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_size_request(
            self.cols * self.cell_size + 2,
            self.rows * self.cell_size + 2
        )
        self.drawing_area.set_draw_func(self.draw)
        game_frame.set_child(self.drawing_area)

        # 信息面板
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        info_box.set_valign(Gtk.Align.START)
        main_box.append(info_box)

        # 分数
        self.score_label = Gtk.Label(label=f"{_('score')}: 0")
        self.score_label.add_css_class("title-3")
        self.score_label.set_halign(Gtk.Align.START)
        info_box.append(self.score_label)

        # 等级
        self.level_label = Gtk.Label(label=f"{_('level')}: 1")
        self.level_label.add_css_class("title-4")
        self.level_label.set_halign(Gtk.Align.START)
        info_box.append(self.level_label)

        # 行数
        self.lines_label = Gtk.Label(label=f"{_('lines')}: 0")
        self.lines_label.add_css_class("title-4")
        self.lines_label.set_halign(Gtk.Align.START)
        info_box.append(self.lines_label)

        # 下一个方块预览
        next_label = Gtk.Label(label=f"{_('next')}:")
        next_label.set_halign(Gtk.Align.START)
        info_box.append(next_label)

        self.next_area = Gtk.DrawingArea()
        self.next_area.set_size_request(100, 80)
        self.next_area.set_draw_func(self.draw_next)
        info_box.append(self.next_area)

        # 控制说明
        controls_label = Gtk.Label(label=_("hint_tetris"))
        controls_label.add_css_class("dim-label")
        controls_label.set_halign(Gtk.Align.START)
        info_box.append(controls_label)

        # 键盘事件
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self.on_key_pressed)
        main_box.add_controller(key_controller)
        main_box.set_focusable(True)

        # 页面显示时自动获取焦点
        main_box.connect("map", lambda w: w.grab_focus())

        return main_box

    def get_widget(self):
        return self.widget

    def new_game(self):
        """开始新游戏"""
        self.board = [[0] * self.cols for _ in range(self.rows)]
        self.board_colors = [[None] * self.cols for _ in range(self.rows)]
        self.score = 0
        self.level = 1
        self.lines = 0
        self.game_over = False
        self.paused = False

        self.next_piece = random.choice(list(self.SHAPES.keys()))
        self.spawn_piece()
        self.start_timer()
        self.update_display()
        self.widget.grab_focus()

    def spawn_piece(self):
        """生成新方块"""
        self.current_piece = self.next_piece
        self.next_piece = random.choice(list(self.SHAPES.keys()))
        self.current_shape = [row[:] for row in self.SHAPES[self.current_piece]]
        self.current_x = self.cols // 2 - len(self.current_shape[0]) // 2
        self.current_y = 0

        if not self.is_valid_position():
            self.game_over = True
            self.stop_timer()
            self.score_manager.record_score("tetris", self.score)
            self.show_game_over()

        self.next_area.queue_draw()

    def is_valid_position(self, shape=None, x=None, y=None):
        """检查位置是否有效"""
        if shape is None:
            shape = self.current_shape
        if x is None:
            x = self.current_x
        if y is None:
            y = self.current_y

        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    new_x = x + j
                    new_y = y + i
                    if new_x < 0 or new_x >= self.cols:
                        return False
                    if new_y >= self.rows:
                        return False
                    if new_y >= 0 and self.board[new_y][new_x]:
                        return False
        return True

    def rotate(self):
        """旋转方块"""
        rotated = list(zip(*self.current_shape[::-1]))
        rotated = [list(row) for row in rotated]
        if self.is_valid_position(rotated):
            self.current_shape = rotated
            self.drawing_area.queue_draw()

    def move(self, dx, dy):
        """移动方块"""
        if self.is_valid_position(x=self.current_x + dx, y=self.current_y + dy):
            self.current_x += dx
            self.current_y += dy
            self.drawing_area.queue_draw()
            return True
        return False

    def drop(self):
        """方块下落一格"""
        if not self.move(0, 1):
            self.lock_piece()
            self.clear_lines()
            self.spawn_piece()

    def hard_drop(self):
        """直接落到底部"""
        while self.move(0, 1):
            self.score += 2
        self.lock_piece()
        self.clear_lines()
        self.spawn_piece()
        self.update_display()

    def lock_piece(self):
        """锁定方块"""
        for i, row in enumerate(self.current_shape):
            for j, cell in enumerate(row):
                if cell:
                    y = self.current_y + i
                    x = self.current_x + j
                    if 0 <= y < self.rows and 0 <= x < self.cols:
                        self.board[y][x] = 1
                        self.board_colors[y][x] = self.COLORS[self.current_piece]

    def clear_lines(self):
        """消除完整的行"""
        lines_cleared = 0
        y = self.rows - 1
        while y >= 0:
            if all(self.board[y]):
                lines_cleared += 1
                del self.board[y]
                del self.board_colors[y]
                self.board.insert(0, [0] * self.cols)
                self.board_colors.insert(0, [None] * self.cols)
            else:
                y -= 1

        if lines_cleared:
            self.lines += lines_cleared
            # 计分
            scores = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += scores.get(lines_cleared, 0) * self.level

            # 升级
            self.level = self.lines // 10 + 1
            self.update_display()

        self.drawing_area.queue_draw()

    def update_display(self):
        """更新显示"""
        self.score_label.set_label(f"{_('score')}: {self.score}")
        self.level_label.set_label(f"{_('level')}: {self.level}")
        self.lines_label.set_label(f"{_('lines')}: {self.lines}")

    def draw(self, area, cr, width, height):
        """绘制游戏区域"""
        # 背景
        cr.set_source_rgb(0.1, 0.1, 0.1)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        # 网格线
        cr.set_source_rgb(0.2, 0.2, 0.2)
        for i in range(self.rows + 1):
            cr.move_to(0, i * self.cell_size)
            cr.line_to(self.cols * self.cell_size, i * self.cell_size)
        for j in range(self.cols + 1):
            cr.move_to(j * self.cell_size, 0)
            cr.line_to(j * self.cell_size, self.rows * self.cell_size)
        cr.stroke()

        # 已锁定的方块
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j]:
                    self.draw_cell(cr, j, i, self.board_colors[i][j])

        # 当前方块
        if self.current_shape and not self.game_over:
            color = self.COLORS[self.current_piece]
            for i, row in enumerate(self.current_shape):
                for j, cell in enumerate(row):
                    if cell:
                        self.draw_cell(cr, self.current_x + j, self.current_y + i, color)

    def draw_cell(self, cr, x, y, color):
        """绘制单个格子"""
        if y < 0:
            return

        # 解析颜色
        r = int(color[1:3], 16) / 255
        g = int(color[3:5], 16) / 255
        b = int(color[5:7], 16) / 255

        px = x * self.cell_size + 1
        py = y * self.cell_size + 1
        size = self.cell_size - 2

        # 填充
        cr.set_source_rgb(r, g, b)
        cr.rectangle(px, py, size, size)
        cr.fill()

        # 高光
        cr.set_source_rgba(1, 1, 1, 0.3)
        cr.rectangle(px, py, size, 3)
        cr.fill()
        cr.rectangle(px, py, 3, size)
        cr.fill()

    def draw_next(self, area, cr, width, height):
        """绘制下一个方块预览"""
        cr.set_source_rgb(0.15, 0.15, 0.15)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        if self.next_piece:
            shape = self.SHAPES[self.next_piece]
            color = self.COLORS[self.next_piece]
            offset_x = (width - len(shape[0]) * 20) // 2
            offset_y = (height - len(shape) * 20) // 2

            for i, row in enumerate(shape):
                for j, cell in enumerate(row):
                    if cell:
                        r = int(color[1:3], 16) / 255
                        g = int(color[3:5], 16) / 255
                        b = int(color[5:7], 16) / 255
                        cr.set_source_rgb(r, g, b)
                        cr.rectangle(offset_x + j * 20, offset_y + i * 20, 18, 18)
                        cr.fill()

    def on_key_pressed(self, controller, keyval, keycode, state):
        """键盘按键处理"""
        if self.game_over:
            return False

        if keyval in (Gdk.KEY_a, Gdk.KEY_A, Gdk.KEY_Left):
            self.move(-1, 0)
        elif keyval in (Gdk.KEY_d, Gdk.KEY_D, Gdk.KEY_Right):
            self.move(1, 0)
        elif keyval in (Gdk.KEY_s, Gdk.KEY_S, Gdk.KEY_Down):
            self.drop()
            self.score += 1
            self.update_display()
        elif keyval in (Gdk.KEY_w, Gdk.KEY_W, Gdk.KEY_Up):
            self.rotate()
        elif keyval == Gdk.KEY_space:
            self.hard_drop()
        elif keyval == Gdk.KEY_p:
            self.paused = not self.paused

        return True

    def start_timer(self):
        """启动定时器"""
        self.stop_timer()

        def tick():
            if self.game_over or self.paused:
                return True
            self.drop()
            return True

        # 速度随等级增加
        interval = max(100, 500 - (self.level - 1) * 50)
        self.timer_id = GLib.timeout_add(interval, tick)

    def stop_timer(self):
        """停止定时器"""
        if self.timer_id:
            GLib.source_remove(self.timer_id)
            self.timer_id = None

    def show_game_over(self):
        """显示游戏结束对话框"""
        dialog = Adw.AlertDialog(
            heading=_("game_over"),
            body=f"{_('score')}: {self.score}\n{_('level')}: {self.level}\n{_('lines')}: {self.lines}"
        )
        dialog.add_response("ok", _("ok"))
        dialog.set_default_response("ok")
        dialog.present(self.widget.get_root())

    def stop(self):
        """停止游戏"""
        self.stop_timer()
        self.game_over = True
        if self.score > 0:
            self.score_manager.record_score("tetris", self.score)
