# Dual Messenger+ website (source)

This branch holds everything needed to rebuild the website.
The published site itself lives on the `main` branch, which GitHub Pages serves.

## Build

```
pip install jinja2 markdown
python3 build.py
```

This writes two folders (both ignored by git):

- `dist/`: the site. To publish, copy its contents to the root of the `main` branch.
- `preview/`: one page that holds every language, for a quick look without a server.

## Where things are

- `content/<language>/site.json`: the home page texts. `privacy.md` and `terms.md`: the legal pages.
  English (`content/en`) is the original, the other 14 folders are translations.
- `templates/`: page templates. `static/`: stylesheet, fonts and images.
- `build.py`: the language list, the site address, the App Store id and the contact address.
- `tools/`: checks and helpers.
  - `check_lang.py CODE ...` compares a translation's structure with the English original.
  - `linkcheck.py` checks links and language tags in `dist/`.
  - `make_og.py` rebuilds the link-preview images.
  - `overflow.js`, `shoot.js` and `router_test.js` render pages for layout checks (they need Playwright and Chrome).
  - `images.py` rebuilds the phone screenshots from the original App Store screenshots, which are not in this repository.
  - `BRIEF.md` and `ref/`: the brief and the approved wording used for the translations.

## Changing a text

Edit the English file and the same place in each language folder, then run:

```
python3 tools/check_lang.py tr de nl fr es it pt-PT ru id ja zh-Hans ar he hi
python3 build.py
```

## Rules the texts follow

- Never state or imply that more than two accounts can be used.
- Themes and app icons are not mentioned as features.
- Translated legal pages carry a note that the English version applies if the two differ.
