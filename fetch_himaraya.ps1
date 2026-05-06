# ヒマラヤ楽天店 キャンプ用品 全データ取得スクリプト
$APP_ID = "9b07f603-1b86-48ad-ab6b-d08005640ac6"
$KEY    = "pk_GYZOQiIkgr4viwkEy43XE78LIPlm2dhw0bZ23VSePE7"

$allItems = @()

for ($page = 1; $page -le 19; $page++) {
    $url = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260401?format=json&keyword=%E3%82%AD%E3%83%A3%E3%83%B3%E3%83%97&genreId=0&shopCode=himaraya&page=$page&applicationId=$APP_ID&accessKey=$KEY"
    try {
        $res = Invoke-RestMethod -Uri $url -Method Get
        if (-not $res.Items -or $res.Items.Count -eq 0) {
            Write-Host "データなし。終了。"
            break
        }
        foreach ($item in $res.Items) {
            $i = $item.Item
            $allItems += [PSCustomObject]@{
                name      = $i.itemName
                price     = $i.itemPrice
                code      = $i.itemCode
                pointRate = $i.pointRate
            }
        }
        Write-Host "$page ページ完了（計 $($allItems.Count) 件）"
        Start-Sleep -Milliseconds 400
    } catch {
        Write-Host "エラー (page $page): $_"
        break
    }
}

$outPath = [System.IO.Path]::Combine($env:USERPROFILE, "Desktop", "rakuten_himaraya.json")
$allItems | ConvertTo-Json | Out-File -FilePath $outPath -Encoding UTF8
Write-Host ""
Write-Host "完了！ $($allItems.Count) 件をデスクトップに保存しました。"
Write-Host "ファイル名: rakuten_himaraya.json"
Write-Host "このウィンドウを閉じる前に、ファイルをClaudeに貼り付けてください。"
Read-Host "Enterキーで閉じる"
