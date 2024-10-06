"""
AI-generated mdbook link rewrite script
"""

import argparse
import logging
import os
import re

from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def update_edit_urls(book_dir):
    for root, dirs, files in os.walk(book_dir):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f, "html.parser")

                if file in (
                    "matrix.html",
                    "entities.html",
                    "techniques.html",
                    "platforms.html",
                    "tactics.html",
                    "mitigations.html",
                ):
                    # Identify Matrix and Object list pages by their file names or content
                    change_links = soup.find_all("a", title="Suggest an edit")
                    for link in change_links:
                        link.decompose()
                    logger.info(f"Removed change links from {file_path}")

                elif file in (
                    "index.html",
                    "contribute.html",
                    "qna.html",
                ):
                    # Fix md pages
                    edit_link = soup.find("a", title="Suggest an edit")
                    if edit_link and "href" in edit_link.attrs:
                        old_url = edit_link["href"]
                        new_url = re.sub(
                            r"/edit/main/build/intro/([^\.]*?)\.md",
                            r"/edit/main/\1.md",
                            old_url,
                        )
                        edit_link["href"] = new_url
                        logger.debug(
                            f"Changed URL from '{old_url}' to '{new_url}'",
                        )
                else:
                    edit_link = soup.find("a", title="Suggest an edit")
                    if edit_link and "href" in edit_link.attrs:
                        old_url = edit_link["href"]
                        new_url = re.sub(
                            r"/edit/main/build/([^\.]*?)\.md",
                            r"/edit/main/\1.json",
                            old_url,
                        )
                        edit_link["href"] = new_url
                        logger.debug(
                            f"Changed URL from '{old_url}' to '{new_url}'",
                        )

                # Add the script to the end of the <head> section
                # Ugly solution but it works
                head = soup.find("head")
                if head:
                    script_tag_1 = soup.new_tag(
                        "script",
                        src="https://www.googletagmanager.com/gtag/js?id=G-BEG3SB4GH3",
                    )
                    script_tag_1.attrs["async"] = "async"
                    script_tag_2 = soup.new_tag("script")
                    script_tag_2.string = "window.dataLayer = window.dataLayer || [];\nfunction gtag(){dataLayer.push(arguments);}\ngtag('js', new Date());\ngtag('config', 'G-BEG3SB4GH3');"
                    head.append(script_tag_1)
                    head.append(script_tag_2)
                    logger.debug(f"Added Google Tag Manager script to {file_path}")

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(str(soup))


def main():
    parser = argparse.ArgumentParser(description="Update edit URLs in mdBook output.")
    parser.add_argument("--book-dir", help="Path to the mdBook output directory")
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug logging"
    )
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    book_dir = args.book_dir
    if not os.path.isdir(book_dir):
        logger.error(f"Error: The directory '{book_dir}' does not exist.")
        return

    update_edit_urls(book_dir)
    logger.info(f"Edit URLs have been updated in '{book_dir}'.")


if __name__ == "__main__":
    main()
