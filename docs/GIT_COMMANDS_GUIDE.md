# 🔧 Basic Git Commands Guide

A reference for the most commonly used Git commands, with examples for each.

---

## Table of Contents

1. [git init](#git-init)
2. [git clone](#git-clone)
3. [git status](#git-status)
4. [git add](#git-add)
5. [git commit](#git-commit)
6. [git push](#git-push)
7. [git pull](#git-pull)

---

## git init

**What it does:** Creates a new, empty Git repository in the current directory (or converts an existing project into a Git repository).

```bash
# Initialize a new repository in the current directory
git init

# Initialize a new repository in a specific folder (creates it if needed)
git init my-project
```

After running `git init`, a hidden `.git/` folder is created that tracks all version history.

---

## git clone

**What it does:** Downloads a copy of an existing remote repository to your local machine, including all commits and branches.

```bash
# Clone a repository via HTTPS
git clone https://github.com/AloSantana/Antigravitys.git

# Clone into a custom directory name
git clone https://github.com/AloSantana/Antigravitys.git my-workspace

# Clone a specific branch
git clone -b main https://github.com/AloSantana/Antigravitys.git
```

---

## git status

**What it does:** Shows the state of the working directory and staging area — which files have been modified, which are staged for the next commit, and which are untracked.

```bash
# Check status of the current repository
git status

# Short / compact output
git status -s
```

Example output:

```
On branch main
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
        modified:   backend/main.py

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        docs/NEW_FEATURE.md
```

---

## git add

**What it does:** Stages changes (new files, modifications, or deletions) so they will be included in the next commit.

```bash
# Stage a single file
git add backend/main.py

# Stage a specific directory
git add docs/

# Stage all changes in the current directory (new, modified, and deleted)
git add .

# Stage parts of a file interactively
git add -p backend/main.py
```

> **Tip:** `git add .` stages everything. Use `git status` first to review what you are about to stage.

---

## git commit

**What it does:** Records the staged changes as a new snapshot (commit) in the repository history, with a descriptive message.

```bash
# Commit with an inline message
git commit -m "Add Git commands guide to docs"

# Stage all tracked modified files and commit in one step
git commit -am "Fix typo in README"

# Open the default editor to write a multi-line commit message
git commit
```

**Writing good commit messages:**
- Use the imperative mood: "Add feature" not "Added feature"
- Keep the subject line under 72 characters
- Optionally add a blank line followed by a longer description

---

## git push

**What it does:** Uploads local commits to a remote repository so others can access them.

```bash
# Push the current branch to the remote named 'origin'
git push origin main

# Push and set the upstream tracking branch (first push of a new branch)
git push -u origin feature/my-new-feature

# Push all local branches
git push --all origin
```

> **Note:** You must have write access to the remote repository to push.

---

## git pull

**What it does:** Fetches changes from a remote repository and immediately merges them into the current local branch. It is the combination of `git fetch` + `git merge`.

```bash
# Pull the latest changes for the current branch from 'origin'
git pull

# Pull from a specific remote and branch
git pull origin main

# Pull using rebase instead of merge (keeps a cleaner history)
git pull --rebase origin main
```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `git init` | Create a new local repository |
| `git clone <url>` | Download a remote repository |
| `git status` | Check working tree and staging area |
| `git add <file>` | Stage changes for the next commit |
| `git commit -m "<msg>"` | Save staged changes to history |
| `git push origin <branch>` | Upload local commits to remote |
| `git pull` | Fetch and merge remote changes |

---

## Typical Workflow Example

```bash
# 1. Clone the repository
git clone https://github.com/AloSantana/Antigravitys.git
cd Antigravitys

# 2. Check what has changed
git status

# 3. Stage your changes
git add docs/GIT_COMMANDS_GUIDE.md

# 4. Commit the changes
git commit -m "Add Git commands guide"

# 5. Push to the remote
git push origin main

# 6. Pull the latest changes from teammates
git pull
```

---

*For more advanced Git topics (branching, merging, rebasing, stashing), see the [official Git documentation](https://git-scm.com/doc).*
