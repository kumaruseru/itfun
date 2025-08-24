# COWN Project Cleanup Script (PowerShell)
# Removes temporary files, old test results, and cache files

param(
    [string]$ProjectRoot = "",
    [switch]$DryRun = $false
)

function Write-ColorOutput($Message, $Color = "White") {
    Write-Host $Message -ForegroundColor $Color
}

function Get-ProjectSize($Path) {
    $files = Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue
    $totalSize = ($files | Measure-Object -Property Length -Sum).Sum
    $fileCount = $files.Count
    
    # Convert to human readable
    $units = @("B", "KB", "MB", "GB", "TB")
    $unitIndex = 0
    $size = $totalSize
    
    while ($size -ge 1024 -and $unitIndex -lt $units.Length - 1) {
        $size = $size / 1024
        $unitIndex++
    }
    
    return @{
        Size = "{0:N1} {1}" -f $size, $units[$unitIndex]
        Files = $fileCount
    }
}

function Remove-ItemSafely($Path, $Description) {
    if (Test-Path $Path) {
        if ($DryRun) {
            Write-ColorOutput "   [DRY RUN] Would remove: $Path" "Yellow"
        } else {
            try {
                Remove-Item $Path -Recurse -Force
                Write-ColorOutput "   📄 Removed: $Description" "Green"
                return $true
            } catch {
                Write-ColorOutput "   ❌ Failed to remove: $Path - $($_.Exception.Message)" "Red"
                return $false
            }
        }
    }
    return $false
}

function Clean-PythonCache($ProjectPath) {
    Write-ColorOutput "🧹 Cleaning Python cache files..." "Cyan"
    
    $patterns = @(
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".pytest_cache",
        ".mypy_cache"
    )
    
    $removedCount = 0
    
    foreach ($pattern in $patterns) {
        $items = Get-ChildItem -Path $ProjectPath -Recurse -Force -Name $pattern -ErrorAction SilentlyContinue
        foreach ($item in $items) {
            $fullPath = Join-Path $ProjectPath $item
            if (Remove-ItemSafely $fullPath "Python cache: $item") {
                $removedCount++
            }
        }
    }
    
    Write-ColorOutput "   ✅ Removed $removedCount Python cache items" "Green"
}

function Clean-TemporaryFiles($ProjectPath) {
    Write-ColorOutput "🧹 Cleaning temporary files..." "Cyan"
    
    $patterns = @(
        "*.tmp",
        "*.temp",
        "*.bak", 
        "*.old",
        "*~",
        ".DS_Store",
        "Thumbs.db"
    )
    
    $removedCount = 0
    
    foreach ($pattern in $patterns) {
        $items = Get-ChildItem -Path $ProjectPath -Recurse -Force -Name $pattern -ErrorAction SilentlyContinue
        foreach ($item in $items) {
            $fullPath = Join-Path $ProjectPath $item
            if (Remove-ItemSafely $fullPath "Temporary file: $item") {
                $removedCount++
            }
        }
    }
    
    Write-ColorOutput "   ✅ Removed $removedCount temporary files" "Green"
}

function Clean-QuantumResults($ProjectPath) {
    Write-ColorOutput "🧹 Cleaning old quantum test results..." "Cyan"
    
    $patterns = @(
        "advanced_qkd_demo_results_*.json",
        "quantum_results_*.json", 
        "cown_quantum_demo_results_*.json",
        "qkd_test_results_*.json",
        "quantum_benchmark_*.json"
    )
    
    # Keep files from last 24 hours
    $cutoffTime = (Get-Date).AddHours(-24)
    $removedCount = 0
    
    foreach ($pattern in $patterns) {
        $items = Get-ChildItem -Path $ProjectPath -Recurse -Force -Name $pattern -ErrorAction SilentlyContinue
        foreach ($item in $items) {
            $fullPath = Join-Path $ProjectPath $item
            $fileInfo = Get-Item $fullPath -ErrorAction SilentlyContinue
            
            if ($fileInfo -and $fileInfo.LastWriteTime -lt $cutoffTime) {
                if (Remove-ItemSafely $fullPath "Old quantum result: $item") {
                    $removedCount++
                }
            } elseif ($fileInfo) {
                Write-ColorOutput "   🔒 Keeping recent: $item" "Yellow"
            }
        }
    }
    
    Write-ColorOutput "   ✅ Removed $removedCount old result files" "Green"
}

function Clean-Logs($ProjectPath) {
    Write-ColorOutput "🧹 Cleaning old log files..." "Cyan"
    
    $patterns = @(
        "*.log"
    )
    
    # Keep logs from last 7 days
    $cutoffTime = (Get-Date).AddDays(-7)
    $removedCount = 0
    
    foreach ($pattern in $patterns) {
        $items = Get-ChildItem -Path $ProjectPath -Recurse -Force -Name $pattern -ErrorAction SilentlyContinue
        foreach ($item in $items) {
            $fullPath = Join-Path $ProjectPath $item
            $fileInfo = Get-Item $fullPath -ErrorAction SilentlyContinue
            
            if ($fileInfo -and $fileInfo.LastWriteTime -lt $cutoffTime) {
                if (Remove-ItemSafely $fullPath "Old log: $item") {
                    $removedCount++
                }
            } elseif ($fileInfo) {
                Write-ColorOutput "   🔒 Keeping recent log: $item" "Yellow"
            }
        }
    }
    
    Write-ColorOutput "   ✅ Removed $removedCount old log files" "Green"
}

function Clean-BuildArtifacts($ProjectPath) {
    Write-ColorOutput "🧹 Cleaning build artifacts..." "Cyan"
    
    $patterns = @(
        "dist",
        "build",
        "*.egg-info",
        "coverage.xml",
        ".coverage",
        "htmlcov"
    )
    
    $removedCount = 0
    
    foreach ($pattern in $patterns) {
        $items = Get-ChildItem -Path $ProjectPath -Recurse -Force -Name $pattern -ErrorAction SilentlyContinue
        foreach ($item in $items) {
            $fullPath = Join-Path $ProjectPath $item
            if (Remove-ItemSafely $fullPath "Build artifact: $item") {
                $removedCount++
            }
        }
    }
    
    Write-ColorOutput "   ✅ Removed $removedCount build artifacts" "Green"
}

# Main execution
Write-ColorOutput "🚀 Starting COWN Project Cleanup" "Magenta"
Write-ColorOutput ("=" * 50) "Magenta"

# Determine project root
if (-not $ProjectRoot) {
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
}

if (-not (Test-Path $ProjectRoot)) {
    Write-ColorOutput "❌ Project root not found: $ProjectRoot" "Red"
    exit 1
}

Write-ColorOutput "📁 Project root: $ProjectRoot" "White"

if ($DryRun) {
    Write-ColorOutput "⚠️  DRY RUN MODE - No files will be deleted" "Yellow"
}

# Get initial project size
$initialStats = Get-ProjectSize $ProjectRoot
Write-ColorOutput "📊 Initial project size: $($initialStats.Size) ($($initialStats.Files) files)" "White"
Write-ColorOutput ""

# Run cleanup operations
Clean-PythonCache $ProjectRoot
Write-ColorOutput ""

Clean-TemporaryFiles $ProjectRoot
Write-ColorOutput ""

Clean-QuantumResults $ProjectRoot
Write-ColorOutput ""

Clean-Logs $ProjectRoot
Write-ColorOutput ""

Clean-BuildArtifacts $ProjectRoot
Write-ColorOutput ""

# Get final project size
$finalStats = Get-ProjectSize $ProjectRoot
Write-ColorOutput "📊 Cleanup Summary:" "White"
Write-ColorOutput "   📁 Final project size: $($finalStats.Size) ($($finalStats.Files) files)" "White"
Write-ColorOutput ""

if ($DryRun) {
    Write-ColorOutput "🎉 Dry run completed! Run without -DryRun to actually clean files." "Green"
} else {
    Write-ColorOutput "🎉 Cleanup completed successfully!" "Green"
}

Write-ColorOutput "💡 Tip: Run this script regularly to keep your project clean" "Cyan"
