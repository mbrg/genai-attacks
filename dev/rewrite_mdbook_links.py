import argparse
import os
import re

from bs4 import BeautifulSoup


def update_edit_urls(book_dir):
    for root, dirs, files in os.walk(book_dir):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f, "html.parser")

                edit_link = soup.find("a", title="Suggest an edit")
                if edit_link and "href" in edit_link.attrs:
                    old_url = edit_link["href"]
                    new_url = re.sub(
                        r"/edit/main/build/([^\.]*?)\.md",
                        r"/edit/main/\1.json",
                        old_url,
                    )
                    edit_link["href"] = new_url
                    print("Changed URL from", old_url, "to", new_url)

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(str(soup))


def main():
    parser = argparse.ArgumentParser(description="Update edit URLs in mdBook output.")
    parser.add_argument("book_dir", help="Path to the mdBook output directory")
    args = parser.parse_args()

    book_dir = args.book_dir
    if not os.path.isdir(book_dir):
        print(f"Error: The directory '{book_dir}' does not exist.")
        return

    update_edit_urls(book_dir)
    print(f"Edit URLs have been updated in '{book_dir}'.")


if __name__ == "__main__":
    main()
