#Get-ChildItem C:\Users\*\Appdata\Roaming\1C\1cv8\2fc1e320-9017-4f3a-94bc-039340b2f535 | Remove-Item -Force –Recurse
#Remove-Item C:\Users\*\Appdata\Roaming\1C\1cv8\2fc1e320-9017-4f3a-94bc-039340b2f535 -Force -Recurse
$Logfile = "C:\Windows\1c_clean_cache.log"
$trashes = Get-ChildItem C:\Users\*\Appdata\Roaming\1C\1cv8\????????-????-????-????-????????????


foreach ($trash in $trashes)
{
Try {
        Remove-Item $trash  -Force -Recurse -ErrorAction Stop
    }


Catch  
    {
	### To know error name
	###$_.GetType().FullName
    #$_ | Out-File $Logfile -Append
	$Time=Get-Date
    $ErrorMessage = $_.Exception.Message
    #$FailedItem = $_.Exception.ItemName
	"$Time $trash $ErrorMessage" | out-file $Logfile  -append
	#Write-Host $_.CategoryInfo.Reason
    #Write-Host $_.Exception.ItemName
    }
}
