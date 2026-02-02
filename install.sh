#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
EdOps 安装与初始化脚本

用法:
  curl -fsSL <install.sh> | bash -s -- [options]

选项:
  --help                 显示帮助
  --repo <url>           Git 仓库地址（脚本不在仓库内时必填）
  --branch <name>        克隆的分支或标签（默认: main）
  --dir <path>           安装目录（默认: ~/.edops）
  --venv <path>          Python venv 路径（默认: <dir>/venv）
  --skip-bootstrap       跳过 edops local bootstrap

示例:
  curl -fsSL <install.sh> | bash -s -- --repo https://example.com/edops.git
EOF
}

REPO_URL="${EDOPS_INSTALL_REPO:-}"
BRANCH="${EDOPS_INSTALL_BRANCH:-main}"
INSTALL_DIR="${EDOPS_INSTALL_DIR:-$HOME/.edops}"
VENV_DIR="${EDOPS_VENV_DIR:-$INSTALL_DIR/venv}"
SKIP_BOOTSTRAP="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help)
      usage
      exit 0
      ;;
    --repo)
      REPO_URL="$2"
      shift 2
      ;;
    --branch)
      BRANCH="$2"
      shift 2
      ;;
    --dir)
      INSTALL_DIR="$2"
      shift 2
      ;;
    --venv)
      VENV_DIR="$2"
      shift 2
      ;;
    --skip-bootstrap)
      SKIP_BOOTSTRAP="true"
      shift 1
      ;;
    *)
      echo "未知参数: $1" >&2
      usage
      exit 1
      ;;
  esac
done

OS_NAME="$(uname -s | tr '[:upper:]' '[:lower:]')"
case "$OS_NAME" in
  linux*|darwin*|msys*|mingw*|cygwin*)
    ;;
  *)
    echo "当前系统 ($OS_NAME) 未被脚本显式支持，但仍会尝试安装。" >&2
    ;;
esac

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "未找到 Python，请先安装 Python 3.9+。" >&2
  exit 1
fi

if [[ -f "pyproject.toml" ]]; then
  SRC_DIR="$(pwd)"
else
  if [[ -z "$REPO_URL" ]]; then
    echo "未检测到 EdOps 源码目录，请使用 --repo 指定仓库地址。" >&2
    exit 1
  fi
  mkdir -p "$INSTALL_DIR"
  SRC_DIR="$INSTALL_DIR/src"
  if [[ -d "$SRC_DIR/.git" ]]; then
    git -C "$SRC_DIR" fetch --all --tags
    git -C "$SRC_DIR" checkout "$BRANCH"
    git -C "$SRC_DIR" pull --ff-only
  else
    git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$SRC_DIR"
  fi
fi

"$PYTHON_BIN" -m venv "$VENV_DIR"
if [[ -d "$VENV_DIR/bin" ]]; then
  PIP_BIN="$VENV_DIR/bin/pip"
  EDOPS_BIN="$VENV_DIR/bin/edops"
else
  PIP_BIN="$VENV_DIR/Scripts/pip.exe"
  EDOPS_BIN="$VENV_DIR/Scripts/edops.exe"
fi

"$PIP_BIN" install --upgrade pip setuptools wheel
"$PIP_BIN" install -e "$SRC_DIR"

if [[ "$SKIP_BOOTSTRAP" != "true" ]]; then
  "$EDOPS_BIN" local bootstrap
fi

cat <<EOF
✅ EdOps 已安装完成。
👉 可执行命令: $EDOPS_BIN
EOF
