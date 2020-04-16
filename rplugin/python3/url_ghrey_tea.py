import os
import subprocess

import pynvim  # type: ignore


@pynvim.plugin
class Plugin:
    def __init__(self, vim) -> None:
        self.vim = vim

    def _build_url(self) -> str:
        abs_file_path: str = self.vim.funcs.expand("%:p")

        self.vim.chdir(os.path.dirname(abs_file_path))

        # create relative file path
        top_level_dir: str = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            check=True,
            text=True,
        ).stdout.strip()
        rel_file_path: str = abs_file_path
        if rel_file_path.startswith(top_level_dir):
            rel_file_path = rel_file_path[len(top_level_dir) :].strip("/")

        # create URL to repo
        remote_url: str = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            check=True,
            text=True,
        ).stdout.strip()
        if remote_url.endswith(".git"):
            remote_url = os.path.splitext(remote_url)[0]
        if not remote_url.startswith("https://github.com"):
            remote_url = "https://github.com/" + remote_url.split(":")[1]

        line_no: str = self.vim.funcs.line(".")

        # create URL of the form:
        # https://github.com/username/repo_name/blob/master/relative_file_path#L1
        url: str = f"{remote_url}/blob/master/{rel_file_path}#L{line_no}"

        return url

    @pynvim.command("GHOpenUrl", sync=True)
    def open_url(self) -> None:
        url: str = self._build_url()
        subprocess.call(["xdg-open", url])

    @pynvim.command("GHGetUrl", sync=True)
    def get_url(self) -> None:
        url: str = self._build_url()
        self.vim.funcs.setreg("+", [url], "l")
