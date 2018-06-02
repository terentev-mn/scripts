# Check 'robot' user logged in console
$a = "robot"
$Test = query user /server:$SERVER | select-string $a

Try {
	$b = $Test.ToString().Substring(1,11)
	if ($b.equals($a)) {
			Write-Host "OK"
			exit 0
	}
}
Catch  
    {
	Write-Host "$a not logged"
	exit 2
	}
