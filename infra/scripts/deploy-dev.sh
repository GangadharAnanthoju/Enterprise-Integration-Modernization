#!/usr/bin/env bash
set -euo pipefail

RESOURCE_GROUP_NAME="${RESOURCE_GROUP_NAME:-rg-sysint-enterprise-integration-eus}"
LOCATION="${LOCATION:-swedencentral}"
TEMPLATE_FILE="${TEMPLATE_FILE:-../main.bicep}"
PARAMETERS_FILE="${PARAMETERS_FILE:-../parameters.dev.json}"

echo "Deploying disposable Logic Apps Standard learning environment"
echo "Resource group: ${RESOURCE_GROUP_NAME}"
echo "Location: ${LOCATION}"

az group show --name "${RESOURCE_GROUP_NAME}" --output none

az deployment group create \
  --resource-group "${RESOURCE_GROUP_NAME}" \
  --template-file "${TEMPLATE_FILE}" \
  --parameters "@${PARAMETERS_FILE}" \
  --parameters location="${LOCATION}"
