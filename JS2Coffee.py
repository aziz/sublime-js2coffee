import sublime
import sublime_plugin
import subprocess


class JsCoffeeCommand(sublime_plugin.TextCommand):

    def run(self, edit, new_file):
        self.new_file = new_file
        self.edit = edit
        self.settings = sublime.load_settings("JS2Coffee.sublime-settings")
        input_region = self.select_all(self.view)
        contents = self.view.substr(input_region)
        output = self.js2coffee(contents)

        if output:
            if self.new_file:
                view = self.view.window().new_file()
                output_region = self.select_all(view)
            else:
                view = self.view
                output_region = input_region


            view.replace(edit, output_region, output.decode('UTF-8'))
            view.set_syntax_file(self.settings.get("coffee_syntax_path"))

    def select_all(self, view):
        """returns a region containing the whole view"""
        return sublime.Region(0, self.view.size())

    def js2coffee(self, contents):
        js2coffee = subprocess.Popen(
            self.settings.get("js2coffee_path"),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        output, error = js2coffee.communicate(bytes(contents, 'UTF-8'))

        if error:
            self.write_to_console(error)
            self.view.window().run_command("show_panel", {"panel": "output.exec"})
            return None
        return output

    def write_to_console(self, str):
        self.output_view = self.view.window().get_output_panel("exec")
        selection_was_at_end = (
            len(self.output_view.sel()) == 1 and
            self.output_view.sel()[0] == sublime.Region(self.output_view.size())
        )
        self.output_view.set_read_only(False)
        self.output_view.insert(self.edit, self.output_view.size(), str.decode('UTF-8'))
        if selection_was_at_end:
            self.output_view.show(self.output_view.size())
        self.output_view.set_read_only(True)
