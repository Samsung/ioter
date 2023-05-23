# Contributing to Ioter

As a contributor, here are the guidelines we would like you to follow.

- [Contributing to Ioter](#contributing-to-ioter)
  - [Bugs](#bugs)
  - [New Features](#new-features)
  - [Contributing Code](#contributing-code)
    - [Initial Setup](#initial-setup)
    - [Submitting a Pull Request](#submitting-a-pull-request)
      - [Branch](#branch)
      - [Create Commits](#create-commits)
      - [Upstream Sync and Clean Up](#upstream-sync-and-clean-up)
      - [Coding Conventions and Style](#coding-conventions-and-style)
      - [Push and Test](#push-and-test)
      - [Submit Pull Request](#submit-pull-request)
  - [Contributing Documentation](#contributing-documentation)

## Bugs

If you find a bug in the source code, you can help us by [submitting a GitHub Issue](https://github.com/Samsung/ioter/issues/new). Even better, you can [submit a Pull Request](#submitting-a-pull-request) with a fix.

## New Features

You can request a new feature by [submitting a GitHub Issue](https://github.com/Samsung/ioter/issues/new). Even better, you can [submit a Pull Request](#submitting-a-pull-request) with a fix.

## Contributing Code

The Ioter Project follows the "Fork-and-Pull" model for accepting contributions.

### Initial Setup

Setup your GitHub fork and continuous-integration services:

1. Fork the [Ioter repository](https://github.com/Samsung/ioter) by clicking "Fork" on the web UI.

Setup your local development environment:

```bash
# Clone your fork
git clone git@github.com:<username>/ioter.git

# Add upstream (For the first time after clone)
git remote add upstream git@github.com:Samsung/ioter.git
```

### Submitting a Pull Request

#### Branch

For each new feature, create a working branch:

```bash
# Create a working branch for your new feature
git branch --track <branch-name> origin/main

# Checkout the branch
git checkout <branch-name>
```

#### Create Commits

```bash
# Add each modified file you'd like to include in the commit
git add <file1> <file2>

# Create a commit
git commit
```

This will open up a text editor where you can write your commit message.

#### Upstream Sync and Clean Up

Prior to submitting your pull request, you might want to do a few things to clean up your branch and make it as simple as possible for the original repo's maintainer to test, accept, and merge your work.

If any commits have been made to the upstream main branch, you should rebase your development branch so that merging it will be a simple fast-forward that won't require any conflict resolution work.

```bash
# Fetch upstream main and merge with your repo's main branch
git checkout main
git pull upstream main

# If there were any new commits, rebase your development branch
git checkout <branch-name>
git rebase main
```

Now, it may be desirable to squash some of your smaller commits down into a small number of larger more cohesive commits. You can do this with an interactive rebase:

```bash
# Rebase all commits on your development branch
git checkout
git rebase -i main
```

This will open up a text editor where you can specify which commits to squash.

#### Coding Conventions and Style

Ioter uses and enforces the [autopep8](https://pypi.org/project/autopep8/) on all python code, except for code located in [third_party](third_party).

#### Push and Test

```bash
# Checkout your branch
git checkout <branch-name>

# Push to your GitHub fork:
git push origin <branch-name>
```

#### Submit Pull Request

Once you've validated that all continuous-integration checks have passed, go to the page for your fork on GitHub, select your development branch, and click the pull request button. If you need to make any adjustments to your pull request, just push the updates to GitHub. Your pull request will automatically track the changes on your development branch and update.

## Contributing Documentation

Documentation undergoes the same review process as code.
