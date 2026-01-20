# Download script for Tyler Sorensen's papers from UCSC
# Run this script from the website directory

$baseUrl = "https://users.soe.ucsc.edu/~tsorensen/files/"
$outputDir = "files"

# Create files directory if it doesn't exist
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

# PDF files to download (papers and theses)
$pdfFiles = @(
    "asplos2015.pdf",
    "asplos_poster2015.pdf",
    "bsthesis.pdf",
    "concur2018.pdf",
    "fse2017.pdf",
    "fse_poster2017.pdf",
    "fse_slides2017.pdf",
    "iccad20.pdf",
    "iccad_slides2020.pdf",
    "ics2013.pdf",
    "ics_poster2013.pdf",
    "ics_preprint2013.pdf",
    "iiswc2019.pdf",
    "iiswc_slides2019.pdf",
    "ispass2020.pdf",
    "ispass2023.pdf",
    "ISSTA2023.pdf",
    "iwocl2016.pdf",
    "iwocl2019.pdf",
    "iwocl_slides2016.pdf",
    "iwocl_slides2019.pdf",
    "msthesis.pdf",
    "oopsla2016.pdf",
    "oopsla2020.pdf",
    "oopsla2021a.pdf",
    "oopsla2021b.pdf",
    "phdthesis.pdf",
    "pldi2016.pdf",
    "pldi_slides2016.pdf",
    "rtas2020.pdf",
    "taco2021.pdf",
    "tinytocs2015.pdf",
    "BSides.pdf",
    "cv.pdf"
)

Write-Host "Downloading PDF files from UCSC..." -ForegroundColor Cyan
Write-Host ""

$successCount = 0
$failCount = 0

foreach ($file in $pdfFiles) {
    $url = "$baseUrl$file"
    $outputPath = Join-Path $outputDir $file
    
    Write-Host "Downloading: $file ... " -NoNewline
    
    try {
        Invoke-WebRequest -Uri $url -OutFile $outputPath -UseBasicParsing
        Write-Host "OK" -ForegroundColor Green
        $successCount++
    }
    catch {
        Write-Host "FAILED" -ForegroundColor Red
        $failCount++
    }
}

# Also download CV to root directory
Write-Host ""
Write-Host "Downloading CV to root directory... " -NoNewline
try {
    Invoke-WebRequest -Uri "${baseUrl}cv.pdf" -OutFile "cv.pdf" -UseBasicParsing
    Write-Host "OK" -ForegroundColor Green
}
catch {
    Write-Host "FAILED" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Download complete!" -ForegroundColor Cyan
Write-Host "  Success: $successCount files" -ForegroundColor Green
Write-Host "  Failed:  $failCount files" -ForegroundColor $(if ($failCount -gt 0) { "Red" } else { "Green" })
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Files downloaded to: $outputDir\" -ForegroundColor Yellow
Write-Host ""
Write-Host "NOTE: You may need to rename some files to match the website links:" -ForegroundColor Yellow
Write-Host "  - ISSTA2023.pdf -> gpuharbor2023.pdf" -ForegroundColor Gray
Write-Host "  - ispass2023.pdf -> redwood2023.pdf" -ForegroundColor Gray
Write-Host "  - BSides.pdf -> leftoverlocals2024_slides.pdf" -ForegroundColor Gray
Write-Host "  - iccad20.pdf -> iccad2020.pdf" -ForegroundColor Gray
Write-Host "  - iiswc_slides2019.pdf -> iiswc2019_slides.pdf" -ForegroundColor Gray
Write-Host ""
Write-Host "Still needed (download manually):" -ForegroundColor Yellow
Write-Host "  - leftoverlocals2024.pdf (from ArXiv)" -ForegroundColor Gray
Write-Host "  - mcmutants2023.pdf (from co-author site)" -ForegroundColor Gray
Write-Host "  - pldi2018.pdf (from co-author site)" -ForegroundColor Gray
Write-Host "  - popl2017.pdf (from co-author site)" -ForegroundColor Gray
Write-Host "  - bettertogether2025.pdf (IISWC 2025)" -ForegroundColor Gray
Write-Host "  - photo.jpg (your profile photo)" -ForegroundColor Gray
