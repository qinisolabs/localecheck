# Set up the git repo (run once, on your machine)

Do the folder restructure **here**, not in the scratch/download space — it's a
clean two-minute job at repo creation. Run these from the directory that
contains the downloaded `locale-api`, `locale-api-ts`, and `locale-eval` folders.

## 1. Arrange the monorepo layout

```bash
mkdir -p localecheck/packages

# TS is the primary package
mv locale-api-ts        localecheck/packages/localecheck-ts
mv locale-api           localecheck/packages/localecheck-python
mv locale-eval          localecheck/eval

# move repo-level docs to the root (they currently live in the python folder)
cd localecheck
mv packages/localecheck-python/PUBLISH.md        ./
mv packages/localecheck-python/BUSINESS_MODEL.md ./
mv packages/localecheck-python/benchmark.html    ./
mv packages/localecheck-python/llms.txt          ./
# bring in the downloaded root files: .gitignore, LOCAL_TEST.md, and
# README.root.md (rename it to README.md at the repo root)
#   mv ../README.root.md ./README.md     # adjust source path to where you downloaded it
```

Target structure:

```
localecheck/
├── README.md            (root brand overview)
├── .gitignore
├── PUBLISH.md
├── BUSINESS_MODEL.md
├── benchmark.html
├── llms.txt
├── LOCAL_TEST.md
├── packages/
│   ├── localecheck-ts/         ← primary; has its own data/, README, package.json
│   └── localecheck-python/     ← has its own data/, README, pyproject.toml
└── eval/
```

## 2. Clean any build artifacts before first commit

```bash
rm -rf packages/localecheck-ts/node_modules packages/localecheck-ts/dist
rm -rf packages/localecheck-python/build packages/localecheck-python/*.egg-info
find . -name __pycache__ -type d -prune -exec rm -rf {} +
```

(The `.gitignore` already excludes these, but clearing them keeps the first
commit clean.)

## 3. Init and verify, then commit

```bash
git init
git add .
git status            # confirm no node_modules / dist / __pycache__ are staged

# sanity-check both packages still build/test after the move:
( cd packages/localecheck-ts && npm install && npm test )      # 34 passed
( cd packages/localecheck-python && pip install -r requirements.txt && pytest -q )  # 27 passed

git commit -m "Initial commit: localecheck (TS + Python)"
```

## 4. Push to the GitHub org

Create the org first (see the brand-name decision), then:

```bash
git remote add origin git@github.com:qinisolabs/localecheck.git
git branch -M main
git push -u origin main
```

## Notes

- **Each package keeps its own `data/`** so it bundles correctly when published
  to npm / PyPI. If you want a single source of truth later, keep the canonical
  copy in one package and add a small `sync-data` script — don't move data
  outside the package dirs.
- Nothing in the code references the folder names, so the move is safe — paths
  are all relative within each package. Step 3's build/test re-run confirms it.
- Only after this is green do you follow `PUBLISH.md`.
