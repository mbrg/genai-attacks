# Welcome to GenAI Attacks Matrix!

## How To Contribute Content?

Edit any `.json` file in the directories listed below, or add a new one. That's it!

* Your change will be automatically tested for compliance with the [schema](/schema/) once a PR is created.
* Once a PR gets merged to `main`, the website will automatically update within a few minutes.
* You can check out the [schema](/schema/) directory or look at other files for example, you'll find them at:

```
|
--| tactic
--| technique
--| procedure
--| entity
--| platform
```

## How To Work With the Repo?

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

### Submit a PR to main

Any PR to `main` will trigger the [PR Validation](/.github/workflows/pr-validation.yaml) action, running the same tests that `pre-commit` runs.
These tests must pass for the PR to be merged.

Once merged to `main`, the [Release](/.github/workflows/release.yaml) action will trigger.
It will build the new website and upload it to Github Pages, within a few minutes.
