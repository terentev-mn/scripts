Import-Module ActiveDirectory
$dom="utsrus.com"
#$users = Get-ADUser -SearchBase 'ou=test-install,dc=corp,dc=utsrus,dc=com' -Filter *  -Properties *|Select-Object name,mail,samaccountname,surname,givenname
$users = Get-ADUser -Filter *  -Properties *|Select-Object name,mail,samaccountname,surname,givenname
foreach ($user in $users)
{
    #$email = $user.givenname +"." + $user.surname + "@" + "$dom"
	#Set-ADUser -Identity $user.samaccountname -EmailAddress $email
	#Write-Host $t
	if (-Not ($user.mail)) {
	$email = $user.givenname +"." + $user.surname + "@" + "$dom"
	Set-ADUser -Identity $user.samaccountname -EmailAddress $email
	Write-Host $user.name,$user.mail
	}
}
