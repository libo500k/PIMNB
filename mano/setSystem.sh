
#/bin/bash
source token.sh

a=`curl -X PUT -H 'Content-Type:application/json' -H 'charset:UTF-8' -H "X-Auth-Token: ${token}"  -v -k  'https://127.0.0.1:9141/v1/pimCm/Systems/Set/EA2F88D9E18E11E6A098CB63F9A226BC' -d '{ "CpuMode" : { "SuperThreadFlag" : "Open", "IntelVtFlag" : "Open" }} '`

echo $a


#{ 
#        "CpuMode" : { 
#                "SuperThreadFlag" : "Open", 
#                "IntelVtFlag" : "Open" 
#        }, 
#        "NicMode" : { 
#                "PxeFlag" : "Close", 
#                "SR-IOVFlag" : "Close" 
#        }, 
#        "DiskMode" : { 
#                "RaidFlag" : "1" 
#        }, 
#        "BootMode" : { 
#                "BootFlag" : "UEFI+Legacy" 
#        }, 
#        "PowerMode" : { 
#                "DormancyFlag" : "Close" 
#        } 
#} 

