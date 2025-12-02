#!/usr/bin/env python3
"""游戏集合 - 主应用程序"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib

from score_manager import ScoreManager
from games.game_2048 import Game2048
from games.minesweeper import Minesweeper
from games.tetris import Tetris
from games.snake import Snake
from games.chess import Chess
from i18n import i18n, _


class GameCollection(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id='com.example.gamecollection',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.score_manager = ScoreManager()
        self.window = None

    def do_activate(self):
        if not self.window:
            self.window = MainWindow(application=self)
        self.window.present()


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title(_("app_name"))
        self.set_default_size(800, 600)

        self.app = kwargs.get('application')
        self.current_game = None

        # 注册语言变更回调
        i18n.add_callback(self.on_language_changed)

        # 创建导航视图
        self.navigation_view = Adw.NavigationView()
        self.set_content(self.navigation_view)

        # 创建欢迎页面
        self.welcome_page = self.create_welcome_page()
        self.navigation_view.push(self.welcome_page)

    def on_language_changed(self):
        """语言变更时刷新界面"""
        self.set_title(_("app_name"))
        self.refresh_welcome_page()

    def create_welcome_page(self):
        """创建欢迎页面"""
        page = Adw.NavigationPage(title=_("app_name"))

        toolbar_view = Adw.ToolbarView()
        page.set_child(toolbar_view)

        # 头部栏
        header = Adw.HeaderBar()
        toolbar_view.add_top_bar(header)

        # 右上角菜单按钮
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu_button.set_tooltip_text("Menu")

        # 创建菜单
        menu = Gio.Menu()

        # 语言子菜单
        lang_menu = Gio.Menu()
        lang_menu.append(_("chinese"), "win.set-lang-zh")
        lang_menu.append(_("english"), "win.set-lang-en")
        menu.append_submenu(_("language"), lang_menu)

        # 关于
        menu.append(_("about"), "win.show-about")

        menu_button.set_menu_model(menu)
        header.pack_end(menu_button)

        # 添加动作
        self.setup_actions()

        # 主内容
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        toolbar_view.set_content(scroll)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)
        main_box.set_margin_start(24)
        main_box.set_margin_end(24)
        scroll.set_child(main_box)

        # 欢迎横幅
        welcome_banner = Adw.StatusPage()
        welcome_banner.set_icon_name("applications-games-symbolic")
        welcome_banner.set_title(_("welcome_title"))
        welcome_banner.set_description(_("welcome_desc"))
        main_box.append(welcome_banner)

        # 常玩游戏部分
        frequent_games = self.app.score_manager.get_frequent_games()
        if frequent_games:
            frequent_group = Adw.PreferencesGroup()
            frequent_group.set_title(_("frequent_games"))
            main_box.append(frequent_group)

            for game_id, play_count in frequent_games[:3]:
                game_info = self.get_game_info(game_id)
                if game_info:
                    row = Adw.ActionRow()
                    row.set_title(game_info['name'])
                    row.set_subtitle(_("played_times", count=play_count))
                    row.set_activatable(True)
                    row.add_prefix(Gtk.Image.new_from_icon_name(game_info['icon']))
                    row.connect("activated", self.on_game_selected, game_id)

                    arrow = Gtk.Image.new_from_icon_name("go-next-symbolic")
                    row.add_suffix(arrow)
                    frequent_group.add(row)

        # 所有游戏
        all_games_group = Adw.PreferencesGroup()
        all_games_group.set_title(_("all_games"))
        main_box.append(all_games_group)

        games = [
            ("2048", "game_2048", "view-grid-symbolic"),
            ("minesweeper", "game_minesweeper", "dialog-warning-symbolic"),
            ("tetris", "game_tetris", "view-app-grid-symbolic"),
            ("snake", "game_snake", "emoji-nature-symbolic"),
            ("chess", "game_chess", "applications-games-symbolic"),
        ]

        for game_id, name_key, icon in games:
            row = Adw.ActionRow()
            row.set_title(_(name_key))

            high_score = self.app.score_manager.get_high_score(game_id)
            if high_score > 0:
                row.set_subtitle(_("high_score", score=high_score))

            row.set_activatable(True)
            row.add_prefix(Gtk.Image.new_from_icon_name(icon))
            row.connect("activated", self.on_game_selected, game_id)

            arrow = Gtk.Image.new_from_icon_name("go-next-symbolic")
            row.add_suffix(arrow)
            all_games_group.add(row)

        return page

    def setup_actions(self):
        """设置菜单动作"""
        # 设置中文
        action_zh = Gio.SimpleAction.new("set-lang-zh", None)
        action_zh.connect("activate", lambda a, p: self.set_language("zh"))
        self.add_action(action_zh)

        # 设置英文
        action_en = Gio.SimpleAction.new("set-lang-en", None)
        action_en.connect("activate", lambda a, p: self.set_language("en"))
        self.add_action(action_en)

        # 关于
        action_about = Gio.SimpleAction.new("show-about", None)
        action_about.connect("activate", lambda a, p: self.show_about_dialog())
        self.add_action(action_about)

    def set_language(self, lang):
        """设置语言"""
        i18n.lang = lang

    def show_about_dialog(self):
        """显示关于对话框"""
        about = Adw.AboutDialog(
            application_name=_("app_name"),
            application_icon="applications-games-symbolic",
            developer_name="Shus Mo",
            version="1.0.0",
            developers=["Shus Mo <fcanlnony@outlook.com>"],
            copyright="© 2025 Shus Mo",
            license_type=Gtk.License.GPL_3_0,
            website="https://github.com/fcanlnony/Mini-Games-Collection",
            issue_url="https://github.com/fcanlnony/Mini-Games-Collection/issues"
        )
        about.present(self)

    def get_game_info(self, game_id):
        """获取游戏信息"""
        games = {
            "2048": {"name": _("game_2048"), "icon": "view-grid-symbolic", "name_key": "game_2048"},
            "minesweeper": {"name": _("game_minesweeper"), "icon": "dialog-warning-symbolic", "name_key": "game_minesweeper"},
            "tetris": {"name": _("game_tetris"), "icon": "view-app-grid-symbolic", "name_key": "game_tetris"},
            "snake": {"name": _("game_snake"), "icon": "emoji-nature-symbolic", "name_key": "game_snake"},
            "chess": {"name": _("game_chess"), "icon": "applications-games-symbolic", "name_key": "game_chess"},
        }
        return games.get(game_id)

    def on_game_selected(self, row, game_id):
        """游戏被选中"""
        self.app.score_manager.record_play(game_id)

        game_page = self.create_game_page(game_id)
        if game_page:
            self.navigation_view.push(game_page)

    def create_game_page(self, game_id):
        """创建游戏页面"""
        game_info = self.get_game_info(game_id)
        if not game_info:
            return None

        page = Adw.NavigationPage(title=game_info['name'])

        toolbar_view = Adw.ToolbarView()
        page.set_child(toolbar_view)

        # 头部栏
        header = Adw.HeaderBar()
        toolbar_view.add_top_bar(header)

        # 返回按钮会自动添加

        # 新游戏按钮
        new_game_btn = Gtk.Button(label=_("new_game"))
        new_game_btn.add_css_class("suggested-action")
        header.pack_end(new_game_btn)

        # 创建游戏实例
        if game_id == "2048":
            game = Game2048(self.app.score_manager)
        elif game_id == "minesweeper":
            game = Minesweeper(self.app.score_manager)
        elif game_id == "tetris":
            game = Tetris(self.app.score_manager)
        elif game_id == "snake":
            game = Snake(self.app.score_manager)
        elif game_id == "chess":
            game = Chess(self.app.score_manager)
        else:
            return None

        self.current_game = game
        new_game_btn.connect("clicked", lambda b: game.new_game())

        toolbar_view.set_content(game.get_widget())

        # 页面隐藏时停止游戏
        page.connect("hidden", lambda p: self.on_game_hidden(game))

        return page

    def on_game_hidden(self, game):
        """游戏页面隐藏时"""
        if hasattr(game, 'stop'):
            game.stop()
        # 刷新欢迎页面
        self.refresh_welcome_page()

    def refresh_welcome_page(self):
        """刷新欢迎页面"""
        # 移除旧页面
        self.navigation_view.pop_to_page(self.welcome_page)
        # 重新创建欢迎页面
        self.navigation_view.remove(self.welcome_page)
        self.welcome_page = self.create_welcome_page()
        self.navigation_view.push(self.welcome_page)


def main():
    app = GameCollection()
    return app.run(None)


if __name__ == "__main__":
    main()
