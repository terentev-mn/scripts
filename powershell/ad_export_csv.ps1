Import-Module ActiveDirectory
$global:ErrorActionPreference = "Continue"

$users = Get-ADUser -Filter  {(surname -like "*") -And (Enabled -eq 'True')} -Properties Name,OfficePhone,mobilephone,emailaddress,samaccountname | select Name,OfficePhone,mobilephone,emailaddress,samaccountname
#Write-Host $users
$users | Export-Csv -Path "c:\users\mks\desktop\intranet_export.csv" -Encoding UTF8 -noType
