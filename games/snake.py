"""贪吃蛇游戏"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, GLib, Adw
import random
import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])
from i18n import _


class Snake:
    def __init__(self, score_manager):
        self.score_manager = score_manager
        self.cols = 20
        self.rows = 15
        self.cell_size = 24

        self.snake = []
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = None
        self.score = 0
        self.game_over = False
        self.paused = False
        self.timer_id = None

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

        # 游戏区域
        game_frame = Gtk.Frame()
        game_frame.add_css_class("card")
        main_box.append(game_frame)

        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_size_request(
            self.cols * self.cell_size,
            self.rows * self.cell_size
        )
        self.drawing_area.set_draw_func(self.draw)
        game_frame.set_child(self.drawing_area)

        # 控制说明
        hint_label = Gtk.Label(label=_("hint_snake"))
        hint_label.add_css_class("dim-label")
        main_box.append(hint_label)

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
        # 初始化蛇（在中间位置，长度为3）
        start_x = self.cols // 2
        start_y = self.rows // 2
        self.snake = [(start_x - i, start_y) for i in range(3)]

        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.score = 0
        self.game_over = False
        self.paused = False

        self.spawn_food()
        self.start_timer()
        self.update_display()
        self.widget.grab_focus()

    def spawn_food(self):
        """生成食物"""
        empty_cells = []
        for x in range(self.cols):
            for y in range(self.rows):
                if (x, y) not in self.snake:
                    empty_cells.append((x, y))

        if empty_cells:
            self.food = random.choice(empty_cells)

    def update_display(self):
        """更新显示"""
        self.score_label.set_label(f"{_('score')}: {self.score}")
        self.drawing_area.queue_draw()

    def draw(self, area, cr, width, height):
        """绘制游戏区域"""
        # 背景
        cr.set_source_rgb(0.1, 0.12, 0.1)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        # 网格线
        cr.set_source_rgb(0.15, 0.18, 0.15)
        for i in range(self.rows + 1):
            cr.move_to(0, i * self.cell_size)
            cr.line_to(self.cols * self.cell_size, i * self.cell_size)
        for j in range(self.cols + 1):
            cr.move_to(j * self.cell_size, 0)
            cr.line_to(j * self.cell_size, self.rows * self.cell_size)
        cr.stroke()

        # 绘制蛇
        for i, (x, y) in enumerate(self.snake):
            if i == 0:
                # 蛇头
                cr.set_source_rgb(0.2, 0.8, 0.2)
            else:
                # 蛇身 - 渐变颜色
                intensity = 0.6 - (i / len(self.snake)) * 0.3
                cr.set_source_rgb(0.1, intensity, 0.1)

            px = x * self.cell_size + 2
            py = y * self.cell_size + 2
            size = self.cell_size - 4

            # 圆角矩形
            cr.rectangle(px, py, size, size)
            cr.fill()

            # 蛇头的眼睛
            if i == 0:
                cr.set_source_rgb(0, 0, 0)
                eye_size = 4
                dx, dy = self.direction

                if dx == 1:  # 向右
                    cr.arc(px + size - 6, py + 6, eye_size / 2, 0, 2 * 3.14159)
                    cr.fill()
                    cr.arc(px + size - 6, py + size - 6, eye_size / 2, 0, 2 * 3.14159)
                    cr.fill()
                elif dx == -1:  # 向左
                    cr.arc(px + 6, py + 6, eye_size / 2, 0, 2 * 3.14159)
                    cr.fill()
                    cr.arc(px + 6, py + size - 6, eye_size / 2, 0, 2 * 3.14159)
                    cr.fill()
                elif dy == -1:  # 向上
                    cr.arc(px + 6, py + 6, eye_size / 2, 0, 2 * 3.14159)
                    cr.fill()
                    cr.arc(px + size - 6, py + 6, eye_size / 2, 0, 2 * 3.14159)
                    cr.fill()
                else:  # 向下
                    cr.arc(px + 6, py + size - 6, eye_size / 2, 0, 2 * 3.14159)
                    cr.fill()
                    cr.arc(px + size - 6, py + size - 6, eye_size / 2, 0, 2 * 3.14159)
                    cr.fill()

        # 绘制食物
        if self.food:
            x, y = self.food
            px = x * self.cell_size + self.cell_size // 2
            py = y * self.cell_size + self.cell_size // 2
            radius = self.cell_size // 2 - 4

            # 红色苹果
            cr.set_source_rgb(0.9, 0.1, 0.1)
            cr.arc(px, py, radius, 0, 2 * 3.14159)
            cr.fill()

            # 叶子
            cr.set_source_rgb(0.1, 0.6, 0.1)
            cr.move_to(px, py - radius)
            cr.line_to(px + 4, py - radius - 6)
            cr.line_to(px + 8, py - radius - 2)
            cr.fill()

        # 游戏结束覆盖层
        if self.game_over:
            cr.set_source_rgba(0, 0, 0, 0.7)
            cr.rectangle(0, 0, width, height)
            cr.fill()

            cr.set_source_rgb(1, 1, 1)
            cr.select_font_face("Sans", 0, 1)
            cr.set_font_size(24)
            text = "游戏结束"
            extents = cr.text_extents(text)
            cr.move_to(width / 2 - extents.width / 2, height / 2)
            cr.show_text(text)

    def on_key_pressed(self, controller, keyval, keycode, state):
        """键盘按键处理"""
        if self.game_over:
            return False

        # 防止180度转向
        if keyval in (Gdk.KEY_w, Gdk.KEY_W, Gdk.KEY_Up) and self.direction != (0, 1):
            self.next_direction = (0, -1)
        elif keyval in (Gdk.KEY_s, Gdk.KEY_S, Gdk.KEY_Down) and self.direction != (0, -1):
            self.next_direction = (0, 1)
        elif keyval in (Gdk.KEY_a, Gdk.KEY_A, Gdk.KEY_Left) and self.direction != (1, 0):
            self.next_direction = (-1, 0)
        elif keyval in (Gdk.KEY_d, Gdk.KEY_D, Gdk.KEY_Right) and self.direction != (-1, 0):
            self.next_direction = (1, 0)
        elif keyval == Gdk.KEY_p:
            self.paused = not self.paused

        return True

    def move(self):
        """移动蛇"""
        if self.game_over or self.paused:
            return

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # 检查碰撞
        if self.check_collision(new_head):
            self.game_over = True
            self.stop_timer()
            self.score_manager.record_score("snake", self.score)
            self.show_game_over()
            self.drawing_area.queue_draw()
            return

        self.snake.insert(0, new_head)

        # 检查是否吃到食物
        if new_head == self.food:
            self.score += 10
            self.spawn_food()
            self.update_display()
        else:
            self.snake.pop()

        self.drawing_area.queue_draw()

    def check_collision(self, pos):
        """检查碰撞"""
        x, y = pos

        # 撞墙
        if x < 0 or x >= self.cols or y < 0 or y >= self.rows:
            return True

        # 撞自己
        if pos in self.snake:
            return True

        return False

    def start_timer(self):
        """启动定时器"""
        self.stop_timer()

        def tick():
            if not self.game_over:
                self.move()
                return True
            return False

        # 速度：大约150ms移动一次
        self.timer_id = GLib.timeout_add(150, tick)

    def stop_timer(self):
        """停止定时器"""
        if self.timer_id:
            GLib.source_remove(self.timer_id)
            self.timer_id = None

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
        self.stop_timer()
        self.game_over = True
        if self.score > 0:
            self.score_manager.record_score("snake", self.score)
