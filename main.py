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
from games.chinese_chess import ChineseChess
from games.tic_tac_toe import TicTacToe
from i18n import i18n, _


# 游戏配置
GAMES_CONFIG = [
    ("2048", "game_2048", "view-grid-symbolic"),
    ("minesweeper", "game_minesweeper", "dialog-warning-symbolic"),
    ("tetris", "game_tetris", "view-app-grid-symbolic"),
    ("snake", "game_snake", "emoji-nature-symbolic"),
    ("chess", "game_chess", "applications-games-symbolic"),
    ("chinese_chess", "game_chinese_chess", "media-playback-start-symbolic"),
    ("tic_tac_toe", "game_tic_tac_toe", "view-dual-symbolic"),
]


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
        self.set_resizable(True)

        self.app = kwargs.get('application')
        self.current_game = None

        # 注册语言变更回调
        i18n.add_callback(self.on_language_changed)

        # 创建导航视图
        self.navigation_view = Adw.NavigationView()
        self.set_content(self.navigation_view)

        # 创建主页面
        self.home_page = self.create_home_page()
        self.navigation_view.push(self.home_page)

    def on_language_changed(self):
        """语言变更时刷新界面"""
        self.set_title(_("app_name"))
        self.refresh_home_page()

    def create_home_page(self):
        """创建主页面（一级界面）"""
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

        menu = Gio.Menu()
        lang_menu = Gio.Menu()
        lang_menu.append(_("chinese"), "win.set-lang-zh")
        lang_menu.append(_("english"), "win.set-lang-en")
        menu.append_submenu(_("language"), lang_menu)
        menu.append(_("about"), "win.show-about")

        menu_button.set_menu_model(menu)
        header.pack_end(menu_button)

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

        # 导航分组
        nav_group = Adw.PreferencesGroup()
        main_box.append(nav_group)

        # 常玩游戏入口
        frequent_row = Adw.ActionRow()
        frequent_row.set_title(_("frequent_games"))
        frequent_row.set_subtitle(_("frequent_games_desc"))
        frequent_row.set_activatable(True)
        frequent_row.add_prefix(Gtk.Image.new_from_icon_name("starred-symbolic"))
        frequent_row.add_suffix(Gtk.Image.new_from_icon_name("go-next-symbolic"))
        frequent_row.connect("activated", lambda r: self.show_frequent_games())
        nav_group.add(frequent_row)

        # 所有游戏入口
        all_games_row = Adw.ActionRow()
        all_games_row.set_title(_("all_games"))
        all_games_row.set_subtitle(_("all_games_desc"))
        all_games_row.set_activatable(True)
        all_games_row.add_prefix(Gtk.Image.new_from_icon_name("view-app-grid-symbolic"))
        all_games_row.add_suffix(Gtk.Image.new_from_icon_name("go-next-symbolic"))
        all_games_row.connect("activated", lambda r: self.show_all_games())
        nav_group.add(all_games_row)

        return page

    def show_frequent_games(self):
        """显示常玩游戏页面（二级界面）"""
        page = Adw.NavigationPage(title=_("frequent_games"))

        toolbar_view = Adw.ToolbarView()
        page.set_child(toolbar_view)

        header = Adw.HeaderBar()
        toolbar_view.add_top_bar(header)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        toolbar_view.set_content(scroll)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)
        main_box.set_margin_start(24)
        main_box.set_margin_end(24)
        scroll.set_child(main_box)

        frequent_games = self.app.score_manager.get_frequent_games()

        if frequent_games:
            games_group = Adw.PreferencesGroup()
            main_box.append(games_group)

            for game_id, play_count in frequent_games:
                game_info = self.get_game_info(game_id)
                if game_info:
                    row = Adw.ActionRow()
                    row.set_title(game_info['name'])
                    row.set_subtitle(_("played_times", count=play_count))
                    row.set_activatable(True)
                    row.add_prefix(Gtk.Image.new_from_icon_name(game_info['icon']))
                    row.add_suffix(Gtk.Image.new_from_icon_name("go-next-symbolic"))
                    row.connect("activated", self.on_game_selected, game_id)
                    games_group.add(row)
        else:
            # 没有常玩游戏时显示提示
            empty_status = Adw.StatusPage()
            empty_status.set_icon_name("starred-symbolic")
            empty_status.set_title(_("no_frequent_games"))
            empty_status.set_description(_("no_frequent_games_desc"))
            main_box.append(empty_status)

        self.navigation_view.push(page)

    def show_all_games(self):
        """显示所有游戏页面（二级界面）"""
        page = Adw.NavigationPage(title=_("all_games"))

        toolbar_view = Adw.ToolbarView()
        page.set_child(toolbar_view)

        header = Adw.HeaderBar()
        toolbar_view.add_top_bar(header)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        toolbar_view.set_content(scroll)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)
        main_box.set_margin_start(24)
        main_box.set_margin_end(24)
        scroll.set_child(main_box)

        games_group = Adw.PreferencesGroup()
        main_box.append(games_group)

        for game_id, name_key, icon in GAMES_CONFIG:
            row = Adw.ActionRow()
            row.set_title(_(name_key))

            high_score = self.app.score_manager.get_high_score(game_id)
            if high_score > 0:
                row.set_subtitle(_("high_score", score=high_score))

            row.set_activatable(True)
            row.add_prefix(Gtk.Image.new_from_icon_name(icon))
            row.add_suffix(Gtk.Image.new_from_icon_name("go-next-symbolic"))
            row.connect("activated", self.on_game_selected, game_id)
            games_group.add(row)

        self.navigation_view.push(page)

    def setup_actions(self):
        """设置菜单动作"""
        action_zh = Gio.SimpleAction.new("set-lang-zh", None)
        action_zh.connect("activate", lambda a, p: self.set_language("zh"))
        self.add_action(action_zh)

        action_en = Gio.SimpleAction.new("set-lang-en", None)
        action_en.connect("activate", lambda a, p: self.set_language("en"))
        self.add_action(action_en)

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
            "2048": {"name": _("game_2048"), "icon": "view-grid-symbolic"},
            "minesweeper": {"name": _("game_minesweeper"), "icon": "dialog-warning-symbolic"},
            "tetris": {"name": _("game_tetris"), "icon": "view-app-grid-symbolic"},
            "snake": {"name": _("game_snake"), "icon": "emoji-nature-symbolic"},
            "chess": {"name": _("game_chess"), "icon": "applications-games-symbolic"},
            "chinese_chess": {"name": _("game_chinese_chess"), "icon": "media-playback-start-symbolic"},
            "tic_tac_toe": {"name": _("game_tic_tac_toe"), "icon": "view-dual-symbolic"},
        }
        return games.get(game_id)

    def on_game_selected(self, row, game_id):
        """游戏被选中"""
        self.app.score_manager.record_play(game_id)

        game_page = self.create_game_page(game_id)
        if game_page:
            self.navigation_view.push(game_page)

    def create_game_page(self, game_id):
        """创建游戏页面（三级界面）"""
        game_info = self.get_game_info(game_id)
        if not game_info:
            return None

        page = Adw.NavigationPage(title=game_info['name'])

        toolbar_view = Adw.ToolbarView()
        page.set_child(toolbar_view)

        header = Adw.HeaderBar()
        toolbar_view.add_top_bar(header)

        new_game_btn = Gtk.Button(label=_("new_game"))
        new_game_btn.add_css_class("suggested-action")
        header.pack_end(new_game_btn)

        # 创建游戏实例
        game_classes = {
            "2048": Game2048,
            "minesweeper": Minesweeper,
            "tetris": Tetris,
            "snake": Snake,
            "chess": Chess,
            "chinese_chess": ChineseChess,
            "tic_tac_toe": TicTacToe,
        }

        game_class = game_classes.get(game_id)
        if not game_class:
            return None

        game = game_class(self.app.score_manager)
        self.current_game = game
        new_game_btn.connect("clicked", lambda b: game.new_game())

        # 使用 ScrolledWindow 包裹游戏内容，允许窗口调整大小
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_child(game.get_widget())
        toolbar_view.set_content(scroll)

        page.connect("hidden", lambda p: self.on_game_hidden(game))

        return page

    def on_game_hidden(self, game):
        """游戏页面隐藏时"""
        if hasattr(game, 'stop'):
            game.stop()

    def refresh_home_page(self):
        """刷新主页面"""
        self.navigation_view.pop_to_page(self.home_page)
        self.navigation_view.remove(self.home_page)
        self.home_page = self.create_home_page()
        self.navigation_view.push(self.home_page)


def main():
    app = GameCollection()
    return app.run(None)


if __name__ == "__main__":
    main()
