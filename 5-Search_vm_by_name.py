# Marco Tosato
# 2013/01/16 17:21
#
# Sample program to access vSphere v4.1 using Python and Suds,
# the main goal is to retrieve the properties of a signle VM,
# to do this we need to create a ObjectSpec object whom obj property
# is set to a MoRef to the virtual machine of interest.
# 
# The steps we need to take are as follow
#
# 1) Get the MoRef to the VM by using the SearchIndex folder and
#    specifying the path to the VM 'ha-datacenter/vm/Intranet (2)'
#
# 2) create the ObjectSpec putting the VM MoRef as the obj property
#
# 3) Create the PropertySpec objects and the PropertyFilterSpec Object
#    as needed
#
# 4) Call the RetrievePropertiesEx() method of the PropertyCollector object
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
psVM.pathSet = ['name','config.uuid','config.files','layout','layoutEx','rootSnapshot','snapshot',]

# # # # # # # # # # # # #
# Build the FilterSpec  #
propertyFilter = client.factory.create('ns0:PropertyFilterSpec')
propertyFilter.propSet = [psVM,] # Retrive these properties....
propertyFilter.objectSet = [objectSpec,] # ....from these objects

# # # # # # # # # # # # # # # #
# Go with PropertyCollector!  #
propertyCollector = serviceContent.propertyCollector
digRes = serviceConnection.RetrievePropertiesEx(propertyCollector, [propertyFilter])

# Print the result
print digRes
