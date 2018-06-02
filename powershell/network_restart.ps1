# Attention !!!
# this script will working only whith PowerShell 3 or higher

# get all methods of netadapter
# gcm -Noun netadapter | select name, modulename
# restart-netadapter "*"

$Computer = "10.0.0.1"
$Logfile = "C:\Windows\network_restart.log"
$i = 0
function Ping {
    #enable-netadapter "*"
    #"Test i = $i" | out-file $Logfile  -append
    $PingRequest = Test-Connection -ComputerName $Computer -Count 3 -Quiet
    if ($PingRequest -eq $false) {
        restart-netadapter "*"
        $Time=Get-Date
        "$Time Shit happens. Restarting network adapters" | out-file $Logfile  -append
        }
}
try {
do {
    $i = $i + 20
    Ping
    sleep 20
    }
while($i -le 270)
}
catch {
enable-netadapter "*"
}
