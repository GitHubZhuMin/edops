# EdOps 一键安装脚本 (Windows PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "正在开始安装 EdOps..." -ForegroundColor Green

# 1. 检查基础依赖
function Check-Dependency($name) {
    if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
        Write-Host "错误: 未安装 $name。请先安装 $name。" -ForegroundColor Red
        exit 1
    }
}

Check-Dependency python
Check-Dependency git
Check-Dependency docker

# 2. 确定安装目录
$INSTALL_DIR = Join-Path $HOME "edops-deploy"
if ($args.Count -gt 0) {
    $INSTALL_DIR = $args[0]
}

Write-Host "安装目录: $INSTALL_DIR" -ForegroundColor Yellow

# 3. 下载/更新源码
if (Test-Path (Join-Path $INSTALL_DIR ".git")) {
    Write-Host "目录已存在，正在更新源码..." -ForegroundColor Yellow
    Set-Location $INSTALL_DIR
    git pull
} else {
    Write-Host "正在克隆 EdOps 仓库..." -ForegroundColor Yellow
    git clone https://github.com/GitHubZhuMin/edops.git $INSTALL_DIR
    Set-Location $INSTALL_DIR
}

# 4. 创建并激活虚拟环境
if (-not (Test-Path "venv")) {
    Write-Host "正在创建虚拟环境..." -ForegroundColor Yellow
    python -m venv venv
}

# 激活虚拟环境 (Windows)
& .\venv\Scripts\Activate.ps1

# 5. 安装 EdOps
Write-Host "正在安装 EdOps 及其依赖..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -e .

# 6. 初始化配置提示
Write-Host "安装完成！" -ForegroundColor Green
Write-Host ""
Write-Host "请运行以下命令开始部署："
Write-Host "cd $INSTALL_DIR" -ForegroundColor Yellow
Write-Host ".\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "edops local bootstrap --preset standard" -ForegroundColor Yellow
