targetScope = 'resourceGroup'

@description('Deployment environment name.')
param environmentName string = 'dev'

@description('Azure region for resources.')
param location string = resourceGroup().location

@description('Short project prefix used in resource names.')
param projectPrefix string = 'aiint'

@description('Resource tags.')
param tags object = {
  Project: 'AI-Ready Integration Modernization'
  Owner: 'Integration Team'
  Environment: environmentName
}

output deploymentSummary object = {
  environmentName: environmentName
  location: location
  projectPrefix: projectPrefix
}
