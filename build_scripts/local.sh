# generate markdown from json files
python build_scripts/generate_content_as_md.py
# customize book theme
mkdir -p build/theme
cp book_theme/head.hbs build/theme/head.hbs
# build book
bin/mdbook build
# rewrite book URLs
python build_scripts/rewrite_mdbook_links.py --book-dir book/
# echo book location for easy access
echo "book/index.html"
