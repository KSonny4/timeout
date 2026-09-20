#!/bin/sh
# Install a released binary without root, overwrites or changes to shell configuration.
set -eu
version=
prefix=${HOME:?HOME is required}/.local
usage() { printf '%s\n' 'Usage: sh install.sh --version X.Y.Z [--prefix DIR]'; }
die() { printf 'timeout install: %s\n' "$*" >&2; exit 1; }
while [ "$#" -gt 0 ]; do
  case "$1" in
    --version) [ "$#" -ge 2 ] || die 'missing version'; version=$2; shift 2 ;;
    --prefix) [ "$#" -ge 2 ] || die 'missing prefix'; prefix=$2; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) usage >&2; die "unknown argument: $1" ;;
  esac
done
printf '%s\n' "$version" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$' || die 'an explicit numeric --version X.Y.Z is required'
case "$prefix" in /*) ;; *) die '--prefix must be an absolute path' ;; esac
case "$(uname -s)" in
  Darwin) os=apple-darwin ;;
  Linux) os=unknown-linux-gnu
    ldd --version 2>&1 | grep -Eiq 'glibc|GNU libc' || die 'Linux release binaries require glibc; build from source on other libcs' ;;
  *) die 'supported systems are macOS and glibc Linux' ;;
esac
case "$(uname -m)" in
  arm64|aarch64) arch=aarch64 ;;
  x86_64|amd64) arch=x86_64 ;;
  *) die 'supported architectures are Apple Silicon/ARM64 and x86_64' ;;
esac
[ ! -e "$prefix/bin/timeout" ] && [ ! -L "$prefix/bin/timeout" ] || die "refusing to overwrite $prefix/bin/timeout"
[ ! -e "$prefix/share/doc/timeout" ] && [ ! -L "$prefix/share/doc/timeout" ] || die "documentation destination already exists"
command -v curl >/dev/null || die 'curl is required'
work=$(mktemp -d "${TMPDIR:-/tmp}/timeout-install.XXXXXXXX")
staged=
trap 'rm -rf "$work"; [ -z "$staged" ] || rm -f "$staged"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
name=timeout-$version-$arch-$os
base=https://github.com/KSonny4/timeout/releases/download/v$version
fetch() {
  curl --fail --location --proto '=https' --proto-redir '=https' \
    --connect-timeout 20 --max-time 180 --retry 2 --output "$2" "$1"
}
fetch "$base/$name.tar.gz" "$work/$name.tar.gz"
fetch "$base/SHA256SUMS" "$work/SHA256SUMS"
expected=$(awk -v file="$name.tar.gz" '$2 == file { print $1 }' "$work/SHA256SUMS")
printf '%s\n' "$expected" | grep -Eq '^[a-f0-9]{64}$' || die 'missing or invalid checksum'
if command -v shasum >/dev/null; then
  actual=$(shasum -a 256 "$work/$name.tar.gz" | awk '{print $1}')
elif command -v sha256sum >/dev/null; then
  actual=$(sha256sum "$work/$name.tar.gz" | awk '{print $1}')
else
  die 'shasum or sha256sum is required'
fi
[ "$actual" = "$expected" ] || die 'release checksum mismatch'
tar -tzf "$work/$name.tar.gz" | awk -v root="$name" '
  $0 !~ ("^" root "(/|$)") || $0 ~ /(^|\/)\.\.(\/|$)/ { bad=1 }
  END { exit bad }' || die 'unexpected archive layout'
tar -xzf "$work/$name.tar.gz" -C "$work"
[ -f "$work/$name/bin/timeout" ] && [ ! -L "$work/$name/bin/timeout" ] || die 'missing regular executable'
[ -d "$work/$name/share/doc/timeout" ] || die 'missing licence/source documentation'
mkdir -p "$prefix/bin" "$prefix/share/doc"
staged=$(mktemp "$prefix/bin/.timeout-install.XXXXXXXX")
cat "$work/$name/bin/timeout" > "$staged"
chmod 755 "$staged"
ln "$staged" "$prefix/bin/timeout" || die 'destination appeared during installation; refusing to replace it'
cp -R "$work/$name/share/doc/timeout" "$prefix/share/doc/timeout"
printf 'Installed %s/bin/timeout\nEnsure %s/bin is on PATH.\n' "$prefix" "$prefix"
