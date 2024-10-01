# How To Contribute

## How To Contribute Content?

| :point_up:    | You can edit any `.json` file or create a new one directly in your browser to easily contribute! |
|------|:---|

Improve our knowledge base by editing or adding files within these directories:

```
|
--| tactic
--| technique
--| procedure
--| entity
--| platform
```

File schema and how things work:
* Your change will be automatically tested for compliance with the [schema](/schema/) once a PR is created.
* Once a PR gets merged to `main`, the website will automatically update within a few minutes.
* You can check out the [schema](/schema/) directory or look at other files for reference.

## How To Work With this Repo? [Optional]

If you want to contribute as a developer or just prefer to work with git, and benefit from auto-fixes for some of the common issues:

### Set Up

```bash
# clone this repo
git clone <this-repo>
# install dependencies
pip install -r requirements.txt
# install pre-commit hooks
pre-commit install
```

### Run Tests

These tests must pass to merge to `main`. They will also auto-fix any issue they can.

```bash
pre-commit run --all-files
```

#### Common Issues
* If you get an _end-of-file-fixer_ error in the PR's tests, make sure that there's an empty line at the end of the file. IDEs can sometimes change this automatically according to your plugins.
* Make sure that the `$id` exactly matches the filename itself and the name field (both for best practice and to avoid constraint test errors).
* If you use code blocks using tripe backticks, make sure to add a new line `\n` before and after them.

### Build Locally

#### Setup

```bash
# install mdbook (replace the binary if you're not using Linux)
mkdir bin
curl -sSL https://github.com/rust-lang/mdBook/releases/download/v0.4.40/mdbook-v0.4.40-x86_64-unknown-linux-gnu.tar.gz | tar -xz --directory=bin
chmod +x bin/mdbook
# enable script execution
chmod +x build_scripts/local.sh
```

#### Build

```bash
# build mdbook
./build_scripts/local.sh
# open book/index.html to review the book
```

### Submit a PR to main

Any PR to `main` will trigger the [PR Validation](/.github/workflows/pr-validation.yaml) action, running the same tests that `pre-commit` runs.
These tests must pass for the PR to be merged.

Once merged to `main`, the [Release](/.github/workflows/release.yaml) action will trigger.
It will build the new website and upload it to Github Pages, within a few minutes.
