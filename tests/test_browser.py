import os
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
import shutil
import subprocess
from tempfile import TemporaryDirectory
from threading import Thread
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
VIRTUAL_TIME_BUDGET_MS = 5000
BROWSER_TIMEOUT_SECONDS = 30


def find_browser():
    browser = os.environ.get("BROWSER_BIN") or next(
        (path for name in ("chromium", "chromium-browser", "google-chrome", "msedge", "chrome")
         if (path := shutil.which(name))),
        None,
    )
    if browser:
        return browser
    for location in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
        directory = os.environ.get(location)
        if not directory:
            continue
        for relative in ("Google/Chrome/Application/chrome.exe", "Microsoft/Edge/Application/msedge.exe"):
            path = Path(directory) / relative
            if path.is_file():
                return str(path)
    return None


class BrowserDiscoveryTest(unittest.TestCase):
    def test_finds_windows_installations_outside_path(self):
        for location in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
            for relative in ("Google/Chrome/Application/chrome.exe", "Microsoft/Edge/Application/msedge.exe"):
                with self.subTest(location=location, browser=relative), TemporaryDirectory() as directory:
                    browser = Path(directory) / relative
                    browser.parent.mkdir(parents=True)
                    browser.touch()
                    with patch.dict(os.environ, {location: directory}, clear=True), patch.object(shutil, "which", return_value=None):
                        self.assertEqual(find_browser(), str(browser))

    def test_explicit_browser_takes_precedence(self):
        with TemporaryDirectory() as directory:
            browser = str(Path(directory) / "custom-browser.exe")
            with patch.dict(os.environ, {"BROWSER_BIN": browser}, clear=True), patch.object(shutil, "which", return_value=str(Path(directory) / "path-browser.exe")):
                self.assertEqual(find_browser(), browser)

    def test_path_takes_precedence_over_windows_installations(self):
        with TemporaryDirectory() as directory:
            installed = Path(directory) / "Microsoft/Edge/Application/msedge.exe"
            installed.parent.mkdir(parents=True)
            installed.touch()
            browser = str(Path(directory) / "path-browser.exe")
            with patch.dict(os.environ, {"PROGRAMFILES": directory}, clear=True), patch.object(shutil, "which", return_value=browser):
                self.assertEqual(find_browser(), browser)

    def test_missing_browser_still_returns_none(self):
        with TemporaryDirectory() as directory:
            (Path(directory) / "Google/Chrome/Application/chrome.exe").mkdir(parents=True)
            with patch.dict(os.environ, {"PROGRAMFILES": directory}, clear=True), patch.object(shutil, "which", return_value=None):
                self.assertIsNone(find_browser())


class BrowserRegressionTest(unittest.TestCase):
    def test_regression_pages(self):
        browser = find_browser()
        self.assertIsNotNone(browser, "Set BROWSER_BIN to an installed Chrome, Edge, or Chromium executable.")
        pages = sorted((ROOT / "tests").glob("*.html"))
        self.assertTrue(pages, "No browser regression pages found.")

        handler = partial(SimpleHTTPRequestHandler, directory=str(ROOT))
        with ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                for page in pages:
                    with self.subTest(page=page.name), TemporaryDirectory() as profile:
                        result = subprocess.run(
                            [browser, "--headless", "--disable-gpu", "--no-first-run",
                             f"--user-data-dir={profile}", "--dump-dom",
                             f"--virtual-time-budget={VIRTUAL_TIME_BUDGET_MS}",
                             f"http://127.0.0.1:{server.server_port}/tests/{page.name}"],
                            capture_output=True,
                            encoding="utf-8",
                            timeout=BROWSER_TIMEOUT_SECONDS,
                            check=False,
                        )
                        self.assertEqual(result.returncode, 0, result.stderr)
                        status = re.search(r'<p id="status" role="status">([^<]*)</p>', result.stdout)
                        self.assertIsNotNone(status, "Browser did not return the regression page status.")
                        self.assertEqual(status.group(1), "통과했습니다.", page.name)
            finally:
                server.shutdown()
                thread.join()
