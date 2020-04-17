import os
import subprocess
from typing import Optional

import pynvim


@pynvim.plugin
class Plugin:
    def __init__(self, vim: pynvim.api.Nvim) -> None:
        self.vim: pynvim.api.Nvim = vim

    def _build_url(self) -> Optional[str]:
        abs_file_path: str = self.vim.funcs.expand("%:p")

        if not abs_file_path:
            return None

        self.vim.chdir(os.path.dirname(abs_file_path))

        # create relative file path
        try:
            top_level_dir: str = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                check=True,
                text=True,
            ).stdout.strip()
        except subprocess.CalledProcessError:
            return None
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
        url: Optional[str] = self._build_url()
        if not url:
            return
        subprocess.call(["xdg-open", url])

    @pynvim.command("GHGetUrl", sync=True)
    def get_url(self) -> None:
        url: Optional[str] = self._build_url()
        if not url:
            self.vim.funcs.setreg("+", [], "l")
            return
        self.vim.funcs.setreg("+", [url], "l")
