#gr-spacebase project github.com/wirrell/gr-spacebase

"""Holds the channels lists for the three chosen testing environments."""


def Durham():
    """UHF environment info for Durham City DH1."""
    #Pontop Pike
    primary_chans = ['33', '34', '49', '50', '54', '55', '56', '58', '59']
    #Bilsdale, Fenham and Durham Relay
    secondary_chans = ['21', '22', '23', '24', '26', '27', '29', '40', '41',
                       '44', '47']
    unocc_chans = [str(x) for x in range(21, 61)]
    for k in primary_chans:
        unocc_chans.remove(k)
    for j in secondary_chans:
        unocc_chans.remove(j)
    unocc_chans.remove('36') #radar
    unocc_chans.remove('38') #PMSE
    return [primary_chans, secondary_chans, unocc_chans]

def MetroCentre():
    """UHF environment info for Gateshead MetroCentre NE11."""
    #Fenham
    primary_chans = ['21', '22', '24', '25', '27', '28', '31', '37']
    #Pontop Pike
    secondary_chans = ['33', '34', '49', '50', '54', '55', '56', '58', '59']

    unocc_chans = [str(x) for x in range(21, 61)]
    for k in primary_chans:
        unocc_chans.remove(k)
    for j in secondary_chans:
        unocc_chans.remove(j)
    unocc_chans.remove('36') #radar
    unocc_chans.remove('38') #PMSE
    return [primary_chans, secondary_chans, unocc_chans]

def Consett():
    """UHF environment info for Consett town centre DH8."""
    #Pontop Pike
    primary_chans = ['33', '34', '49', '50', '54', '55', '56', '58', '59']
    #Bilsdale
    secondary_chans = ['23', '26', '29', '40', '43', '46']

    unocc_chans = [str(x) for x in range(21, 61)]
    for k in primary_chans:
        unocc_chans.remove(k)
    for j in secondary_chans:
        unocc_chans.remove(j)
    unocc_chans.remove('36') #radar
    unocc_chans.remove('38') #PMSE
    return [primary_chans, secondary_chans, unocc_chans]
    
