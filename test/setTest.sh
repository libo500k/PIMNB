curl -d '{ "CpuMode" : { "SuperThreadFlag" : "Open", "IntelVtFlag" : "Open" }} '  -X PUT -v -k  -u USERID:Passw0rd  https://10.240.197.157/v1/pimCm/Systems/Set/EA2F88D9E18E11E6A098CB63F9A226BC



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

