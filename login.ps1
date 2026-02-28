$credential = Get-Content "C:\Users\Administrator\.openclaw\workspace\projects\iraq-website-business\credentials.txt"
$email = $credential[0]
$password = $credential[1]

Write-Host "Email: $email"

# Create expect-like script
$expectScript = @"
spawn surge login
expect "email:"
send "$email\r"
expect "password:"
send "$password\r"
expect eof
"@

$expectScript | Out-File -FilePath "C:\Users\Administrator\.openclaw\workspace\projects\iraq-website-business\login.exp" -Encoding ascii
