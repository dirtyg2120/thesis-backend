#!/bin/sh
set -e

remote=socialbot@103.176.178.107

# NOTE: Only deploy from current git HEAD
git archive --format=tar.gz HEAD | ssh "$remote" 'cat >source.tar.gz'
ssh "$remote" ./backend/bin/pip install --upgrade \
	--disable-pip-version-check source.tar.gz
ssh "$remote" rm source.tar.gz
ssh "$remote" systemctl --user restart backend.service
