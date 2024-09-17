# Welcome!

## How To Contribute Content?

Just edit any `.json` file or add a new one in the relevant directory. That's it!

* Your change will be automatically tested for compliance with the [schema](/schema/) once a PR is created.
* Once a PR gets merged to `main`, the website will automatically update within a few monutes.
* You can check out the [schema](/schema/) directory or look at other files for example, you'll find them at:

    ```
    .
    --| tactic:
    --| technique:
    --| procedure
    --| entity
    --| platform
    ```

---

If you want to contribute as a developer or just prefer to work with git and benefit from auto-fixes for some of the common issues: 

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

Tests will run and reviewers will be notified.
Once your PR is merged, an action will trigger to build and deploy your changes to the Github Pages website.