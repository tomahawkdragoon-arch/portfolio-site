#!/usr/bin/env bash
# Netlify runs this before each build. Exit 0 = skip the deploy, exit 1 = deploy.
# Commits that only change the nightly prices file are skipped, so they cost no Netlify credits.
if [ -z "$CACHED_COMMIT_REF" ] || [ "$CACHED_COMMIT_REF" = "$COMMIT_REF" ]; then
  exit 1
fi
git diff --quiet "$CACHED_COMMIT_REF" "$COMMIT_REF" -- . ':(exclude)site/data/live.json'
