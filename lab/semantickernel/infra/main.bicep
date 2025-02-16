@description('List of OpenAI resources to create. Add pairs of name and location.')
param openAIConfig array = []

@description('Deployment Name')
param openAIDeploymentName string

@description('Azure OpenAI Sku')
@allowed([
  'S0'
])
param openAISku string = 'S0'

@description('Model Name')
param openAIModelName string

@description('Model Version')
param openAIModelVersion string

@description('Model Capacity')
param openAIModelCapacity int = 50

param administratorLogin string

param storageContainerName string 

@description('Principal ID for role assignment')
param principalId string 

@secure()
param administratorLoginPassword string
param location string = resourceGroup().location
param serverName string = 'postgresserver'
param serverEdition string = 'Burstable'
param skuSizeGB int = 128
param dbInstanceType string = 'Standard_B2s'
param haMode string = 'Disabled'
param availabilityZone string = '1'
param version string = '12'
// buult-in logging: additions BEGIN

@description('Name of the Log Analytics resource')
param logAnalyticsName string = 'workspace'

@description('Location of the Log Analytics resource')
param logAnalyticsLocation string = resourceGroup().location

@description('Name of the Application Insights resource')
param applicationInsightsName string = 'insights'

@description('Location of the Application Insights resource')
param applicationInsightsLocation string = resourceGroup().location

var principalType = 'User' 

// buult-in logging: additions END

// vector-searching: additions BEGIN

@description('Embeddings Model Name')
param openAIEmbeddingsDeploymentName string = 'text-embedding-large-3'

@description('Embeddings Model Name')
param openAIEmbeddingsModelName string = 'text-embedding-large-3'

@description('Embeddings Model Version')
param openAIEmbeddingsModelVersion string = '1'

@description('AI Search service name')
@minLength(2)
@maxLength(60)
param searchServiceName string = 'search'

@description('AI Search service location')
param searchServiceLocation string = resourceGroup().location

@description('AI Search service SKU')
param searchServiceSku string = 'standard'

@description('Replicas distribute search workloads across the service. You need at least two replicas to support high availability of query workloads (not applicable to the free tier).')
@minValue(1)
@maxValue(12)
param searchServiceReplicaCount int = 1

@description('Partitions allow for scaling of document count as well as faster indexing by sharding your index over multiple search units.')
@allowed([
  1
  2
  3
  4
  6
  12
])
param searchServicePartitionCount int = 1

// vector-searching: additions END

var resourceSuffix = uniqueString(subscription().id, resourceGroup().id)

resource cognitiveServices 'Microsoft.CognitiveServices/accounts@2021-10-01' = [for config in openAIConfig: if(length(openAIConfig) > 0) {
  name: '${config.name}-${resourceSuffix}'
  location: config.location
  sku: {
    name: openAISku
  }
  kind: 'OpenAI'
  properties: {
    apiProperties: {
      statisticsEnabled: false
    }
    customSubDomainName: toLower('${config.name}-${resourceSuffix}')
  }
}]

resource deployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01'  =  [for (config, i) in openAIConfig: if(length(openAIConfig) > 0) {
    name: openAIDeploymentName
    parent: cognitiveServices[i]
    properties: {
      model: {
        format: 'OpenAI'
        name: openAIModelName
        version: openAIModelVersion
      }
    }
    sku: {
        name: 'GlobalStandard'
        capacity: openAIModelCapacity
    }
}]


// vector-searching: additions BEGIN
resource embeddingsDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01'  =  [for (config, i) in openAIConfig: if(length(openAIConfig) > 0 && !empty(deployment[i].id)) {
  name: openAIEmbeddingsDeploymentName
  parent: cognitiveServices[i]
  properties: {
    model: {
      format: 'OpenAI'
      name: openAIEmbeddingsModelName
      version: openAIEmbeddingsModelVersion
    }
  }
  sku: {
      name: 'Standard'
      capacity: openAIModelCapacity
  }
}]

module searchService 'br/public:avm/res/search/search-service:0.7.1'  = {
  name: 'search-service'
  scope: resourceGroup()
  params: {
    name: '${searchServiceName}-${resourceSuffix}'
    location: searchServiceLocation
    sku: searchServiceSku
    managedIdentities: { systemAssigned: true }
    replicaCount: searchServiceReplicaCount
    partitionCount: searchServicePartitionCount
    roleAssignments: [
      {
        roleDefinitionIdOrName: 'Search Index Data Reader'
        principalId: principalId
        principalType: principalType
      }
      {
        roleDefinitionIdOrName: 'Search Index Data Contributor'
        principalId: principalId
        principalType: principalType
      }
      {
        roleDefinitionIdOrName: 'Search Service Contributor'
        principalId: principalId
        principalType: principalType
      }
    ]
    }
}
// vector-searching: additions END

// create postgreSQL database
resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2021-06-01' = {
  name: '${serverName}-${resourceSuffix}'
  location: location
  sku: {
    name: dbInstanceType
    tier: serverEdition
  }
  properties: {
    version: version
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorLoginPassword
    highAvailability: {
      mode: haMode
    }
    storage: {
      storageSizeGB: skuSizeGB
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    availabilityZone: availabilityZone
  }
}

// buult-in logging: additions BEGIN
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2021-12-01-preview' = {
  name: '${logAnalyticsName}-${resourceSuffix}'
  location: logAnalyticsLocation
  properties: any({
    retentionInDays: 30
    features: {
      searchVersion: 1
    }
    sku: {
      name: 'PerGB2018'
    }
  })
}

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${applicationInsightsName}-${resourceSuffix}'
  location: applicationInsightsLocation
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

// Storage
module storage 'br/public:avm/res/storage/storage-account:0.9.1' = {
  name: 'storage'
  scope: resourceGroup()
  params: {
    name: 'storage${resourceSuffix}'
    location: location
    kind: 'StorageV2'
    skuName: 'Standard_LRS'
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    blobServices: {
      deleteRetentionPolicyDays: 2
      deleteRetentionPolicyEnabled: true
      containers: [
        {
          name: storageContainerName
          publicAccess: 'None'
        }
      ]
    }
    roleAssignments: [
      {
        roleDefinitionIdOrName: 'Storage Blob Data Reader'
        principalId: principalId
        principalType: principalType
      }
      // For uploading documents to storage container:
      {
        roleDefinitionIdOrName: 'Storage Blob Data Contributor'
        principalId: principalId
        principalType: principalType
      }
    ]
  }
}

// Necessary for integrated vectorization, for search service to access storage
module storageRoleSearchService './role.bicep' = {
  scope: resourceGroup()
  name: 'storage-role-searchservice'
  params: {
    principalId: searchService.outputs.systemAssignedMIPrincipalId
    roleDefinitionId: '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1' // Storage Blob Data Reader
    principalType: 'ServicePrincipal'
  }
}

// Necessary for integrated vectorization, for search service to access OpenAI embeddings
module openAiRoleSearchService './role.bicep' = {
  scope: resourceGroup()
  name: 'openai-role-searchservice'
  params: {
    principalId: searchService.outputs.systemAssignedMIPrincipalId
    roleDefinitionId: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
    principalType: 'ServicePrincipal'
  }
}

