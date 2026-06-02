targetScope = 'resourceGroup'

@description('Deployment environment name.')
param environmentName string = 'dev'

@description('Azure region for resources.')
param location string = resourceGroup().location

@description('Short project prefix used in resource names.')
param projectPrefix string = 'sysint'

@description('Logic Apps Standard app name.')
param logicAppName string = 'la-sysint-enterprise-integration-eus'

@description('Workflow Standard app service plan name.')
param appServicePlanName string = 'asp-sysint-enterprise-integration-eus'

@description('Storage account name for the Logic Apps Standard runtime.')
param storageAccountName string = 'stsysintintegeus001'

@description('Resource tags.')
param tags object = {
  Project: 'Enterprise Integration Modernization'
  Owner: 'Integration Team'
  Environment: environmentName
  CostPosture: 'Disposable learning deployment'
}

module storage 'modules/storage.bicep' = {
  name: 'storage-${environmentName}'
  params: {
    location: location
    storageAccountName: storageAccountName
    tags: tags
  }
}

module logicApp 'modules/logicapp.bicep' = {
  name: 'logicapp-${environmentName}'
  params: {
    location: location
    logicAppName: logicAppName
    appServicePlanName: appServicePlanName
    storageAccountName: storageAccountName
    tags: tags
  }
  dependsOn: [
    storage
  ]
}

output deploymentSummary object = {
  environmentName: environmentName
  location: location
  projectPrefix: projectPrefix
  logicAppName: logicApp.outputs.logicAppName
  logicAppDefaultHostName: logicApp.outputs.defaultHostName
  appServicePlanName: appServicePlanName
  storageAccountName: storage.outputs.storageAccountName
  costPosture: 'WS1 Workflow Standard. Delete resources when not actively using the learning environment.'
}
