# Marco Tosato
# 2013/01/16 17:21
#
# This is a sampla program released under GNU/GPL v3 Licence,
# you can find a copy of the lincence at:
#
# http://www.gnu.org/licenses/gpl.html
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# NB: MoRef = Managed Object Reference as defined in the vSphere API/SDK

# # # # # #
# Imports #
from suds.client import Client
from suds.sudsobject import Property

import datetime

import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.INFO)
logging.getLogger('suds.wsdl').setLevel(logging.INFO)

# From API Reference:
#
#   A vSphere API client application begins by connecting to a server
#   and obtaining a reference to the ServiceInstance. The client can
#   then use the RetrieveServiceContent method to gain access to the
#   various vSphere manager entities and to the root folder of the
#   inventory.
#
# so steps that we needs to take are as follow:
#
# 1) Connect to the server
# 2) Obtain a reference so the ServiceInstance managed object
# 3) Call the RetriveServiceContent() method which retrives the
#    properties of the service instance, that is the various vSphere
#    manager entities and the root folder of the inventory
# 4) Authenticate, ecc ecc
#
#
# NB: use type suds.sudsobjects.property instead of building a
#     ns0:ManagedObjectReference with client.factory.create(), for some
#     unknown reason this method does not works for me!!

location = 'https://esx3/sdk'
url = 'file:/home/marco/Documents/Projects/Python-WMware/vimWSDL/vimServiceEsx3.wsdl'

# Build Client object to access the SOAP service
client = Client(url)
client.set_options(location = location)

# Service Connection variable ....just to maintain the naming convention
# used in the document "Designing backup solutions for VMware vSphere"
serviceConnection = client.service

# Build reference to the Managed Object 'ServiceInstance'
serviceInstance_MoRef = Property('ServiceInstance')
serviceInstance_MoRef._type = 'ServiceInstance'

# Retrive the properties of ServiceInstance, this is done by calling the
# RetrieveServiceContent() method which returns a ServiceContent object
serviceContent = serviceConnection.RetrieveServiceContent(serviceInstance_MoRef)

# Build reference to the ManagedObject 'SessionManager'
sessionManager_MoRef = serviceContent.sessionManager

# Login to the service
userSession = serviceConnection.Login(sessionManager_MoRef, 'root', 'Passw0rd')

# Obtain a MoRef to the root folder
rootFolder_MoRef = serviceContent.rootFolder

# Obtain a MoRef reference to the SearchIndex object
searchI_MoRef = serviceContent.searchIndex

# Obtain a MoRef reference to the 'Intranet (2)' virtual machine
intranetVm_MoRef = serviceConnection.FindByInventoryPath(searchI_MoRef,'ha-datacenter/vm/Intranet (2)')

# ObjectSpec
objectSpec = client.factory.create('ns0:ObjectSpec')
objectSpec.obj = intranetVm_MoRef
objectSpec.skip = False # We want just this VM

# Properties of VMS
psVM = client.factory.create('ns0:PropertySpec')
psVM.type = 'VirtualMachine'
#psVM.all = True
#psVM.pathSet = ['name','config.uuid','config.files','capability','layout','layoutEx','rootSnapshot','snapshot',]
psVM.pathSet = ['config.hardware.device',]

# # # # # # # # # # # # #
# Build the FilterSpec  #
propertyFilter = client.factory.create('ns0:PropertyFilterSpec')
propertyFilter.propSet = [psVM,] # Retrive these properties....
propertyFilter.objectSet = [objectSpec,] # ....from these objects

# # # # # # # # # # # # # # # #
# Go with PropertyCollector!  #
propertyCollector = serviceContent.propertyCollector
digRes = serviceConnection.RetrievePropertiesEx(propertyCollector, [propertyFilter])

# Extract the "config.hardware.device" object
confHwDev = digRes.objects[0].propSet[0]

# Extract the array of virtual devices
virtualDevsArray = confHwDev.val.VirtualDevice

VirtualDiskClass = client.factory.create('ns0:VirtualDisk').__class__

vdiskSet = []

for vdev in virtualDevsArray:
    if isinstance(vdev,VirtualDiskClass): vdiskSet.append(vdev)
# end if

vmDisk = vdiskSet[0]

snapshotTask_MoRef = serviceConnection.CreateSnapshot_Task(intranetVm_MoRef,'Snap-Backup-' + str(datetime.datetime.now()),'',False,False)


# Logout
#serviceConnection.Login(sessionManager_MoRef)
