#!/usr/bin/env bash
set -euo pipefail

manifest=tools/dict-builder/manifest.json
source_root=/tmp
prefix=/tmp/moqi-pinned-libime

while (($#)); do
  case "$1" in
    --manifest) manifest=$2; shift 2 ;;
    --source-root) source_root=$2; shift 2 ;;
    --prefix) prefix=$2; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

read -r fcitx_repo fcitx_commit libime_repo kenlm_commit libime_commit < <(
  python3 - "$manifest" <<'PY'
import json, sys
m = json.load(open(sys.argv[1], encoding="utf-8"))
print(m["fcitx5_repository"], m["fcitx5_commit"], m["libime_repository"], m["kenlm_commit"], m["libime_commit"])
PY
)

work=$(mktemp -d -p "$source_root" moqi-pinned-libime.XXXXXX)
trap 'rm -rf "$work"' EXIT

fetch_commit() {
  local repo=$1 commit=$2 destination=$3
  git init --quiet "$destination"
  git -C "$destination" remote add origin "$repo"
  git -C "$destination" fetch --quiet --depth 1 origin "$commit"
  test "$(git -C "$destination" rev-parse FETCH_HEAD)" = "$commit"
  git -C "$destination" checkout --quiet --detach "$commit"
}

fetch_commit "$fcitx_repo" "$fcitx_commit" "$work/fcitx5"
fetch_commit "$libime_repo" "$libime_commit" "$work/libime"
git -C "$work/libime" submodule update --init --depth 1
test "$(git -C "$work/libime/src/libime/core/kenlm" rev-parse HEAD)" = "$kenlm_commit"

rm -rf "$prefix"
cmake -S "$work/fcitx5" -B "$work/fcitx5-build" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="$prefix/fcitx5" \
  -DENABLE_TEST=OFF -DENABLE_TESTING_ADDONS=OFF \
  -DENABLE_DBUS=OFF -DENABLE_X11=OFF -DENABLE_WAYLAND=OFF \
  -DENABLE_SERVER=OFF -DENABLE_KEYBOARD=OFF -DENABLE_ENCHANT=OFF \
  -DENABLE_EMOJI=OFF -DENABLE_LIBUUID=OFF -DENABLE_DL=OFF \
  -DENABLE_XDGAUTOSTART=OFF -DBUILD_SPELL_DICT=OFF -DEVENT_LOOP_BACKEND=none
cmake --build "$work/fcitx5-build" --parallel
cmake --install "$work/fcitx5-build"

cmake -S "$work/libime" -B "$work/libime-build" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="$prefix" \
  -DCMAKE_PREFIX_PATH="$prefix/fcitx5" \
  -DENABLE_TEST=OFF -DENABLE_DATA=OFF -DENABLE_TOOLS=ON
cmake --build "$work/libime-build" --parallel
cmake --install "$work/libime-build"

pinyindict="$prefix/bin/libime_pinyindict"
test -x "$pinyindict"
cat > "$prefix/toolchain.json" <<EOF
{
  "fcitx5_repository": "$fcitx_repo",
  "fcitx5_commit": "$fcitx_commit",
  "kenlm_commit": "$kenlm_commit",
  "libime_repository": "$libime_repo",
  "libime_commit": "$libime_commit",
  "pinyindict": "$pinyindict",
  "pinyindict_sha256": "$(sha256sum "$pinyindict" | cut -d ' ' -f1)"
}
EOF
cat "$prefix/toolchain.json"
