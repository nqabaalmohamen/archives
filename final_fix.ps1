$c = Get-Content index.html -Raw
$c = $c.Replace('https://goldfish-banked-valley.ngrok-free.dev', 'https://symphony-preference-nominated-playing.trycloudflare.com')
$c = $c.Replace('ngrok-skip-browser-warning', 'cf-skip-browser-warning')
$c = $c.Replace('V4.4', 'V4.5')
Set-Content -Path index.html -Value $c

$s = Get-Content archive_system/settings.py -Raw
$s = $s.Replace('https://goldfish-banked-valley.ngrok-free.dev', 'https://symphony-preference-nominated-playing.trycloudflare.com')
$s = $s.Replace('NGROK_TUNNEL_URL', 'CLOUDFLARE_TUNNEL_URL')
Set-Content -Path archive_system/settings.py -Value $s
