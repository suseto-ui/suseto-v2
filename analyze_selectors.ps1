$root = Get-Item .
# Collect template IDs and classes
$templateIds = @{}
$templateClasses = @{}
$allIds = @()
$allClasses = @()
Get-ChildItem -Path .\templates -Filter *.html -Recurse | ForEach-Object {
    $path = $_.FullName
    $text = Get-Content -Raw $path
    $ids = [regex]::Matches($text, 'id=["\']([^"\']+)["\']') | ForEach-Object { $_.Groups[1].Value }
    $classes = [regex]::Matches($text, 'class=["\']([^"\']+)["\']') | ForEach-Object { $_.Groups[1].Value -split '\s+' } | ForEach-Object { $_ }
    $templateIds[$path] = $ids
    $templateClasses[$path] = $classes
    $allIds += $ids
    $allClasses += $classes
}
$allIds = $allIds | Sort-Object -Unique
$allClasses = $allClasses | Sort-Object -Unique

# Find which templates reference which JS files
$jsReferences = @{}
Get-ChildItem -Path .\templates -Filter *.html -Recurse | ForEach-Object {
    $text = Get-Content -Raw $_.FullName
    $matches = [regex]::Matches($text, "url_for\('static'\s*,\s*filename\s*=\s*'js/([^']+)'\)")
    foreach($m in $matches){
        $js = $m.Groups[1].Value
        if(-not $jsReferences.ContainsKey($js)) { $jsReferences[$js] = @() }
        $jsReferences[$js] += $_.FullName
    }
}

# Analyze JS files for selectors
function Normalize-Selector($sel){
    if($sel -match '^#([A-Za-z0-9_\-]+)') { return @{type='id'; name=$matches[1] } }
    if($sel -match '^\.([A-Za-z0-9_\-]+)') { return @{type='class'; name=$matches[1] } }
    if($sel -match '^\[([^\]]+)\]') { return @{type='attr'; name=$matches[1] } }
    if($sel -match '^([A-Za-z0-9_\-]+)(\[.+\])') { return @{type='class'; name=$matches[1] } }
    return @{type='other'; name=$sel}
}

$report = @()
Get-ChildItem -Path .\static\js -Filter *.js -Recurse | ForEach-Object {
    $file = $_.FullName
    $text = Get-Content -Raw $file
    $selectors = @()
    # getElementById
    $matches = [regex]::Matches($text, "getElementById\([\"']([^\"']+)[\"']\)") | ForEach-Object { $_.Groups[1].Value }
    foreach($m in $matches){ $selectors += @{raw=$m; kind='id'; norm=Normalize-Selector('#'+$m)} }
    # querySelector / querySelectorAll
    $matches2 = [regex]::Matches($text, "querySelector(All)?\([\"']([^\"']+)[\"']\)")
    foreach($mm in $matches2){ $s = $mm.Groups[2].Value; $selectors += @{raw=$s; kind='css'; norm=Normalize-Selector($s)} }
    $selectors = $selectors | Sort-Object -Property raw -Unique

    $selResults = @()
    foreach($s in $selectors){
        $type = $s.norm.type
        $name = $s.norm.name
        $status = 'unknown'
        if($type -eq 'id'){
            $status = (if($allIds -contains $name) { 'present' } else { 'MISSING'})
        } elseif($type -eq 'class'){
            $status = (if($allClasses -contains $name) { 'present' } else { 'MISSING'})
        } elseif($type -eq 'attr'){
            $attr = $name
            $attrFound = $false
            foreach($t in $templateIds.Keys){ if($templateClasses[$t] -and ($templateClasses[$t] -join ' ') -match $attr){ $attrFound = $true; break } }
            $status = (if($attrFound) { 'present-ish' } else { 'unknown' })
        } else { $status = 'unknown' }
        $selResults += [PSCustomObject]@{selector=$s.raw; type=$type; name=$name; status=$status}
    }

    $refs = @()
    $baseName = Split-Path $file -Leaf
    if($jsReferences.ContainsKey($baseName)) { $refs = $jsReferences[$baseName] } else { $refs = @() }

    $report += [PSCustomObject]@{
        js = $baseName
        path = $file
        referenced_in = $refs
        selectors = $selResults
    }
}

# Print summary
Write-Output "JS files analyzed: $($report.Count)"
$missingOverall = @()
foreach($r in $report){
    Write-Output "\n--- $($r.js) ---"
    if($r.referenced_in.Count){ Write-Output "Referenced in templates:"; $r.referenced_in | ForEach-Object { Write-Output "  - $_" } } else { Write-Output "Not referenced in templates (might be included globally)" }
    Write-Output "Selectors used:";
    foreach($s in $r.selectors){ Write-Output "  - [$($s.type)] $($s.selector) => $($s.status)"; if($s.status -eq 'MISSING'){ $missingOverall += "$($r.js): $($s.selector)" } }
}

Write-Output "\n=== Summary of missing selectors ==="
if($missingOverall.Count -eq 0){ Write-Output 'No missing ID/class selectors detected across templates.' } else { $missingOverall | ForEach-Object { Write-Output "- $_" } }
