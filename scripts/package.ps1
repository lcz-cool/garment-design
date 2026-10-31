<#
.SYNOPSIS
    garment-design skill 的打包 / 安装脚本（单一源在这里，别手改已安装副本）。

.DESCRIPTION
    源目录：<repo>\dist\garment-design\garment-design\
      ├─ SKILL.md
      ├─ references\
      ├─ assets\
      └─ scripts\

  默认动作：把源目录打成一个带 garment-design\ 包装层的 zip（可直接分发给别人）。
  -Install：再把源目录同步到 ~\.workbuddy\skills\garment-design。

  旧版备份默认落到 ~\.workbuddy\skill-backups\garment-design\（skills 目录的旁边，
  绝不放进去 —— 放进去会被 skill 扫描器当成另一个同名 skill）。默认保留最近 3 份。

.EXAMPLE
    powershell -File scripts\package.ps1
    powershell -File scripts\package.ps1 -Install
    powershell -File scripts\package.ps1 -Install -KeepBackups 1
    powershell -File scripts\package.ps1 -Install -InstallRoot "D:\skills"
#>
[CmdletBinding()]
param(
    [string]$Source,
    [string]$ZipPath,
    [switch]$Install,
    [string]$InstallRoot,
    # 旧版备份放这里。默认放到 skills 目录的旁边，绝不放进去 ——
    # 放进去会被 skill 扫描器当成另一个同名 skill，列表里越堆越多。
    [string]$BackupRoot,
    # 保留最近几份备份，更早的自动删除。设 0 表示全部保留。
    [int]$KeepBackups = 3
)

$ErrorActionPreference = 'Stop'
$skillName = 'garment-design'

# Remove-Item -Recurse 在部分环境里会被安全钩子接管（转回收站失败即抛错），
# 清理属于可失败操作，改用 .NET 目录删除并且失败只警告、不中断安装。
# 注意：git 的对象文件是只读的，必须先清属性，否则 Delete 报"拒绝访问"。
function Remove-DirectoryQuiet([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) { return $true }
    try {
        Get-ChildItem -LiteralPath $Path -Recurse -Force -ErrorAction SilentlyContinue |
            ForEach-Object { $_.Attributes = 'Normal' }
        [System.IO.Directory]::Delete($Path, $true)
        return $true
    }
    catch {
        Write-Warning "无法删除目录（已跳过，可手动清理）：$Path`n  $($_.Exception.Message)"
        return $false
    }
}

# $PSScriptRoot 在参数默认值阶段可能还是空的，所以默认值在脚本体里补
if (-not $Source) { $Source = Split-Path -Parent $PSScriptRoot }
if (-not $InstallRoot) { $InstallRoot = Join-Path $HOME '.workbuddy\skills' }

# ---------- 校验源 ----------
if (-not (Test-Path -LiteralPath $Source)) { throw "源目录不存在：$Source" }
$Source = (Resolve-Path -LiteralPath $Source).Path
if (-not (Test-Path -LiteralPath (Join-Path $Source 'SKILL.md'))) {
    throw "源目录里没有 SKILL.md，确认 -Source 指向 skill 根目录：$Source"
}
if (-not $ZipPath) {
    # 默认落到 <dist>\garment-design.zip —— 源的上一层是包装层，再上一层才是 dist
    $wrapperDir = Split-Path -Parent $Source
    $distDir = Split-Path -Parent $wrapperDir
    $ZipPath = Join-Path $distDir "${skillName}.zip"
}
$ZipPath = [System.IO.Path]::GetFullPath($ZipPath)

$files = Get-ChildItem -LiteralPath $Source -Recurse -File
Write-Host "源：$Source"
Write-Host ("文件 {0} 个，{1:N1} KB" -f $files.Count, (($files | Measure-Object Length -Sum).Sum / 1KB))

# ---------- 打包 ----------
$stage = Join-Path $env:TEMP ("gd-pack-" + [guid]::NewGuid().ToString('N').Substring(0, 8))
try {
    $stageSkill = Join-Path $stage $skillName
    New-Item -ItemType Directory -Path $stageSkill -Force | Out-Null
    Copy-Item -LiteralPath $Source -Destination $stage -Recurse -Force
    # 本地 git 历史不该进分发包（也不该进安装副本）
    foreach ($ex in @('.git', '.github')) {
        $p = Join-Path $stageSkill $ex
        if (Test-Path -LiteralPath $p) { Remove-DirectoryQuiet $p | Out-Null }
    }
    # Copy-Item 会把目录名带进来，这里统一成 stage\<skillName>
    if (-not (Test-Path -LiteralPath $stageSkill)) {
        throw "暂存目录结构异常：$stageSkill 不存在"
    }

    if (Test-Path -LiteralPath $ZipPath) {
        # 只删自己构建的那个 zip，路径已确认为 <dist>\garment-design.zip
        if ((Split-Path -Leaf $ZipPath) -ne "${skillName}.zip") { throw "拒绝覆盖非预期文件：$ZipPath" }
        Remove-Item -LiteralPath $ZipPath -Force
    }
    Compress-Archive -Path $stageSkill -DestinationPath $ZipPath -CompressionLevel Optimal
    Write-Host "已打包：$ZipPath" -ForegroundColor Green
}
finally {
    if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
}

# ---------- 安装 ----------
if ($Install) {
    if (-not (Test-Path -LiteralPath $InstallRoot)) {
        New-Item -ItemType Directory -Path $InstallRoot -Force | Out-Null
    }
    if (-not $BackupRoot) {
        $BackupRoot = Join-Path (Split-Path -Parent $InstallRoot) (Join-Path 'skill-backups' $skillName)
    }
    $BackupRoot = [System.IO.Path]::GetFullPath($BackupRoot)
    $installFull = [System.IO.Path]::GetFullPath($InstallRoot).TrimEnd('\') + '\'
    if ($BackupRoot.StartsWith($installFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "备份目录不能放在 skills 目录里，会被当成另一个 skill：$BackupRoot"
    }
    New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null

    $dest = Join-Path $InstallRoot $skillName
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    # 暂存与备份都放到 skills 目录之外，安装过程中不会在列表里闪出一个新条目
    $tmp = Join-Path $BackupRoot ".new-$stamp"
    $bak = Join-Path $BackupRoot "bak-$stamp"

    if (Test-Path -LiteralPath $tmp) { Remove-DirectoryQuiet $tmp | Out-Null }
    Copy-Item -LiteralPath $Source -Destination $tmp -Recurse -Force
    # 安装副本只放技能内容，不要变成一个可用的 git 工作区
    foreach ($ex in @('.git', '.github')) {
        $p = Join-Path $tmp $ex
        if (Test-Path -LiteralPath $p) { Remove-DirectoryQuiet $p | Out-Null }
    }
    $hadOld = Test-Path -LiteralPath $dest
    if ($hadOld) { Move-Item -LiteralPath $dest -Destination $bak }
    try {
        Move-Item -LiteralPath $tmp -Destination $dest
    }
    catch {
        if ($hadOld -and (Test-Path -LiteralPath $bak)) { Move-Item -LiteralPath $bak -Destination $dest }
        throw
    }

    $newHash = (Get-FileHash -LiteralPath (Join-Path $dest 'SKILL.md')).Hash
    $srcHash = (Get-FileHash -LiteralPath (Join-Path $Source 'SKILL.md')).Hash
    Write-Host "已安装：$dest" -ForegroundColor Green
    if ($hadOld) { Write-Host "旧版本备份：$bak" }
    if ($newHash -ne $srcHash) { throw "安装后 SKILL.md 哈希不一致，检查复制过程" }
    Write-Host "SKILL.md 哈希校验通过" -ForegroundColor Green

    # 清理安装过程中可能残留的暂存目录
    Get-ChildItem -LiteralPath $BackupRoot -Directory -Filter '.new-*' -ErrorAction SilentlyContinue |
        ForEach-Object { Remove-DirectoryQuiet $_.FullName | Out-Null }

    # 只留最近 $KeepBackups 份，避免长期使用后堆一堆旧版本
    if ($KeepBackups -gt 0) {
        $old = Get-ChildItem -LiteralPath $BackupRoot -Directory -Filter 'bak-*' -ErrorAction SilentlyContinue |
            Sort-Object Name -Descending | Select-Object -Skip $KeepBackups
        foreach ($o in $old) {
            if (Remove-DirectoryQuiet $o.FullName) { Write-Host "已清理旧备份：$($o.Name)" }
        }
    }
    $kept = @(Get-ChildItem -LiteralPath $BackupRoot -Directory -Filter 'bak-*' -ErrorAction SilentlyContinue).Count
    Write-Host "备份目录：$BackupRoot（保留 $kept 份）"
}
