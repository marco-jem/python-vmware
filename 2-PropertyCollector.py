# Marco Tosato
# 2013/01/16 17:21
#
# Sample program to access vSphere v4.1 using Python and Suds,
# the main goal was retrive Virtual Machines properties but
# it tourned out that you can only go as far as retriving the
# properties of the vmFolder because vmFolder only contains
# MoRef to the VMs.
# To youse the MoRef to the Virtual Machines you need to use a
# ContainerView
#
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
print "Login Time: {0}".format( userSession.loginTime )

# Obtain a MoRef to the root folder
rootFolder_MoRef = serviceContent.rootFolder


# # # # # # # # # # # # # # #
# Objects selection setup:  #

# Datacenter to datastoreFolder, hostFolder, networkFolder, vmFolder
tsDatacenter_to_datastoreFolder = client.factory.create('ns0:TraversalSpec')
tsDatacenter_to_datastoreFolder.type = 'Datacenter'
tsDatacenter_to_datastoreFolder.path = 'datastoreFolder'

tsDatacenter_to_hostFolder = client.factory.create('ns0:TraversalSpec')
tsDatacenter_to_hostFolder.type = 'Datacenter'
tsDatacenter_to_hostFolder.path = 'hostFolder'

tsDatacenter_to_networkFolder = client.factory.create('ns0:TraversalSpec')
tsDatacenter_to_networkFolder.type = 'Datacenter'
tsDatacenter_to_networkFolder.path = 'networkFolder'

tsDatacenter_to_vmFolder = client.factory.create('ns0:TraversalSpec')
tsDatacenter_to_vmFolder.type = 'Datacenter'
tsDatacenter_to_vmFolder.path = 'vmFolder'
tsDatacenter_to_vmFolder.skip = False

# Folder to childEntity (using recursion)
ssDigFolder = client.factory.create('ns0:SelectionSpec')
ssDigFolder.name = 'tsDigFolder'

tsDigFolder = client.factory.create('ns0:TraversalSpec')
tsDigFolder.name = 'tsDigFolder'
tsDigFolder.skip = False
tsDigFolder.type = 'Folder'
tsDigFolder.path = 'childEntity'
tsDigFolder.selectSet = [ ssDigFolder,
			  tsDatacenter_to_datastoreFolder,
			  tsDatacenter_to_hostFolder,
			  tsDatacenter_to_networkFolder,
			  tsDatacenter_to_vmFolder,
			]

# ObjetSpec instance: this object specify the starting point for the traversal
# and ore or more SelectionSpec (or subclasses as TraversalSpec) that describes
# how to traverse the inventory
objectSpec = client.factory.create('ns0:ObjectSpec')
objectSpec.obj = rootFolder_MoRef
objectSpec.skip = False
objectSpec.selectSet = [tsDigFolder]


# # # # # # # # # # # # # # #
# Property retrival setup:  #

# Properties of Folders
psFolder = client.factory.create('ns0:PropertySpec')
psFolder.type = 'Folder'
psFolder.pathSet = ['name','parent','childEntity']

# Properties of Datacenters
psDC = client.factory.create('ns0:PropertySpec')
psDC.type = 'Datacenter'
psDC.pathSet = ['name', 'parent']

# # # # # # # # # # # # #
# Build the FilterSpec  #
propertyFilter = client.factory.create('ns0:PropertyFilterSpec')
propertyFilter.propSet = [psFolder,psDC,psVM] # Retrive these properties....
propertyFilter.objectSet = [objectSpec] # ....from these objects

# # # # # # # # # # # # # # # #
# Go with PropertyCollector!  #
propertyCollector_MoRef = serviceContent.propertyCollector
digRes = serviceConnection.RetrievePropertiesEx(propertyCollector_MoRef, [propertyFilter])

# Print the result
print digRes
