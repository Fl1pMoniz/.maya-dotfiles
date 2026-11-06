#!/usr/bin/env python3
"""Maya Rofi web-search mode.

Search with the configured engine, open URLs directly, use leading bangs for
alternate sites, and optionally fetch suggestions by ending the query with `!`.
The interaction follows the existing rofi-web-search script by pdonadeo (MIT).
"""
from pathlib import Path
import gzip
import html
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request

DEFAULT_CONFIG = {
    "search_engine": "google",
    "browser": "xdg-open",
}
BROWSERS = {
    "zen": ["zen-browser"],
    "chrome": ["google-chrome-stable"],
    "chromium": ["chromium"],
    "brave": ["brave-browser"],
    "firefox": ["firefox"],
    "xdg-open": ["xdg-open"],
}
ENGINES = {
    "google": (
        "Google",
        "https://www.google.com/search?q={query}",
        "https://suggestqueries.google.com/complete/search?client=firefox&q={query}",
    ),
    "duckduckgo": (
        "DuckDuckGo",
        "https://duckduckgo.com/?q={query}",
        "https://duckduckgo.com/ac/?type=list&q={query}",
    ),
    "wikipedia": (
        "Wikipedia",
        "https://en.wikipedia.org/w/index.php?search={query}",
        None,
    ),
    "youtube": (
        "YouTube",
        "https://www.youtube.com/results?search_query={query}",
        None,
    ),
    "github": (
        "GitHub",
        "https://github.com/search?type=repositories&q={query}",
        None,
    ),
    "aur": (
        "AUR",
        "https://aur.archlinux.org/packages?K={query}",
        None,
    ),
    "openstreetmap": (
        "OpenStreetMap",
        "https://www.openstreetmap.org/search?query={query}",
        None,
    ),
    "dictionary": (
        "Dictionary",
        "https://duckduckgo.com/?q=define+{query}",
        None,
    ),
}
BANGS = {
    "g": "google",
    "google": "google",
    "ddg": "duckduckgo",
    "duck": "duckduckgo",
    "w": "wikipedia",
    "wiki": "wikipedia",
    "yt": "youtube",
    "youtube": "youtube",
    "gh": "github",
    "aur": "aur",
    "maps": "openstreetmap",
    "define": "dictionary",
}


def config_path():
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "rofi" / "web-search.json"


def load_config():
    config = dict(DEFAULT_CONFIG)
    try:
        loaded = json.loads(config_path().read_text())
    except (OSError, ValueError):
        return config
    if isinstance(loaded, dict):
        engine = loaded.get("search_engine")
        browser = loaded.get("browser")
        if engine in ENGINES:
            config["search_engine"] = engine
        if isinstance(browser, str) and browser:
            config["browser"] = browser
    return config


def browser_command(browser):
    command = BROWSERS.get(browser, browser.split())
    return command if command else BROWSERS["xdg-open"]


def open_target(target, browser):
    if os.environ.get("MAYA_WEB_DRY_RUN"):
        print(target)
        return
    try:
        subprocess.Popen(
            [*browser_command(browser), target],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError:
        pass


def split_query(query):
    """Return (engine name, text) after applying a leading search bang."""
    match = re.match(r"^!([A-Za-z]+)\s+(.+)$", query)
    if match and match.group(1).lower() in BANGS:
        return BANGS[match.group(1).lower()], match.group(2).strip()
    return None, query


def search_url(query, config):
    if re.match(r"^[a-z][a-z0-9+.-]*://", query, re.I):
        return query
    if re.match(r"^www\.", query, re.I):
        return "https://" + query
    engine, text = split_query(query)
    engine = engine or config["search_engine"]
    _, template, _ = ENGINES[engine]
    return template.format(query=urllib.parse.quote_plus(text))


def fetch_suggestions(query, config):
    engine, text = split_query(query)
    engine = engine or config["search_engine"]
    template = ENGINES[engine][2]
    if not template:
        return []
    request = urllib.request.Request(
        template.format(query=urllib.parse.quote_plus(text)),
        headers={"User-Agent": "Mozilla/5.0 (Wayland; Linux x86_64) rofi-web-search"},
    )
    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            data = response.read()
            if response.headers.get("Content-Encoding") == "gzip":
                data = gzip.decompress(data)
        parsed = json.loads(data)
    except (OSError, ValueError):
        return []
    if engine == "duckduckgo":
        return [html.unescape(item.get("phrase", "")) for item in parsed if item.get("phrase")]
    if isinstance(parsed, list) and len(parsed) > 1 and isinstance(parsed[1], list):
        return [html.unescape(item) for item in parsed[1] if item]
    return []


def main():
    config = load_config()
    retv = int(os.environ.get("ROFI_RETV", "0"))
    info = os.environ.get("ROFI_INFO", "")
    query = " ".join(sys.argv[1:]).strip()
    browser = os.environ.get("MAYA_BROWSER") or config["browser"]

    if retv == 2 and query.endswith("!"):
        suggestions = fetch_suggestions(query.rstrip("! ").strip(), config)
        if suggestions:
            print("\n".join(suggestions))
        else:
            target = search_url(query.rstrip("! ").strip(), config)
            print(f"Search the web for {query.rstrip('! ').strip()}\0info\x1furl\x1f{target}")
        return

    if retv == 1:
        if info.startswith("url\x1f"):
            open_target(info.split("\x1f", 1)[1], browser)
        elif query:
            open_target(search_url(query, config), browser)
        return

    if retv == 2:
        if query:
            open_target(search_url(query, config), browser)
        return

    print("Type a query and press Enter\0nonselectable\x1ftrue")
    print("End with ! to fetch search suggestions\0nonselectable\x1ftrue")
    print("Use !g, !ddg, !w, !yt, !gh or !aur for another site\0nonselectable\x1ftrue")


if __name__ == "__main__":
    main()
