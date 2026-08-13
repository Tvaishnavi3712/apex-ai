// =============================================================================
// APEX — Azure foundation (policy-compliant, private-only PaaS)
//
// Deploys into a CBTS sandbox subscription governed by the ALZ policy set
// `Deny-PublicPaaSEndpoints` (mg-alz-sandbox). That policy HARD-DENIES any PaaS
// resource with public network access, so every service here is created with
// publicNetworkAccess = Disabled and reached over Private Endpoints inside a VNet.
//
// Deploy:
//   az deployment group create -g manish-dev-apex-ai-coe \
//     --template-file main.bicep --parameters prefix=apexcoe
// =============================================================================

@description('Short lowercase prefix for resource names (3-10 chars).')
@minLength(3)
@maxLength(10)
param prefix string = 'apexcoe'

@description('Azure region. Must match the resource group region.')
param location string = resourceGroup().location

@description('VNet address space.')
param vnetAddressPrefix string = '10.42.0.0/16'

// ── naming ───────────────────────────────────────────────────────────────────
var vnetName    = '${prefix}-vnet'
var peSubnet    = 'snet-private-endpoints'
var appsSubnet  = 'snet-apps'
var storageName = '${prefix}stg'                 // storage names: lowercase, no dashes
var cosmosName  = '${prefix}-cosmos'
var kvName      = '${prefix}-kv'

// Cosmos containers — mirrors the 23 DynamoDB tables on AWS.
// Partition key follows how the code actually filters.
var cosmosContainers = [
  { name: 'playbooks',           pk: '/industry' }
  { name: 'blueprints',          pk: '/industry' }
  { name: 'agents',              pk: '/id' }
  { name: 'actions',             pk: '/id' }
  { name: 'work-items',          pk: '/id' }
  { name: 'sessions',            pk: '/id' }
  { name: 'audit-logs',          pk: '/id' }
  { name: 'agent-audit-log',     pk: '/id' }
  { name: 'review-queue',        pk: '/id' }
  { name: 'review-decisions',    pk: '/id' }
  { name: 'pipelines',           pk: '/id' }
  { name: 'simulator-scenarios', pk: '/scenario_id' }
  { name: 'predictive-events',   pk: '/id' }
  { name: 'suppliers',           pk: '/id' }
  { name: 'inventory',           pk: '/id' }
  { name: 'inventory-bom',       pk: '/id' }
  { name: 'purchase-orders',     pk: '/id' }
  { name: 'approved-vendors',    pk: '/id' }
  { name: 'carriers',            pk: '/id' }
  { name: 'job-requisitions',    pk: '/id' }
  { name: 'salary-bands',        pk: '/id' }
  { name: 'specifications',      pk: '/id' }
  { name: 'substitutes',         pk: '/id' }
]

// Blob containers — mirrors the 4 S3 buckets.
var blobContainers = [
  'documents-incoming'
  'documents-processed'
  'blueprints'
  'synthetic-data'
]

// ── network ──────────────────────────────────────────────────────────────────
resource vnet 'Microsoft.Network/virtualNetworks@2023-11-01' = {
  name: vnetName
  location: location
  properties: {
    addressSpace: { addressPrefixes: [ vnetAddressPrefix ] }
    subnets: [
      {
        name: peSubnet
        properties: {
          addressPrefix: '10.42.1.0/24'
          privateEndpointNetworkPolicies: 'Disabled'
        }
      }
      {
        // Container Apps requires a delegated /23 or larger.
        name: appsSubnet
        properties: {
          addressPrefix: '10.42.2.0/23'
          delegations: [
            {
              name: 'aca-delegation'
              properties: { serviceName: 'Microsoft.App/environments' }
            }
          ]
        }
      }
    ]
  }
}

// ── private DNS zones (required for private-endpoint name resolution) ────────
var dnsZoneNames = [
  'privatelink.blob.${environment().suffixes.storage}'
  'privatelink.documents.azure.com'
  'privatelink.vaultcore.azure.net'
]

resource dnsZones 'Microsoft.Network/privateDnsZones@2020-06-01' = [for z in dnsZoneNames: {
  name: z
  location: 'global'
}]

resource dnsLinks 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = [for (z, i) in dnsZoneNames: {
  name: '${z}/link-${vnetName}'
  location: 'global'
  properties: {
    registrationEnabled: false
    virtualNetwork: { id: vnet.id }
  }
  dependsOn: [ dnsZones ]
}]

// ── storage (private) ────────────────────────────────────────────────────────
resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageName
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    publicNetworkAccess: 'Disabled'      // required by policy
    allowBlobPublicAccess: false         // required by policy
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowSharedKeyAccess: false          // force Entra ID auth (managed identity)
    networkAcls: { defaultAction: 'Deny', bypass: 'AzureServices' }
  }
}

resource blobSvc 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  parent: storage
  name: 'default'
}

resource blobs 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = [for c in blobContainers: {
  parent: blobSvc
  name: c
  properties: { publicAccess: 'None' }
}]

// ── cosmos db (private, serverless) ──────────────────────────────────────────
resource cosmos 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' = {
  name: cosmosName
  location: location
  kind: 'GlobalDocumentDB'
  identity: { type: 'SystemAssigned' }
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [ { locationName: location, failoverPriority: 0, isZoneRedundant: false } ]
    capabilities: [ { name: 'EnableServerless' } ]
    publicNetworkAccess: 'Disabled'      // required by policy
    minimalTlsVersion: 'Tls12'
    disableLocalAuth: true               // force Entra ID / RBAC auth
    consistencyPolicy: { defaultConsistencyLevel: 'Session' }
  }
}

resource cosmosDb 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2024-05-15' = {
  parent: cosmos
  name: 'apex'
  properties: { resource: { id: 'apex' } }
}

resource cosmosCtrs 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-05-15' = [for c in cosmosContainers: {
  parent: cosmosDb
  name: c.name
  properties: {
    resource: {
      id: c.name
      partitionKey: { paths: [ c.pk ], kind: 'Hash' }
    }
  }
}]

// ── key vault (private) ──────────────────────────────────────────────────────
resource kv 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: kvName
  location: location
  properties: {
    sku: { family: 'A', name: 'standard' }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    publicNetworkAccess: 'Disabled'      // required by policy
    networkAcls: { defaultAction: 'Deny', bypass: 'AzureServices' }
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
  }
}

// ── private endpoints ────────────────────────────────────────────────────────
var peSubnetId = '${vnet.id}/subnets/${peSubnet}'

module peStorage 'modules/private-endpoint.bicep' = {
  name: 'pe-storage'
  params: {
    name: '${prefix}-pe-blob'
    location: location
    subnetId: peSubnetId
    targetResourceId: storage.id
    groupId: 'blob'
    dnsZoneName: dnsZoneNames[0]
  }
  dependsOn: [ dnsLinks ]
}

module peCosmos 'modules/private-endpoint.bicep' = {
  name: 'pe-cosmos'
  params: {
    name: '${prefix}-pe-cosmos'
    location: location
    subnetId: peSubnetId
    targetResourceId: cosmos.id
    groupId: 'Sql'
    dnsZoneName: dnsZoneNames[1]
  }
  dependsOn: [ dnsLinks ]
}

module peKv 'modules/private-endpoint.bicep' = {
  name: 'pe-kv'
  params: {
    name: '${prefix}-pe-kv'
    location: location
    subnetId: peSubnetId
    targetResourceId: kv.id
    groupId: 'vault'
    dnsZoneName: dnsZoneNames[2]
  }
  dependsOn: [ dnsLinks ]
}

// ── outputs (feed these into backend/.env.azure) ─────────────────────────────
output vnetId string             = vnet.id
output appsSubnetId string       = '${vnet.id}/subnets/${appsSubnet}'
output storageAccountName string = storage.name
output storageBlobEndpoint string = storage.properties.primaryEndpoints.blob
output cosmosAccountName string  = cosmos.name
output cosmosEndpoint string     = cosmos.properties.documentEndpoint
output cosmosDatabase string     = 'apex'
output keyVaultName string       = kv.name
output keyVaultUri string        = kv.properties.vaultUri
