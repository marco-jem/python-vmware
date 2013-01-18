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
url = location + '/vimService?wsdl'

client = Client(url)
client.set_options(location = location)


# Build reference to the Managed Object 'ServiceInstance'
serviceInstance = Property('ServiceInstance')
serviceInstance._type = 'ServiceInstance'

# Retrive the properties of ServiceInstance, this is done by calling the
# RetrieveServiceContent() method which returns a ServiceContent object
serviceContent = client.service.RetrieveServiceContent(serviceInstance)

# Build reference to the ManagedObject 'SessionManager'
sessionManager = serviceContent.sessionManager

userSession = client.service.Login(sessionManager, 'root', 'Passw0rd')

print "Login Time: {0}".format( userSession.loginTime )
