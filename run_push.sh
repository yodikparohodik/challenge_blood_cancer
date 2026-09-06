#!/usr/bin/env bash
# Publish main only after rejecting oversized reachable Git blobs.
set -euo pipefail

source /home/alexu/.config/npsv2back/github.env
: "${GITHUB_USER:?GITHUB_USER must be set}"
: "${GITHUB_TOKEN:?GITHUB_TOKEN must be set}"

max_blob_bytes="${MAX_GIT_BLOB_BYTES:-52428800}"  # 50 MiB by default
largest_blob_bytes="$({
    git rev-list --objects main |
        git cat-file --batch-check='%(objecttype) %(objectsize) %(rest)' |
        awk '$1 == "blob" {print $2}' |
        sort -nr |
        head -n 1
} || true)"
largest_blob_bytes="${largest_blob_bytes:-0}"

if (( largest_blob_bytes > max_blob_bytes )); then
    printf 'Refusing to push: main references a %s-byte blob (limit: %s bytes).\n' \
        "$largest_blob_bytes" "$max_blob_bytes" >&2
    exit 1
fi

remote_url="https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/yodikparohodik/challenge_blood_cancer.git"
remote_main="$(git ls-remote "$remote_url" refs/heads/main | awk 'NR == 1 {print $1}')"

if [[ -z "$remote_main" ]]; then
    printf 'Refusing to push: remote main branch was not found.\n' >&2
    exit 1
fi

git push --force-with-lease="refs/heads/main:${remote_main}" "$remote_url" main
git update-ref refs/remotes/origin/main HEAD
