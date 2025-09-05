<#
push_to_remote.ps1

Usage examples (run from project root):

# Backup remote and force-push local main to remote
.\scripts\push_to_remote.ps1 -BackupRemote -ForcePush

# Reset remote to empty (destructive) after backing up, then push
.\scripts\push_to_remote.ps1 -BackupRemote -ResetRemote -ForcePush

Parameters:
-RemoteUrl: remote repository URL (default: https://github.com/Feruz2024/Media-Planner.git)
-Branch: local branch to push as remote main (default: main)
-CommitMessage: commit message for the local commit
-BackupRemote: create a mirror backup of remote before destructive steps
-ResetRemote: push an empty orphan branch to remote to wipe remote main (confirms interactively)
-ForcePush: use --force when pushing local branch to remote
#>
param(
    [string]$RemoteUrl = "https://github.com/Feruz2024/Media-Planner.git",
    [string]$Branch = "main",
    [string]$CommitMessage = "Scaffold: initial dockerized backend + stations + planner models",
    [switch]$BackupRemote,
    [switch]$ResetRemote,
    [switch]$ForcePush
)

function Abort($msg){ Write-Host "ERROR: $msg" -ForegroundColor Red; exit 1 }

# Check git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Abort "git is not installed or not in PATH." }

# Ensure we're in a git repo
$root = git rev-parse --show-toplevel 2>$null
if ($LASTEXITCODE -ne 0) { Abort "Current directory is not inside a git repository. Run this from the project root." }
Set-Location $root.Trim()
Write-Host "Repository root: $pwd"

# Backup remote if requested
if ($BackupRemote) {
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupDir = "$PWD\remote-backup-$timestamp"
    Write-Host "Creating mirror backup of remote '$RemoteUrl' -> $backupDir"
    git clone --mirror $RemoteUrl $backupDir
    if ($LASTEXITCODE -ne 0) { Abort "Failed to clone remote for backup." }
    Write-Host "Backup created at: $backupDir"
}

# Confirm destructive reset if requested
if ($ResetRemote) {
    $confirm = Read-Host "You requested to reset the remote branch '$Branch' to empty. This is DESTRUCTIVE. Type 'YES' to continue"
    if ($confirm -ne 'YES') { Abort "Reset aborted by user." }
    $tmpBranch = "clean-reset-$(Get-Date -Format 'yyyyMMddHHmmss')"
    Write-Host "Creating orphan branch '$tmpBranch' and pushing it to remote as '$Branch'"
    git checkout --orphan $tmpBranch
    git rm -rf . 2>$null
    git clean -fdx 2>$null
    git commit --allow-empty -m "Reset remote to empty (temporary branch)" | Out-Null
    git push --force $RemoteUrl "${tmpBranch}:${Branch}"
    if ($LASTEXITCODE -ne 0) { Abort "Failed to push empty branch to remote." }
    # return to the original branch
    git checkout -f $Branch
    git branch -D $tmpBranch
    Write-Host "Remote branch '$Branch' reset to empty." -ForegroundColor Yellow
}

# Ensure remote is configured
Write-Host "Setting remote 'origin' to $RemoteUrl"
# remove existing origin if exists
git remote remove origin 2>$null
git remote add origin $RemoteUrl
if ($LASTEXITCODE -ne 0) { Abort "Failed to set remote origin." }

# Stage and commit local changes
Write-Host "Staging all changes..."
git add -A

# Commit
$hasChanges = (git status --porcelain) -ne ''
if ($hasChanges) {
    git commit -m "$CommitMessage"
    if ($LASTEXITCODE -ne 0) { Abort "git commit failed." }
} else {
    Write-Host "No changes to commit. Creating an empty commit to ensure a pushable state."
    git commit --allow-empty -m "$CommitMessage"
}

# Push
if ($ForcePush) {
    Write-Host "Force-pushing branch '$Branch' to remote '$RemoteUrl'..."
    git push --force origin "${Branch}:${Branch}"
} else {
    Write-Host "Pushing branch '$Branch' to remote '$RemoteUrl'..."
    git push origin "${Branch}:${Branch}"
}

if ($LASTEXITCODE -ne 0) { Abort "git push failed. Check authentication and remote access." }

Write-Host "Push complete." -ForegroundColor Green
Write-Host "If remote contains other branches you want removed, consider using --mirror or deleting them manually on the remote."