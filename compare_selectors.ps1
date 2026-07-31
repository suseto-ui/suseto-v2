$templatesPath = "C:\Users\Susetofu\.vscode\suseto-v2.worktrees\fix-nonfunctional-elements\templates"
$allIds = @()
$allClasses = @()
Get-ChildItem -Path $templatesPath -Filter *.html -Recurse | ForEach-Object {
    $text = Get-Content -Raw $_.FullName
    $idMatches = [regex]::Matches($text, "id=[""']([^""']+)[""']")
    foreach($m in $idMatches){ $allIds += $m.Groups[1].Value }
    $classMatches = [regex]::Matches($text, "class=[""']([^""']+)[""']")
    foreach($m in $classMatches){ $parts = $m.Groups[1].Value -split '\s+'; foreach($p in $parts){ $allClasses += $p } }
}
$allIds = $allIds | Sort-Object -Unique
$allClasses = $allClasses | Sort-Object -Unique

$jsPath = "C:\Users\Susetofu\.vscode\suseto-v2.worktrees\fix-nonfunctional-elements\static\js"
$issues = @()
Get-ChildItem -Path $jsPath -Filter *.js -Recurse | ForEach-Object {
    $file = $_.FullName
    $text = Get-Content -Raw $file
    $m1 = [regex]::Matches($text, "getElementById\([""']([^""']+)[""']\)")
    foreach($mm in $m1){ $id = $mm.Groups[1].Value; if(-not ($allIds -contains $id)){ $issues += [pscustomobject]@{js=($_.FullName); selector_type='id'; selector=$id} } }
    $m2 = [regex]::Matches($text, "querySelector(All)?\([""']([^""']+)[""']\)")
    foreach($mm in $m2){ $sel = $mm.Groups[2].Value; if($sel.StartsWith('#')){ $id = $sel.Substring(1); if(-not ($allIds -contains $id)){ $issues += [pscustomobject]@{js=($_.FullName); selector_type='id'; selector=$id} } }
                                                      elseif($sel.StartsWith('.')){ $cls = $sel.Substring(1); if(-not ($allClasses -contains $cls)){ $issues += [pscustomobject]@{js=($_.FullName); selector_type='class'; selector=$cls} } }
                                                      else { $issues += [pscustomobject]@{js=($_.FullName); selector_type='complex'; selector=$sel} }
    }
    $m3 = [regex]::Matches($text, "getElementsByClassName\([""']([^""']+)[""']\)")
    foreach($mm in $m3){ $cls = $mm.Groups[1].Value; if(-not ($allClasses -contains $cls)){ $issues += [pscustomobject]@{js=($_.FullName); selector_type='class'; selector=$cls} } }
    $m4 = [regex]::Matches($text, "getElementsByName\([""']([^""']+)[""']\)")
    foreach($mm in $m4){ $name = $mm.Groups[1].Value; $nameFound = $false
        foreach($t in (Get-ChildItem -Path $templatesPath -Filter *.html -Recurse)){
            $txt = Get-Content -Raw $t.FullName
            if($txt -match "name=[""']$name[""']"){ $nameFound = $true; break }
        }
        if(-not $nameFound){ $issues += [pscustomobject]@{js=($_.FullName); selector_type='name'; selector=$name} }
    }
}
$issues = $issues | Sort-Object js,selector_type,selector -Unique
Write-Output "Found $($issues.Count) potential issues (ids/classes not present or complex selectors):"
foreach($i in $issues){ Write-Output "- $([io.path]::GetFileName($i.js)) : [$($i.selector_type)] $($i.selector)" }
$outPath = "C:\Users\Susetofu\.vscode\suseto-v2.worktrees\fix-nonfunctional-elements\selector-issues.json"
$issues | ConvertTo-Json -Depth 4 | Set-Content $outPath -Encoding utf8
Write-Output "Detailed JSON written to: $outPath"
