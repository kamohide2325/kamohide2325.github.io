@echo off
chcp 65001 > nul
echo ヒマラヤ楽天店 データ取得中...
powershell -ExecutionPolicy Bypass -Command ^
"$APP_ID='9b07f603-1b86-48ad-ab6b-d08005640ac6';" ^
"$KEY='pk_GYZOQiIkgr4viwkEy43XE78LIPlm2dhw0bZ23VSePE7';" ^
"$all=@();" ^
"for($p=1;$p-le19;$p++){" ^
"  $url='https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260401?format=json&keyword=%E3%82%AD%E3%83%A3%E3%83%B3%E3%83%97&genreId=0&shopCode=himaraya&page='+$p+'&applicationId='+$APP_ID+'&accessKey='+$KEY;" ^
"  try{" ^
"    $r=Invoke-RestMethod -Uri $url -Method Get;" ^
"    if(-not $r.Items -or $r.Items.Count-eq 0){break}" ^
"    foreach($i in $r.Items){$all+=[PSCustomObject]@{name=$i.Item.itemName;price=$i.Item.itemPrice;code=$i.Item.itemCode;pointRate=$i.Item.pointRate}}" ^
"    Write-Host ($p.ToString()+'ページ完了 計'+$all.Count+'件');" ^
"    Start-Sleep -Milliseconds 400" ^
"  }catch{Write-Host ('エラー page '+$p+': '+$_);break}" ^
"}" ^
"$out=[System.IO.Path]::Combine($env:USERPROFILE,'Desktop','rakuten_himaraya.json');" ^
"$all|ConvertTo-Json|Out-File -FilePath $out -Encoding UTF8;" ^
"Write-Host ('完了！デスクトップに保存しました: rakuten_himaraya.json 計'+$all.Count+'件')"
pause
