from threading import Timer

import sublime
import sublime_plugin


class BlockCursorEverywhere(sublime_plugin.EventListener):

    def show_block_cursor(self, view):
        validRegions = []
        for s in view.sel():
            if s.a != s.b:
                continue
            validRegions.append(sublime.Region(s.a, s.a + 1))

        if validRegions.__len__:
            view.add_regions('BlockCursorListener', validRegions, 'block_cursor', '', sublime.DRAW_NO_OUTLINE)
        else:
            view.erase_regions('BlockCursorListener')

    def on_selection_modified(self, view):
        if not view.settings().get('command_mode') or view.settings().get('is_widget'):
            view.erase_regions('BlockCursorListener')
            return

        self.show_block_cursor(view)

    def on_deactivated(self, view):
        view.erase_regions('BlockCursorListener')
        view.settings().clear_on_change('command_mode')
        self.current_view = None

    def on_activated(self, view):
        self.current_view = view
        self.timer = Timer(0, lambda: None)

        self.on_selection_modified(view)

        view.settings().add_on_change('command_mode', self.on_command_mode_change)

    def on_command_mode_change(self):
        # Debounce to prevent recursion and plugin crash https://github.com/karlhorky/BlockCursorEverywhere/issues/11
        self.timer.cancel()
        self.timer = Timer(0.0005, self.on_selection_modified, [self.current_view])
        self.timer.start()
