Import-Module ActiveDirectory
$global:ErrorActionPreference = "Continue"

$users = Import-Csv -Path c:\users\maks\desktop\intranet.csv
#name,officephone,mobilephone,emailaddress,samaccountname,comp
#Oвин Иван Андреевич,2111, ,ivan.ovin@stat.ru,OVIN,WS-SPB-051

foreach ($user in $users)
	{
	$name = $user.name
	$tel = $user.officephone
	$mobile = $user.mobilephone
	$email = $user.emailaddress
	$login = $user.samaccountname
	# if login is null then continue
	If(!$login){continue}
	# if var is not null do set..
	If($tel){Set-ADUser -Identity $user.samaccountname -OfficePhone $tel}
	If($mobile){Set-ADUser -Identity $user.samaccountname -MobilePhone $mobile}
	If($email){Set-ADUser -Identity $user.samaccountname -EmailAddress $email}
	Write-Host "Name: $name"
	Write-Host "Tel: $tel"
	Write-Host "Mobile: $mobile"
	Write-Host "Email: $email"
	Write-Host "Login: $login"
	Write-Host "-----------------"
}
