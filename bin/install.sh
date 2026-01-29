#!/bin/bash

# EdOps 一键安装脚本
# 支持 Linux, macOS

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}正在开始安装 EdOps...${NC}"

# 1. 检查基础依赖
check_dependency() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${RED}错误: 未安装 $1。请先安装 $1。${NC}"
        exit 1
    fi
}

check_dependency python3
check_dependency git
check_dependency docker

# 2. 确定安装目录
INSTALL_DIR="${HOME}/edops-deploy"
if [ -n "$1" ]; then
    INSTALL_DIR="$1"
fi

echo -e "${YELLOW}安装目录: ${INSTALL_DIR}${NC}"

# 3. 下载/更新源码
if [ -d "${INSTALL_DIR}/.git" ]; then
    echo -e "${YELLOW}目录已存在，正在更新源码...${NC}"
    cd "${INSTALL_DIR}"
    git pull
else
    echo -e "${YELLOW}正在克隆 EdOps 仓库...${NC}"
    git clone https://github.com/GitHubZhuMin/edops.git "${INSTALL_DIR}"
    cd "${INSTALL_DIR}"
fi

# 4. 创建并激活虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}正在创建虚拟环境...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate

# 5. 安装 EdOps
echo -e "${YELLOW}正在安装 EdOps 及其依赖...${NC}"
pip install --upgrade pip
pip install -e .

# 6. 初始化配置提示
echo -e "${GREEN}安装完成！${NC}"
echo -e ""
echo -e "请运行以下命令开始部署："
echo -e "${YELLOW}cd ${INSTALL_DIR}${NC}"
echo -e "${YELLOW}source venv/bin/activate${NC}"
echo -e "${YELLOW}edops local bootstrap --preset standard${NC}"
echo -e ""
echo -e "您可以将 edops 添加到您的 PATH 中，或者使用别名。"
