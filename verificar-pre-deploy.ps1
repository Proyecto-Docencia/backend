# Script de verificacion y limpieza para despliegue
# Ejecutar antes de desplegar a Cloud Run

Write-Host "`n=== VERIFICACION PRE-DESPLIEGUE - Backend Django ===" -ForegroundColor Cyan
Write-Host ""

$errores = 0
$warnings = 0

# 1. Verificar que estamos en la carpeta correcta
Write-Host "[1/8] Verificando carpeta actual..." -ForegroundColor Yellow
if ((Test-Path "Dockerfile") -and (Test-Path "src")) {
    Write-Host "  OK: Carpeta correcta" -ForegroundColor Green
} else {
    Write-Host "  ERROR: No estas en la carpeta backend/" -ForegroundColor Red
    exit 1
}

# 2. Limpiar archivos __pycache__
Write-Host "`n[2/8] Limpiando archivos cache de Python..." -ForegroundColor Yellow
$pycacheCount = (Get-ChildItem -Path "src" -Recurse -Force -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | Measure-Object).Count
if ($pycacheCount -gt 0) {
    Get-ChildItem -Path "src" -Recurse -Force -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
    Write-Host "  OK: Eliminados $pycacheCount carpetas __pycache__" -ForegroundColor Green
} else {
    Write-Host "  OK: No hay cache para limpiar" -ForegroundColor Green
}

Get-ChildItem -Path "src" -Recurse -Force -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force
Write-Host "  OK: Archivos .pyc eliminados" -ForegroundColor Green

# 3. Verificar archivos .env
Write-Host "`n[3/8] Verificando archivos .env..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  ADVERTENCIA: Archivo .env encontrado (no se subira a Cloud Run)" -ForegroundColor Yellow
    $warnings++
} else {
    Write-Host "  OK: No hay archivo .env" -ForegroundColor Green
}

if (Test-Path ".env.example") {
    Write-Host "  OK: .env.example existe" -ForegroundColor Green
} else {
    Write-Host "  ADVERTENCIA: No existe .env.example" -ForegroundColor Yellow
    $warnings++
}

# 4. Verificar archivos criticos
Write-Host "`n[4/8] Verificando archivos criticos..." -ForegroundColor Yellow
$archivos_criticos = @(
    "Dockerfile",
    "entrypoint.sh",
    "wait_for_db.sh",
    "requirements.txt",
    "src/manage.py",
    "src/config/settings.py"
)

foreach ($archivo in $archivos_criticos) {
    if (Test-Path $archivo) {
        Write-Host "  OK: $archivo" -ForegroundColor Green
    } else {
        Write-Host "  FALTA: $archivo" -ForegroundColor Red
        $errores++
    }
}

# 5. Verificar formato de archivos .sh (LF vs CRLF)
Write-Host "`n[5/8] Verificando formato de scripts..." -ForegroundColor Yellow
$scripts = @("entrypoint.sh", "wait_for_db.sh", "deploy.sh")
foreach ($script in $scripts) {
    if (Test-Path $script) {
        $content = Get-Content $script -Raw
        if ($content -match "`r`n") {
            Write-Host "  Convirtiendo $script de CRLF a LF..." -ForegroundColor Yellow
            $content = $content -replace "`r`n", "`n"
            [System.IO.File]::WriteAllText((Resolve-Path $script).Path, $content, [System.Text.UTF8Encoding]::new($false))
            Write-Host "  OK: $script convertido a LF" -ForegroundColor Green
        } else {
            Write-Host "  OK: $script tiene LF (correcto)" -ForegroundColor Green
        }
    }
}

# 6. Verificar .gitignore y .gcloudignore
Write-Host "`n[6/8] Verificando archivos de ignore..." -ForegroundColor Yellow
if (Test-Path ".gitignore") {
    Write-Host "  OK: .gitignore existe" -ForegroundColor Green
} else {
    Write-Host "  ADVERTENCIA: No existe .gitignore" -ForegroundColor Yellow
    $warnings++
}

if (Test-Path ".gcloudignore") {
    Write-Host "  OK: .gcloudignore existe" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Falta .gcloudignore" -ForegroundColor Red
    $errores++
}

# 7. Verificar tamaño del proyecto
Write-Host "`n[7/8] Verificando tamanio del proyecto..." -ForegroundColor Yellow
$size = (Get-ChildItem -Recurse -File -Exclude "__pycache__","*.pyc" | Measure-Object -Property Length -Sum).Sum
$sizeMB = [math]::Round($size/1MB, 2)
Write-Host "  INFO: Tamanio total: $sizeMB MB" -ForegroundColor Cyan
if ($sizeMB -gt 100) {
    Write-Host "  ADVERTENCIA: Proyecto muy grande" -ForegroundColor Yellow
    $warnings++
} else {
    Write-Host "  OK: Tamanio apropiado para despliegue" -ForegroundColor Green
}

# 8. Verificar configuracion en settings.py
Write-Host "`n[8/8] Verificando configuracion en settings.py..." -ForegroundColor Yellow
$settings = Get-Content "src/config/settings.py" -Raw
if ($settings -match "DB_PORT.*3306") {
    Write-Host "  OK: Puerto BD correcto (3306)" -ForegroundColor Green
} else {
    Write-Host "  ADVERTENCIA: Puerto BD no es 3306" -ForegroundColor Yellow
    $warnings++
}

# Resumen final
Write-Host "`n=== RESUMEN DE VERIFICACION ===" -ForegroundColor Cyan

if (($errores -eq 0) -and ($warnings -eq 0)) {
    Write-Host "`n  TODO PERFECTO - Listo para desplegar" -ForegroundColor Green
    Write-Host "`n  Ejecuta: .\deploy-cloudrun.ps1" -ForegroundColor Cyan
    exit 0
} elseif ($errores -eq 0) {
    Write-Host "`n  $warnings advertencia(s) encontrada(s)" -ForegroundColor Yellow
    Write-Host "  Puedes continuar con el despliegue" -ForegroundColor Green
    Write-Host "`n  Ejecuta: .\deploy-cloudrun.ps1" -ForegroundColor Cyan
    exit 0
} else {
    Write-Host "`n  $errores error(es) critico(s)" -ForegroundColor Red
    Write-Host "  $warnings advertencia(s)" -ForegroundColor Yellow
    Write-Host "`n  Corrige los errores antes de desplegar" -ForegroundColor Red
    exit 1
}
