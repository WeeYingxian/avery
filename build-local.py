"""Wrap the artifact source in a full HTML document so it can be served locally.

The published Artifact supplies its own <!doctype>/<head> wrapper; a local file
needs one or the browser falls back to quirks mode. Run this after editing
avery-plan.html to refresh index.html.
"""
import pathlib

here = pathlib.Path(__file__).parent
src = (here / "avery-plan.html").read_text(encoding="utf-8")

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="avery.ico" sizes="any">
<link rel="apple-touch-icon" href="avery.ico">
<style>
  :root{color-scheme:light dark}
  body{margin:0}
  img{max-width:100%}
  [hidden]{display:none!important}
</style>
</head>
<body>
"""

(here / "index.html").write_text(HEAD + src + "\n</body>\n</html>\n", encoding="utf-8")
print("index.html written:", (here / "index.html").stat().st_size, "bytes")
