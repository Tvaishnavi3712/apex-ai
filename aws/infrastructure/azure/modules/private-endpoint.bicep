// Reusable private endpoint + private DNS zone group.
// One module call per PaaS service that must be reached privately.

param name string
param location string
param subnetId string
param targetResourceId string
@description('Sub-resource group id, e.g. blob | Sql | vault | account')
param groupId string
param dnsZoneName string

resource pe 'Microsoft.Network/privateEndpoints@2023-11-01' = {
  name: name
  location: location
  properties: {
    subnet: { id: subnetId }
    privateLinkServiceConnections: [
      {
        name: '${name}-conn'
        properties: {
          privateLinkServiceId: targetResourceId
          groupIds: [ groupId ]
        }
      }
    ]
  }
}

// Binds the PE's private IP into the private DNS zone so the normal
// public hostname resolves to the private address inside the VNet.
resource dnsGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-11-01' = {
  parent: pe
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: replace(dnsZoneName, '.', '-')
        properties: {
          privateDnsZoneId: resourceId('Microsoft.Network/privateDnsZones', dnsZoneName)
        }
      }
    ]
  }
}

output privateEndpointId string = pe.id
output privateIp string = pe.properties.customDnsConfigs[0].ipAddresses[0]
