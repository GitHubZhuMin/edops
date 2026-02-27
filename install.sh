#!/usr/bin/env bash
set -euo pipefail

DEFAULT_REPO_URL="https://github.com/GitHubZhuMin/edops.git"
DEFAULT_REPO_BRANCH="edops"
GLOBAL_ENV_BLOCK_BEGIN="# >>> edops global env >>>"
GLOBAL_ENV_BLOCK_END="# <<< edops global env <<<"

usage() {
  cat <<EOF
EdOps 安装与初始化脚本

用法:
  curl -fsSL <install.sh-url> | bash -s -- [options]
  bash install.sh [options]

选项:
  --help                 显示帮助
  --repo <url>           Git 仓库地址（默认: $DEFAULT_REPO_URL）
  --branch <name>        克隆的分支或标签（默认仓库为 edops，自定义仓库自动探测）
  --dir <path>           安装目录（默认: ~/.edops）
  --venv <path>          Python venv 路径（默认: <dir>/venv）
  --root <path>          EdOps 环境目录（等价于 edops --root <path>）
  --preset <name>        初始化预设（minimal/standard/full，默认: standard）
  --no-preset            不应用任何预设
  --skip-init            跳过 edops config save --init
  --skip-bootstrap       跳过 edops local bootstrap
  --skip-global-path     跳过写入 shell 环境变量（PATH）

示例:
  curl -fsSL https://raw.githubusercontent.com/GitHubZhuMin/edops/edops/install.sh | bash
  curl -fsSL https://raw.githubusercontent.com/GitHubZhuMin/edops/edops/install.sh | \
    bash -s -- --dir /opt/edops --root /data/edops --preset standard
EOF
}

require_value() {
  local option="$1"
  local value="${2:-}"
  if [[ -z "$value" ]]; then
    echo "参数 $option 需要一个值。" >&2
    usage
    exit 1
  fi
}

detect_default_branch() {
  local repo_url="$1"
  local head_ref=""
  head_ref="$(git ls-remote --symref "$repo_url" HEAD 2>/dev/null | awk '/^ref:/ {print $2}' | sed 's#refs/heads/##' | head -n 1 || true)"
  if [[ -n "$head_ref" ]]; then
    echo "$head_ref"
  else
    echo "main"
  fi
}

choose_shell_rc_files() {
  local shell_name
  shell_name="$(basename "${SHELL:-}")"
  case "$shell_name" in
    zsh)
      RC_FILES=("$HOME/.zshrc" "$HOME/.profile")
      ;;
    bash)
      RC_FILES=("$HOME/.bashrc" "$HOME/.profile")
      ;;
    *)
      RC_FILES=("$HOME/.profile")
      ;;
  esac
}

upsert_shell_block() {
  local target_file="$1"
  local block_line="$2"
  local tmp_in tmp_out

  tmp_in="$(mktemp)"
  tmp_out="$(mktemp)"

  if [[ -f "$target_file" ]]; then
    awk -v begin="$GLOBAL_ENV_BLOCK_BEGIN" -v end="$GLOBAL_ENV_BLOCK_END" '
      $0 == begin {skip=1; next}
      $0 == end {skip=0; next}
      !skip {print}
    ' "$target_file" >"$tmp_in"
  else
    : >"$tmp_in"
  fi

  {
    cat "$tmp_in"
    if [[ -s "$tmp_in" ]]; then
      printf '\n'
    fi
    printf '%s\n' "$GLOBAL_ENV_BLOCK_BEGIN"
    printf '%s\n' "$block_line"
    printf '%s\n' "$GLOBAL_ENV_BLOCK_END"
  } >"$tmp_out"

  mv "$tmp_out" "$target_file"
  rm -f "$tmp_in"
}

setup_global_path() {
  local env_file="$1"
  local bin_dir="$2"
  local block_line=""
  local rc_file=""

  mkdir -p "$(dirname "$env_file")"
  cat >"$env_file" <<EOF
# EdOps installer generated file.
export EDOPS_INSTALL_DIR="$INSTALL_DIR"
export EDOPS_VENV_DIR="$VENV_DIR"
export EDOPS_BIN="$EDOPS_BIN"
export PATH="$bin_dir:\$PATH"
EOF

  block_line="if [ -f \"$env_file\" ]; then . \"$env_file\"; fi"
  choose_shell_rc_files
  for rc_file in "${RC_FILES[@]}"; do
    upsert_shell_block "$rc_file" "$block_line"
  done
}

REPO_URL="${EDOPS_INSTALL_REPO:-$DEFAULT_REPO_URL}"
BRANCH="${EDOPS_INSTALL_BRANCH:-}"
BRANCH_EXPLICIT="false"
if [[ -n "${EDOPS_INSTALL_BRANCH:-}" ]]; then
  BRANCH_EXPLICIT="true"
fi
INSTALL_DIR="${EDOPS_INSTALL_DIR:-$HOME/.edops}"
VENV_DIR="${EDOPS_VENV_DIR:-$INSTALL_DIR/venv}"
ROOT_DIR="${EDOPS_INSTALL_ROOT:-}"
PRESET="${EDOPS_INSTALL_PRESET:-standard}"
VENV_EXPLICIT="false"
if [[ -n "${EDOPS_VENV_DIR:-}" ]]; then
  VENV_EXPLICIT="true"
fi
SKIP_INIT="false"
SKIP_BOOTSTRAP="false"
SKIP_GLOBAL_PATH="false"
GLOBAL_ENV_FILE="${EDOPS_INSTALL_ENV_FILE:-$HOME/.config/edops/env.sh}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help)
      usage
      exit 0
      ;;
    --repo)
      require_value "$1" "${2:-}"
      REPO_URL="$2"
      shift 2
      ;;
    --branch)
      require_value "$1" "${2:-}"
      BRANCH="$2"
      BRANCH_EXPLICIT="true"
      shift 2
      ;;
    --dir)
      require_value "$1" "${2:-}"
      INSTALL_DIR="$2"
      shift 2
      ;;
    --venv)
      require_value "$1" "${2:-}"
      VENV_DIR="$2"
      VENV_EXPLICIT="true"
      shift 2
      ;;
    --root)
      require_value "$1" "${2:-}"
      ROOT_DIR="$2"
      shift 2
      ;;
    --preset)
      require_value "$1" "${2:-}"
      PRESET="$2"
      shift 2
      ;;
    --no-preset)
      PRESET=""
      shift 1
      ;;
    --skip-init)
      SKIP_INIT="true"
      shift 1
      ;;
    --skip-bootstrap)
      SKIP_BOOTSTRAP="true"
      shift 1
      ;;
    --skip-global-path)
      SKIP_GLOBAL_PATH="true"
      shift 1
      ;;
    *)
      echo "未知参数: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ "$VENV_EXPLICIT" != "true" ]]; then
  VENV_DIR="$INSTALL_DIR/venv"
fi

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

"$PYTHON_BIN" - <<'EOF'
import sys
if sys.version_info < (3, 9):
    raise SystemExit("当前 Python 版本低于 3.9，请升级后重试。")
EOF

if [[ -f "pyproject.toml" ]]; then
  SRC_DIR="$(pwd)"
else
  if ! command -v git >/dev/null 2>&1; then
    echo "未找到 git，请先安装 git 后重试。" >&2
    exit 1
  fi
  if [[ -z "$REPO_URL" ]]; then
    echo "未检测到 EdOps 源码目录且仓库地址为空，请通过 --repo 指定仓库。" >&2
    exit 1
  fi
  if [[ "$BRANCH_EXPLICIT" != "true" ]]; then
    if [[ "$REPO_URL" == "$DEFAULT_REPO_URL" ]]; then
      BRANCH="$DEFAULT_REPO_BRANCH"
    else
      BRANCH="$(detect_default_branch "$REPO_URL")"
    fi
  fi
  mkdir -p "$INSTALL_DIR"
  SRC_DIR="$INSTALL_DIR/src"
  if [[ -d "$SRC_DIR/.git" ]]; then
    CURRENT_REMOTE="$(git -C "$SRC_DIR" remote get-url origin 2>/dev/null || true)"
    if [[ -n "$CURRENT_REMOTE" && "$CURRENT_REMOTE" != "$REPO_URL" ]]; then
      git -C "$SRC_DIR" remote set-url origin "$REPO_URL"
    fi
    git -C "$SRC_DIR" fetch --all --tags
    git -C "$SRC_DIR" checkout "$BRANCH"
    if git -C "$SRC_DIR" rev-parse --verify "refs/remotes/origin/$BRANCH" >/dev/null 2>&1; then
      git -C "$SRC_DIR" pull --ff-only origin "$BRANCH"
    fi
  else
    git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$SRC_DIR"
  fi
fi

mkdir -p "$(dirname "$VENV_DIR")"
"$PYTHON_BIN" -m venv "$VENV_DIR"
if [[ -d "$VENV_DIR/bin" ]]; then
  PIP_BIN="$VENV_DIR/bin/pip"
  EDOPS_BIN="$VENV_DIR/bin/edops"
  TUTOR_BIN="$VENV_DIR/bin/tutor"
else
  PIP_BIN="$VENV_DIR/Scripts/pip.exe"
  EDOPS_BIN="$VENV_DIR/Scripts/edops.exe"
  TUTOR_BIN="$VENV_DIR/Scripts/tutor.exe"
fi

"$PIP_BIN" install --upgrade pip setuptools wheel
"$PIP_BIN" install -e "$SRC_DIR"

if [[ ! -x "$EDOPS_BIN" && -x "$TUTOR_BIN" ]]; then
  EDOPS_BIN="$TUTOR_BIN"
fi
if [[ ! -x "$EDOPS_BIN" ]]; then
  echo "安装完成但未找到 edops/tutor 可执行文件，请检查安装日志。" >&2
  exit 1
fi

EDOPS_BIN_DIR="$(dirname "$EDOPS_BIN")"
export PATH="$EDOPS_BIN_DIR:$PATH"

if [[ "$SKIP_GLOBAL_PATH" != "true" ]]; then
  if setup_global_path "$GLOBAL_ENV_FILE" "$EDOPS_BIN_DIR"; then
    GLOBAL_PATH_STATUS="是"
    GLOBAL_PATH_HINT="source \"$GLOBAL_ENV_FILE\""
  else
    GLOBAL_PATH_STATUS="否（自动写入失败）"
    GLOBAL_PATH_HINT="export PATH=\"$EDOPS_BIN_DIR:\$PATH\""
    echo "⚠️ 自动写入全局 PATH 失败。"
    echo "   可手动执行: export PATH=\"$EDOPS_BIN_DIR:\$PATH\""
  fi
else
  GLOBAL_PATH_STATUS="否（用户跳过）"
  GLOBAL_PATH_HINT="export PATH=\"$EDOPS_BIN_DIR:\$PATH\""
fi

if [[ -n "$ROOT_DIR" ]]; then
  EDOPS_CMD=("$EDOPS_BIN" --root "$ROOT_DIR")
else
  EDOPS_CMD=("$EDOPS_BIN")
fi

if [[ "$SKIP_INIT" != "true" ]]; then
  INIT_ARGS=(config save --init)
  if [[ -n "$PRESET" ]]; then
    INIT_ARGS+=(--preset "$PRESET")
  fi
  "${EDOPS_CMD[@]}" "${INIT_ARGS[@]}"
  INIT_STATUS="是"
else
  INIT_STATUS="否（用户跳过）"
fi

if [[ "$SKIP_BOOTSTRAP" != "true" ]]; then
  BOOTSTRAP_ARGS=(local bootstrap)
  if [[ "$SKIP_INIT" == "true" && -n "$PRESET" ]]; then
    BOOTSTRAP_ARGS+=(--preset "$PRESET")
  fi
  if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    "${EDOPS_CMD[@]}" "${BOOTSTRAP_ARGS[@]}"
    BOOTSTRAP_STATUS="是"
  else
    BOOTSTRAP_STATUS="否（Docker 未就绪）"
    BOOTSTRAP_HINT=("${EDOPS_CMD[@]}" "${BOOTSTRAP_ARGS[@]}")
    printf -v BOOTSTRAP_HINT_CMD '%q ' "${BOOTSTRAP_HINT[@]}"
    echo "⚠️ 检测到 Docker daemon 未就绪，已跳过 bootstrap。"
    echo "   Docker 就绪后请执行: ${BOOTSTRAP_HINT_CMD% }"
  fi
else
  BOOTSTRAP_STATUS="否（用户跳过）"
fi

cat <<EOF
✅ EdOps 已安装完成。
👉 源码目录: $SRC_DIR
👉 代码分支: ${BRANCH:-<当前目录>}
👉 可执行命令: $EDOPS_BIN
👉 初始化预设: ${PRESET:-<未使用>}
👉 已执行初始化: $INIT_STATUS
👉 已执行 bootstrap: $BOOTSTRAP_STATUS
👉 全局 PATH: $GLOBAL_PATH_STATUS
👉 立即生效执行: $GLOBAL_PATH_HINT
EOF
