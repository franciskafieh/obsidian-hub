import os

import approvaltests
from approvaltests import verify_as_json, verify, Options
from approvaltests.scrubbers import create_regex_scrubber
from approvaltests.storyboard import StoryBoard

import utils
from tests.helpers_for_testing import verify_as_markdown
from tests.test_templates import JINJA_TEMPLATES_DIR
from themes import get_theme_downloads, collect_data_for_theme, ThemeList
from utils import THEMES_JSON_FILE, get_json_from_github


def test_get_theme_downloads() -> None:
    downloads = get_theme_downloads()
    assert len(downloads) >= 117, len(downloads)

    key_of_first_download = list(downloads.keys())[0]
    download = downloads[key_of_first_download]
    assert download["id"] == key_of_first_download, download["id"]
    assert download["download"] > 0, download["download"]

    # TODO Don't add new themes
    verify_as_json(downloads,
                   options=Options().with_scrubber(create_regex_scrubber('"download": \d+,', '"download": 9999,')))


def test_get_community_themes() -> None:
    theme_list: ThemeList = get_json_from_github(THEMES_JSON_FILE)
    assert len(theme_list) >= 115, len(theme_list)

    first_theme = theme_list[0]
    assert len(first_theme["modes"]) > 0
    assert first_theme["author"] != ""
    assert first_theme["name"] != ""
    assert first_theme["screenshot"] != ""

    # TODO Don't add new themes - maybe get a fixed revision
    # verify_as_json(theme_list)


def test_collect_data_for_theme_with_settings() -> None:
    theme_name = "Minimal"
    verify_theme_data(theme_name)


def test_collect_data_for_theme_without_settings() -> None:
    theme_name = "Christmas"
    verify_theme_data(theme_name)


def test_rendering_of_theme() -> None:
    theme_name = "Minimal"

    template = utils.get_template_from_directory(JINJA_TEMPLATES_DIR, "theme.md.jinja")
    theme_downloads = get_theme_downloads()

    theme_list: ThemeList = get_json_from_github(THEMES_JSON_FILE)
    theme = None
    for t in theme_list:
        if t["name"] == theme_name:
            theme = t
            break
    assert theme

    name = collect_data_for_theme(theme, theme_downloads, template)
    assert name == theme_name

    file_path = "delete_me.md"
    absolute_file_path = os.path.abspath(file_path)
    file_content = utils.render_template_for_file(template, absolute_file_path, **theme)

    assert len(file_content) > 0

    # TODO Scrub the download numbers
    # verify_as_markdown(file_content)


def verify_theme_data(theme_name: str) -> None:
    s = StoryBoard()

    template = utils.get_template_from_directory(JINJA_TEMPLATES_DIR, "theme.md.jinja")
    theme_downloads = get_theme_downloads()

    theme_list: ThemeList = get_json_from_github(THEMES_JSON_FILE)
    theme = None
    for t in theme_list:
        if t["name"] == theme_name:
            theme = t
            break
    assert theme
    assert theme["name"] == theme_name
    assert len(theme["modes"]) > 0
    assert theme["author"] != ""

    s.add_frame(approvaltests.utils.to_json(theme))

    name = collect_data_for_theme(theme, theme_downloads, template)
    assert name == theme_name
    assert theme["user"] != ""
    s.add_frame(approvaltests.utils.to_json(theme))

    # TODO Scrub the download numbers
    # verify(s)
