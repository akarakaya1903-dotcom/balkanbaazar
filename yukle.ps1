# Tum degisiklikleri tek komutla GitHub'a yukler (migrasyon + git add/commit/push).
# Kullanim (proje klasorunde):   .\yukle.ps1 "ne degisti"
# Calismazsa once:   Set-ExecutionPolicy -Scope Process Bypass
param([string]$Mesaj = "guncelleme")

$ErrorActionPreference = "Continue"
$py = if (Test-Path ".\venv\Scripts\python.exe") { ".\venv\Scripts\python.exe" } else { "python" }

function Adim($t) { Write-Host ""; Write-Host ">> $t" -ForegroundColor Cyan }
function Hata($t) { Write-Host ""; Write-Host "HATA: $t" -ForegroundColor Red; exit 1 }

Adim "1/5 Migrasyon dosyalari olusturuluyor"
& $py manage.py makemigrations market
if ($LASTEXITCODE -ne 0) { Hata "makemigrations basarisiz. Yukaridaki hatayi bana gonder." }

Adim "2/5 Veritabani guncelleniyor (yerel)"
& $py manage.py migrate
if ($LASTEXITCODE -ne 0) { Hata "migrate basarisiz. Yukaridaki hatayi bana gonder." }

Adim "3/5 Dosyalar ekleniyor"
git add .
if ($LASTEXITCODE -ne 0) { Hata "git add basarisiz." }

Adim "4/5 Kayit (commit) olusturuluyor"
$degisiklik = git status --porcelain
if ($degisiklik) {
    git commit -m "$Mesaj"
    if ($LASTEXITCODE -ne 0) { Hata "git commit basarisiz." }
} else {
    Write-Host "Yeni degisiklik yok, commit atlandi."
}

Adim "5/5 GitHub'a gonderiliyor"
git push
if ($LASTEXITCODE -ne 0) { Hata "git push basarisiz. Yukaridaki hatayi bana gonder." }

Write-Host ""
Write-Host "TAMAM. Simdi sunucuda su tek komutu calistir:" -ForegroundColor Green
Write-Host "    bash /var/www/balkanbaazar/deploy/update.sh" -ForegroundColor Yellow
