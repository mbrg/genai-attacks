python build_scripts/generate_content_as_md.py
bin/mdbook build
python build_scripts/rewrite_mdbook_links.py --book-dir book/
