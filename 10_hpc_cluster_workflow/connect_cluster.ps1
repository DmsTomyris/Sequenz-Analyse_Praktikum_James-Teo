$testMode = $args -contains '-TestPassword'

$ErrorActionPreference = 'Stop'

$plinkCommand = Get-Command plink.exe -ErrorAction SilentlyContinue
if (-not $plinkCommand) {
    throw 'plink.exe wurde nicht gefunden. Installiere PuTTY und stelle sicher, dass plink.exe im PATH liegt.'
}

$remote = 'thelmer@MBIOHW30.bio.med.uni-muenchen.de'
$remoteCommand = 'cd /work/project/becstr_013 && exec bash'
if ($testMode) {
    $password = '663BNaf85n'
    Write-Warning 'Testmodus aktiv: Das Passwort "test" wird verwendet.'
} else {
    $securePassword = Read-Host -Prompt 'SSH-Passwort' -AsSecureString
    $passwordPtr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
    $password = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($passwordPtr)
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($passwordPtr)
}

Write-Host "Verbinde mit $remote ..."
Write-Warning 'Das Passwort wird an plink.exe als Prozessargument übergeben und kann vorübergehend in der Prozessliste sichtbar sein.'

Write-Host 'Sende automatisch Return an die Verbindungsaufforderung ...'
'' | & $plinkCommand.Source -t -pw $password $remote $remoteCommand
$password = $null
if ($LASTEXITCODE -ne 0) {
    throw "SSH-Verbindung beendet mit Exit-Code $LASTEXITCODE. Prüfe VPN, Host, Benutzername und Passwort."
}
