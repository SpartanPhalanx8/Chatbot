{
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "storageEnabled": {
            "type": "bool"
        },
        "searchEnabled": {
            "type": "bool"
        },
        "azureSearchLocation": {
            "type": "string"
        },
        "azureSearchSku": {
            "type": "string"
        },
        "searchHostingMode": {
            "type": "string"
        },
        "storageResourceName": {
            "type": "string"
        },
        "storageLocation": {
            "type": "string"
        },
        "storageSkuType": {
            "type": "string"
        },
        "storageResourceGroupName": {
            "type": "string"
        },
        "storageNewOrExisting": {
            "type": "String"
        },
        "umiId": {
            "type": "string"
        },
        "name": {
            "type": "string"
        },
        "location": {
            "type": "string"
        },
        "resourceGroupName": {
            "type": "string"
        },
        "resourceGroupId": {
            "type": "string"
        },
        "sku": {
            "type": "string"
        },
        "tagValues": {
            "type": "object"
        },
        "virtualNetworkType": {
            "type": "string"
        },
        "vnet": {
            "type": "object"
        },
        "ipRules": {
            "type": "array"
        },
        "identity": {
            "type": "object"
        },
        "privateEndpoints": {
            "type": "array"
        },
        "privateDnsZone": {
            "type": "string"
        },
        "isCommitmentPlanForDisconnectedContainerEnabled": {
            "type": "bool"
        },
        "commitmentPlanForDisconnectedContainer": {
            "type": "object"
        },
        "isCommitmentPlanForSummarizationEnabled": {
            "type": "bool"
        },
        "commitmentPlanForSummarization": {
            "type": "object"
        },
        "uniqueId": {
            "type": "string",
            "defaultValue": "[newGuid()]"
        }
    },
    "variables": {
        "defaultVNetName": "taCSDefaultVNet9901",
        "defaultSubnetName": "taCSDefaultSubnet9901",
        "defaultAddressPrefix": "13.41.6.0/26",
        "puredAzureSearchName": "[replace(parameters('name'), '-', '')]",
        "normalizedAzureSearchName": "[if(greater(length(variables('puredAzureSearchName')), 40), substring(variables('puredAzureSearchName'), sub(length(variables('puredAzureSearchName')), 40), 40) , variables('puredAzureSearchName'))]",
        "azureSearchName": "[toLower(concat(variables('normalizedAzureSearchName'), '-as', uniqueString(resourceGroup().id, variables('normalizedAzureSearchName'), parameters('azureSearchSku'), parameters('azureSearchLocation'),parameters('searchHostingMode'))))]",
        "storageResourceId": "[concat('/subscriptions/', subscription().subscriptionId, '/resourceGroups/', parameters('storageResourceGroupName'), '/providers/Microsoft.Storage/storageAccounts/', parameters('storageResourceName'))]",
        "storageBlobDataContributorRole": "[concat('/subscriptions/', subscription().subscriptionId, '/providers/Microsoft.Authorization/roleDefinitions/', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')]",
        "storageBlobDataContributorRoleGuid": "[guid(subscription().subscriptionId, parameters('name'), parameters('storageResourceName'), 'storageBlobDataContributor')]",
        "vnetProperties": {
            "customSubDomainName": "[toLower(parameters('name'))]",
            "publicNetworkAccess": "[if(equals(parameters('virtualNetworkType'), 'Internal'), 'Disabled', 'Enabled')]",
            "networkAcls": {
                "defaultAction": "[if(equals(parameters('virtualNetworkType'), 'External'), 'Deny', 'Allow')]",
                "virtualNetworkRules": "[if(and(equals(parameters('virtualNetworkType'), 'External'), not(empty(parameters('vnet')))), json(concat('[{\"id\": \"', concat(subscription().id, '/resourceGroups/', parameters('vnet').resourceGroup, '/providers/Microsoft.Network/virtualNetworks/', parameters('vnet').name, '/subnets/', parameters('vnet').subnets.subnet.name), '\"}]')), json('[]'))]",
                "ipRules": "[if(or(empty(parameters('ipRules')), empty(parameters('ipRules')[0].value)), json('[]'), parameters('ipRules'))]"
            }
        },
        "systemAndUserIdentities": {
            "type": "SystemAssigned, UserAssigned",
            "userAssignedIdentities": "[if(contains(string(parameters('identity')),'userAssignedIdentities'), parameters('identity').userAssignedIdentities, json('{}'))]"
        }
    },
    "resources": [
        {
            "type": "Microsoft.Resources/deployments",
            "apiVersion": "2017-05-10",
            "name": "deployVnet",
            "properties": {
                "mode": "Incremental",
                "template": {
                    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
                    "contentVersion": "1.0.0.0",
                    "parameters": {},
                    "variables": {},
                    "resources": [
                        {
                            "type": "Microsoft.Network/virtualNetworks",
                            "apiVersion": "2020-04-01",
                            "name": "[if(and(equals(parameters('virtualNetworkType'), 'External'), not(empty(parameters('vnet')))), parameters('vnet').name, variables('defaultVNetName'))]",
                            "location": "[parameters('location')]",
                            "properties": {
                                "addressSpace": {
                                    "addressPrefixes": "[if(and(equals(parameters('virtualNetworkType'), 'External'), not(empty(parameters('vnet')))), parameters('vnet').addressPrefixes, json(concat('[{\"', variables('defaultAddressPrefix'),'\"}]')))]"
                                },
                                "subnets": [
                                    {
                                        "name": "[if(and(equals(parameters('virtualNetworkType'), 'External'), not(empty(parameters('vnet')))), parameters('vnet').subnets.subnet.name, variables('defaultSubnetName'))]",
                                        "properties": {
                                            "serviceEndpoints": [
                                                {
                                                    "service": "Microsoft.CognitiveServices",
                                                    "locations": [
                                                        "[parameters('location')]"
                                                    ]
                                                }
                                            ],
                                            "addressPrefix": "[if(and(equals(parameters('virtualNetworkType'), 'External'), not(empty(parameters('vnet')))), parameters('vnet').subnets.subnet.addressPrefix, variables('defaultAddressPrefix'))]"
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                },
                "parameters": {}
            },
            "condition": "[and(and(not(empty(parameters('vnet'))), equals(parameters('vnet').newOrExisting, 'new')), equals(parameters('virtualNetworkType'), 'External'))]"
        },
        {
            "apiVersion": "2024-10-01",
            "name": "[parameters('name')]",
            "location": "[parameters('location')]",
            "type": "Microsoft.CognitiveServices/accounts",
            "kind": "TextAnalytics",
            "tags": "[if(contains(parameters('tagValues'), 'Microsoft.CognitiveServices/accounts'), parameters('tagValues')['Microsoft.CognitiveServices/accounts'], json('{}'))]",
            "sku": {
                "name": "[parameters('sku')]"
            },
            "identity": "[if(contains(string(parameters('identity')),'userAssignedIdentities'), variables('systemAndUserIdentities'), parameters('identity'))]",
            "properties": "[variables('vnetProperties')]",
            "resources": [
                {
                    "type": "commitmentPlans",
                    "apiVersion": "2021-10-01",
                    "name": "DisconnectedContainer-TA-1",
                    "properties": "[parameters('commitmentPlanForDisconnectedContainer')]",
                    "condition": "[parameters('isCommitmentPlanForDisconnectedContainerEnabled')]",
                    "dependsOn": [
                        "[parameters('name')]"
                    ]
                },
                {
                    "type": "commitmentPlans",
                    "apiVersion": "2021-10-01",
                    "name": "DisconnectedContainer-Summarization-1",
                    "properties": "[parameters('commitmentPlanForSummarization')]",
                    "condition": "[parameters('isCommitmentPlanForSummarizationEnabled')]",
                    "dependsOn": [
                        "[parameters('name')]"
                    ]
                }
            ],
            "dependsOn": [
                "[concat('Microsoft.Resources/deployments/', 'deployVnet')]"
            ]
        },
        {
            "apiVersion": "2018-05-01",
            "name": "[concat('deployPrivateEndpoint-', parameters('privateEndpoints')[copyIndex()].privateEndpointConfiguration.privateEndpoint.name)]",
            "type": "Microsoft.Resources/deployments",
            "resourceGroup": "[parameters('privateEndpoints')[copyIndex()].privateEndpointConfiguration.resourceGroup.value.name]",
            "subscriptionId": "[parameters('privateEndpoints')[copyIndex()].privateEndpointConfiguration.subscription.subscriptionId]",
            "dependsOn": [
                "[if(parameters('searchEnabled'), if(parameters('storageEnabled'), concat('Microsoft.Resources/deployments/','attachStorageAndSearchForCognitiveServicesAccount'), concat('Microsoft.Resources/deployments/','attachSearchForCognitiveServicesAccount')), parameters('name'))]"
            ],
            "condition": "[equals(parameters('virtualNetworkType'), 'Internal')]",
            "copy": {
                "name": "privateendpointscopy",
                "count": "[length(parameters('privateEndpoints'))]"
            },
            "properties": {
                "mode": "Incremental",
                "template": {
                    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
                    "contentVersion": "1.0.0.0",
                    "resources": [
                        {
                            "location": "[parameters('privateEndpoints')[copyIndex()].privateEndpointConfiguration.privateEndpoint.location]",
                            "name": "[parameters('privateEndpoints')[copyIndex()].privateEndpointConfiguration.privateEndpoint.name]",
                            "type": "Microsoft.Network/privateEndpoints",
                            "apiVersion": "2021-05-01",
                            "properties": {
                                "subnet": {
                                    "id": "[parameters('privateEndpoints')[copyIndex()].privateEndpointConfiguration.privateEndpoint.properties.subnet.id]"
                                },
                                "privateLinkServiceConnections": [
                                    {
                                        "name": "[parameters('privateEndpoints')[copyIndex()].privateEndpointConfiguration.privateEndpoint.name]",
                                        "properties": {
                                            "privateLinkServiceId": "[concat(parameters('resourceGroupId'), '/providers/Microsoft.CognitiveServices/accounts/', parameters('name'))]",
                                            "groupIds": "[parameters('privateEndpoints')[copyIndex()].privateEndpointConfiguration.privateEndpoint.properties.privateLinkServiceConnections[0].properties.groupIds]"
                                        }
                                    }
                                ],
                                "customNetworkInterfaceName": "[concat(parameters('privateEndpoints')[copyIndex()].privateEndpointConfiguration.privateEndpoint.name, '-nic')]"
                            },
                            "tags": {}
                        }
                    ]
                }
            }
        },
        {
            "apiVersion": "2018-05-01",
            "name": "[concat('deployDnsZoneGroup-', parameters('privateEndpoints')[copyIndex()].privateEndpointConfiguration.privateEndpoint.name)]",
            "type": "Microsoft.Resources/deployments",
            "resourceGroup": "[parameters('privateEndpoints')[copyIndex()].privateEndpointConfiguration.resourceGroup.value.name]",
            "subscriptionId": "[parameters('privateEndpoints')[copyIndex()].privateEndpointConfiguration.subscription.subscriptionId]",
            "dependsOn": [
                "[concat('deployPrivateEndpoint-', parameters('privateEndpoints')[copyIndex()].privateEndpointConfiguration.privateEndpoint.name)]"
            ],
            "condition": "[and(equals(parameters('virtualNetworkType'), 'Internal'), parameters('privateEndpoints')[copyIndex()].privateDnsZoneConfiguration.integrateWithPrivateDnsZone)]",
            "copy": {
                "name": "privateendpointdnscopy",
                "count": "[length(parameters('privateEndpoints'))]"
            },
            "properties": {
                "mode": "Incremental",
                "template": {
                    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
                    "contentVersion": "1.0.0.0",
                    "resources": [
                        {
                            "type": "Microsoft.Network/privateDnsZones",
                            "apiVersion": "2018-09-01",
                            "name": "[parameters('privateDnsZone')]",
                            "location": "global",
                            "tags": {},
                            "properties": {}
                        },
                        {
                            "type": "Microsoft.Network/privateDnsZones/virtualNetworkLinks",
                            "apiVersion": "2018-09-01",
                            "name": "[concat(parameters('privateDnsZone'), '/', replace(uniqueString(parameters('privateEndpoints')[copyIndex()].privateEndpointConfiguration.privateEndpoint.properties.subnet.id), '/subnets/default', ''))]",
                            "location": "global",
                            "dependsOn": [
                                "[parameters('privateDnsZone')]"
                            ],
                            "properties": {
                                "virtualNetwork": {
                                    "id": "[split(parameters('privateEndpoints')[copyIndex()].privateEndpointConfiguration.privateEndpoint.properties.subnet.id, '/subnets/')[0]]"
                                },
                                "registrationEnabled": false
                            }
                        },
                        {
                            "apiVersion": "2017-05-10",
                            "name": "[concat('EndpointDnsRecords-', parameters('privateEndpoints')[copyIndex()].privateEndpointConfiguration.privateEndpoint.name)]",
                            "type": "Microsoft.Resources/deployments",
                            "dependsOn": [
                                "[parameters('privateDnsZone')]"
                            ],
                            "properties": {
                                "mode": "Incremental",
                                "templatelink": {
                                    "uri": "https://go.microsoft.com/fwlink/?linkid=2264916"
                                },
                                "parameters": {
                                    "privateDnsName": {
                                        "value": "[parameters('privateDnsZone')]"
                                    },
                                    "privateEndpointNicResourceId": {
                                        "value": "[concat(parameters('privateEndpoints')[copyIndex()].privateEndpointConfiguration.resourceGroup.value.id, '/providers/Microsoft.Network/networkInterfaces/', parameters('privateEndpoints')[copyIndex()].privateEndpointConfiguration.privateEndpoint.name, '-nic')]"
                                    },
                                    "nicRecordsTemplateUri": {
                                        "value": "https://go.microsoft.com/fwlink/?linkid=2264719"
                                    },
                                    "ipConfigRecordsTemplateUri": {
                                        "value": "https://go.microsoft.com/fwlink/?linkid=2265018"
                                    },
                                    "uniqueId": {
                                        "value": "[parameters('uniqueId')]"
                                    },
                                    "existingRecords": {
                                        "value": {}
                                    }
                                }
                            }
                        },
                        {
                            "type": "Microsoft.Network/privateEndpoints/privateDnsZoneGroups",
                            "apiVersion": "2020-03-01",
                            "name": "[concat(parameters('privateEndpoints')[copyIndex()].privateEndpointConfiguration.privateEndpoint.name, '/', 'default')]",
                            "location": "[parameters('location')]",
                            "dependsOn": [
                                "[parameters('privateDnsZone')]"
                            ],
                            "properties": {
                                "privateDnsZoneConfigs": [
                                    {
                                        "name": "privatelink-cognitiveservices",
                                        "properties": {
                                            "privateDnsZoneId": "[concat(parameters('resourceGroupId'), '/providers/Microsoft.Network/privateDnsZones/', parameters('privateDnsZone'))]"
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        },
        {
            "type": "Microsoft.Resources/deployments",
            "apiVersion": "2017-05-10",
            "name": "roleAssignmentsForStorage",
            "dependsOn": [
                "[concat('Microsoft.CognitiveServices/accounts/', parameters('name'))]",
                "[concat('Microsoft.Resources/deployments/', 'deployStorage')]"
            ],
            "properties": {
                "mode": "Incremental",
                "template": {
                    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
                    "contentVersion": "1.0.0.0",
                    "parameters": {},
                    "variables": {},
                    "resources": [
                        {
                            "type": "Microsoft.Storage/storageAccounts/blobServices",
                            "apiVersion": "2018-07-01",
                            "name": "[concat(parameters('storageResourceName'), '/default')]",
                            "properties": {
                                "cors": {
                                    "corsRules": [
                                        {
                                            "allowedOrigins": [
                                                "https://language.cognitive.azure.com"
                                            ],
                                            "exposedHeaders": [
                                                "*"
                                            ],
                                            "allowedHeaders": [
                                                "*"
                                            ],
                                            "allowedMethods": [
                                                "DELETE",
                                                "GET",
                                                "POST",
                                                "OPTIONS",
                                                "PUT"
                                            ],
                                            "maxAgeInSeconds": 500
                                        }
                                    ]
                                }
                            }
                        },
                        {
                            "type": "Microsoft.Storage/storageAccounts/providers/roleAssignments",
                            "apiVersion": "2018-09-01-preview",
                            "name": "[concat(parameters('storageResourceName'), '/Microsoft.Authorization/', variables('storageBlobDataContributorRoleGuid'))]",
                            "properties": {
                                "roleDefinitionId": "[variables('storageBlobDataContributorRole')]",
                                "principalId": "[if(not(empty(parameters('umiId'))),reference(parameters('umiId'), '2018-11-30', 'Full').properties.principalId,reference(concat('Microsoft.CognitiveServices/accounts/', parameters('name')), '2024-10-01', 'Full').identity.principalId)]",
                                "principalType": "ServicePrincipal",
                                "scope": "[concat(subscription().id,'/resourcegroups/', parameters('storageResourceGroupName'), '/providers/Microsoft.Storage/storageAccounts/', parameters('storageResourceName'))]"
                            }
                        }
                    ]
                },
                "parameters": {}
            },
            "resourceGroup": "[parameters('storageResourceGroupName')]",
            "condition": "[parameters('storageEnabled')]"
        },
        {
            "type": "Microsoft.Resources/deployments",
            "apiVersion": "2017-05-10",
            "name": "deployStorage",
            "properties": {
                "mode": "Incremental",
                "template": {
                    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
                    "contentVersion": "1.0.0.0",
                    "parameters": {},
                    "variables": {},
                    "resources": [
                        {
                            "type": "Microsoft.Storage/storageAccounts",
                            "apiVersion": "2019-04-01",
                            "name": "[parameters('storageResourceName')]",
                            "location": "[parameters('storageLocation')]",
                            "sku": {
                                "name": "[parameters('storageSkuType')]"
                            },
                            "properties": {
                                "minimumTlsVersion": "TLS1_2"
                            }
                        }
                    ]
                },
                "parameters": {}
            },
            "resourceGroup": "[parameters('storageResourceGroupName')]",
            "condition": "[and(parameters('storageEnabled'), equals(parameters('storageNewOrExisting'), 'new'))]"
        },
        {
            "name": "[variables('azureSearchName')]",
            "type": "Microsoft.Search/searchServices",
            "apiVersion": "2015-08-19",
            "location": "[parameters('azureSearchLocation')]",
            "tags": {},
            "properties": {
                "replicaCount": 1,
                "partitionCount": 1,
                "hostingMode": "[parameters('searchHostingMode')]"
            },
            "sku": {
                "name": "[parameters('azureSearchSku')]"
            },
            "condition": "[parameters('searchEnabled')]"
        },
        {
            "type": "Microsoft.Resources/deployments",
            "apiVersion": "2021-04-01",
            "name": "attachStorageAndSearchForCognitiveServicesAccount",
            "dependsOn": [
                "[concat('Microsoft.Resources/deployments/', 'roleAssignmentsForStorage')]",
                "[concat('Microsoft.Search/searchServices/', variables('azureSearchName'))]"
            ],
            "properties": {
                "mode": "Incremental",
                "expressionEvaluationOptions": {
                    "scope": "inner"
                },
                "template": {
                    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
                    "contentVersion": "1.0.0.0",
                    "parameters": {
                        "azureSearchLocation": {
                            "type": "string"
                        },
                        "azureSearchSku": {
                            "type": "string"
                        },
                        "searchHostingMode": {
                            "type": "string"
                        },
                        "storageResourceName": {
                            "type": "string"
                        },
                        "storageLocation": {
                            "type": "string"
                        },
                        "storageSkuType": {
                            "type": "string"
                        },
                        "storageResourceGroupName": {
                            "type": "string"
                        },
                        "umiId": {
                            "type": "string"
                        },
                        "name": {
                            "type": "string"
                        },
                        "location": {
                            "type": "string"
                        },
                        "resourceGroupName": {
                            "type": "string"
                        },
                        "resourceGroupId": {
                            "type": "string"
                        },
                        "sku": {
                            "type": "string"
                        },
                        "tagValues": {
                            "type": "object"
                        },
                        "virtualNetworkType": {
                            "type": "string"
                        },
                        "vnet": {
                            "type": "object"
                        },
                        "ipRules": {
                            "type": "array"
                        },
                        "identity": {
                            "type": "object"
                        }
                    },
                    "variables": {
                        "puredAzureSearchName": "[replace(parameters('name'), '-', '')]",
                        "normalizedAzureSearchName": "[if(greater(length(variables('puredAzureSearchName')), 40), substring(variables('puredAzureSearchName'), sub(length(variables('puredAzureSearchName')), 40), 40) , variables('puredAzureSearchName'))]",
                        "azureSearchName": "[toLower(concat(variables('normalizedAzureSearchName'), '-as', uniqueString(resourceGroup().id, variables('normalizedAzureSearchName'), parameters('azureSearchSku'), parameters('azureSearchLocation'),parameters('searchHostingMode'))))]",
                        "storageResourceId": "[concat('/subscriptions/', subscription().subscriptionId, '/resourceGroups/', parameters('storageResourceGroupName'), '/providers/Microsoft.Storage/storageAccounts/', parameters('storageResourceName'))]",
                        "systemAndUserIdentities": {
                            "type": "SystemAssigned, UserAssigned",
                            "userAssignedIdentities": "[if(contains(string(parameters('identity')),'userAssignedIdentities'), parameters('identity').userAssignedIdentities, json('{}'))]"
                        }
                    },
                    "resources": [
                        {
                            "type": "Microsoft.CognitiveServices/accounts",
                            "apiVersion": "2024-10-01",
                            "name": "[parameters('name')]",
                            "location": "[parameters('location')]",
                            "sku": {
                                "name": "[parameters('sku')]"
                            },
                            "kind": "TextAnalytics",
                            "tags": "[if(contains(parameters('tagValues'), 'Microsoft.CognitiveServices/accounts'), parameters('tagValues')['Microsoft.CognitiveServices/accounts'], json('{}'))]",
                            "identity": "[if(contains(string(parameters('identity')),'userAssignedIdentities'), variables('systemAndUserIdentities'), parameters('identity'))]",
                            "properties": {
                                "customSubDomainName": "[toLower(parameters('name'))]",
                                "publicNetworkAccess": "Enabled",
                                "networkAcls": {
                                    "defaultAction": "Allow",
                                    "virtualNetworkRules": "[if(and(equals(parameters('virtualNetworkType'), 'External'), not(empty(parameters('vnet')))), json(concat('[{\"id\": \"', concat(subscription().id, '/resourceGroups/', parameters('vnet').privateEndpointConfiguration.resourceGroup, '/providers/Microsoft.Network/virtualNetworks/', parameters('vnet').name, '/subnets/', parameters('vnet').subnets.subnet.name), '\"}]')), json('[]'))]",
                                    "ipRules": "[if(or(empty(parameters('ipRules')), empty(parameters('ipRules')[0].value)), json('[]'), parameters('ipRules'))]"
                                },
                                "apiProperties": {
                                    "qnaAzureSearchEndpointId": "[resourceId('Microsoft.Search/searchServices', variables('azureSearchName'))]",
                                    "qnaAzureSearchEndpointKey": "[listadminkeys(resourceId('Microsoft.Search/searchServices', variables('azureSearchName')), '2015-08-19').primaryKey]"
                                },
                                "userOwnedStorage": [
                                    {
                                        "resourceId": "[variables('storageResourceId')]",
                                        "identityClientId": "[if(empty(parameters('umiId')), null(), reference(parameters('umiId'), '2018-11-30', 'Full').properties.clientId)]"
                                    }
                                ]
                            }
                        }
                    ]
                },
                "parameters": {
                    "azureSearchLocation": {
                        "value": "[parameters('azureSearchLocation')]"
                    },
                    "azureSearchSku": {
                        "value": "[parameters('azureSearchSku')]"
                    },
                    "searchHostingMode": {
                        "value": "[parameters('searchHostingMode')]"
                    },
                    "storageResourceName": {
                        "value": "[parameters('storageResourceName')]"
                    },
                    "storageLocation": {
                        "value": "[parameters('storageLocation')]"
                    },
                    "storageSkuType": {
                        "value": "[parameters('storageSkuType')]"
                    },
                    "storageResourceGroupName": {
                        "value": "[parameters('storageResourceGroupName')]"
                    },
                    "umiId": {
                        "value": "[parameters('umiId')]"
                    },
                    "name": {
                        "value": "[parameters('name')]"
                    },
                    "location": {
                        "value": "[parameters('location')]"
                    },
                    "resourceGroupName": {
                        "value": "[parameters('resourceGroupName')]"
                    },
                    "resourceGroupId": {
                        "value": "[parameters('resourceGroupId')]"
                    },
                    "sku": {
                        "value": "[parameters('sku')]"
                    },
                    "tagValues": {
                        "value": "[parameters('tagValues')]"
                    },
                    "virtualNetworkType": {
                        "value": "[parameters('virtualNetworkType')]"
                    },
                    "vnet": {
                        "value": "[parameters('vnet')]"
                    },
                    "ipRules": {
                        "value": "[parameters('ipRules')]"
                    },
                    "identity": {
                        "value": "[parameters('identity')]"
                    }
                }
            },
            "condition": "[and(parameters('storageEnabled'), parameters('searchEnabled'))]"
        },
        {
            "type": "Microsoft.Resources/deployments",
            "apiVersion": "2017-05-10",
            "name": "attachStorageForCognitiveServicesAccount",
            "dependsOn": [
                "[concat('Microsoft.Resources/deployments/', 'roleAssignmentsForStorage')]"
            ],
            "properties": {
                "mode": "Incremental",
                "template": {
                    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
                    "contentVersion": "1.0.0.0",
                    "parameters": {},
                    "variables": {},
                    "resources": [
                        {
                            "type": "Microsoft.CognitiveServices/accounts",
                            "apiVersion": "2024-10-01",
                            "name": "[parameters('name')]",
                            "location": "[parameters('location')]",
                            "sku": {
                                "name": "[parameters('sku')]"
                            },
                            "kind": "TextAnalytics",
                            "tags": "[if(contains(parameters('tagValues'), 'Microsoft.CognitiveServices/accounts'), parameters('tagValues')['Microsoft.CognitiveServices/accounts'], json('{}'))]",
                            "identity": "[if(contains(string(parameters('identity')),'userAssignedIdentities'), variables('systemAndUserIdentities'), parameters('identity'))]",
                            "properties": {
                                "customSubDomainName": "[toLower(parameters('name'))]",
                                "publicNetworkAccess": "[if(equals(parameters('virtualNetworkType'), 'Internal'), 'Disabled', 'Enabled')]",
                                "networkAcls": {
                                    "defaultAction": "[if(equals(parameters('virtualNetworkType'), 'External'), 'Deny', 'Allow')]",
                                    "virtualNetworkRules": "[if(and(equals(parameters('virtualNetworkType'), 'External'), not(empty(parameters('vnet')))), json(concat('[{\"id\": \"', concat(subscription().id, '/resourceGroups/', parameters('vnet').privateEndpointConfiguration.resourceGroup, '/providers/Microsoft.Network/virtualNetworks/', parameters('vnet').name, '/subnets/', parameters('vnet').subnets.subnet.name), '\"}]')), json('[]'))]",
                                    "ipRules": "[if(or(empty(parameters('ipRules')), empty(parameters('ipRules')[0].value)), json('[]'), parameters('ipRules'))]"
                                },
                                "userOwnedStorage": [
                                    {
                                        "resourceId": "[variables('storageResourceId')]",
                                        "identityClientId": "[if(empty(parameters('umiId')), null(), reference(parameters('umiId'), '2018-11-30', 'Full').properties.clientId)]"
                                    }
                                ]
                            }
                        }
                    ]
                },
                "parameters": {}
            },
            "condition": "[and(parameters('storageEnabled'), not(parameters('searchEnabled')))]"
        },
        {
            "type": "Microsoft.Resources/deployments",
            "apiVersion": "2017-05-10",
            "name": "attachSearchForCognitiveServicesAccount",
            "dependsOn": [
                "[concat('Microsoft.CognitiveServices/accounts/', parameters('name'))]",
                "[concat('Microsoft.Search/searchServices/', variables('azureSearchName'))]"
            ],
            "properties": {
                "mode": "Incremental",
                "expressionEvaluationOptions": {
                    "scope": "inner"
                },
                "template": {
                    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
                    "contentVersion": "1.0.0.0",
                    "parameters": {
                        "azureSearchLocation": {
                            "type": "string"
                        },
                        "azureSearchSku": {
                            "type": "string"
                        },
                        "searchHostingMode": {
                            "type": "string"
                        },
                        "umiId": {
                            "type": "string"
                        },
                        "name": {
                            "type": "string"
                        },
                        "location": {
                            "type": "string"
                        },
                        "resourceGroupName": {
                            "type": "string"
                        },
                        "resourceGroupId": {
                            "type": "string"
                        },
                        "sku": {
                            "type": "string"
                        },
                        "tagValues": {
                            "type": "object"
                        },
                        "virtualNetworkType": {
                            "type": "string"
                        },
                        "vnet": {
                            "type": "object"
                        },
                        "ipRules": {
                            "type": "array"
                        },
                        "identity": {
                            "type": "object"
                        }
                    },
                    "variables": {
                        "puredAzureSearchName": "[replace(parameters('name'), '-', '')]",
                        "normalizedAzureSearchName": "[if(greater(length(variables('puredAzureSearchName')), 40), substring(variables('puredAzureSearchName'), sub(length(variables('puredAzureSearchName')), 40), 40) , variables('puredAzureSearchName'))]",
                        "azureSearchName": "[toLower(concat(variables('normalizedAzureSearchName'), '-as', uniqueString(resourceGroup().id, variables('normalizedAzureSearchName'), parameters('azureSearchSku'), parameters('azureSearchLocation'),parameters('searchHostingMode'))))]",
                        "systemAndUserIdentities": {
                            "type": "SystemAssigned, UserAssigned",
                            "userAssignedIdentities": "[if(contains(string(parameters('identity')),'userAssignedIdentities'), parameters('identity').userAssignedIdentities, json('{}'))]"
                        }
                    },
                    "resources": [
                        {
                            "type": "Microsoft.CognitiveServices/accounts",
                            "apiVersion": "2024-10-01",
                            "name": "[parameters('name')]",
                            "location": "[parameters('location')]",
                            "sku": {
                                "name": "[parameters('sku')]"
                            },
                            "kind": "TextAnalytics",
                            "tags": "[if(contains(parameters('tagValues'), 'Microsoft.CognitiveServices/accounts'), parameters('tagValues')['Microsoft.CognitiveServices/accounts'], json('{}'))]",
                            "identity": "[if(contains(string(parameters('identity')),'userAssignedIdentities'), variables('systemAndUserIdentities'), parameters('identity'))]",
                            "properties": {
                                "customSubDomainName": "[toLower(parameters('name'))]",
                                "publicNetworkAccess": "Enabled",
                                "networkAcls": {
                                    "defaultAction": "Allow",
                                    "virtualNetworkRules": "[if(and(equals(parameters('virtualNetworkType'), 'External'), not(empty(parameters('vnet')))), json(concat('[{\"id\": \"', concat(subscription().id, '/resourceGroups/', parameters('vnet').privateEndpointConfiguration.resourceGroup, '/providers/Microsoft.Network/virtualNetworks/', parameters('vnet').name, '/subnets/', parameters('vnet').subnets.subnet.name), '\"}]')), json('[]'))]",
                                    "ipRules": "[if(or(empty(parameters('ipRules')), empty(parameters('ipRules')[0].value)), json('[]'), parameters('ipRules'))]"
                                },
                                "apiProperties": {
                                    "qnaAzureSearchEndpointId": "[resourceId('Microsoft.Search/searchServices', variables('azureSearchName'))]",
                                    "qnaAzureSearchEndpointKey": "[listadminkeys(resourceId('Microsoft.Search/searchServices', variables('azureSearchName')), '2015-08-19').primaryKey]"
                                }
                            }
                        }
                    ]
                },
                "parameters": {
                    "azureSearchLocation": {
                        "value": "[parameters('azureSearchLocation')]"
                    },
                    "azureSearchSku": {
                        "value": "[parameters('azureSearchSku')]"
                    },
                    "searchHostingMode": {
                        "value": "[parameters('searchHostingMode')]"
                    },
                    "umiId": {
                        "value": "[parameters('umiId')]"
                    },
                    "name": {
                        "value": "[parameters('name')]"
                    },
                    "location": {
                        "value": "[parameters('location')]"
                    },
                    "resourceGroupName": {
                        "value": "[parameters('resourceGroupName')]"
                    },
                    "resourceGroupId": {
                        "value": "[parameters('resourceGroupId')]"
                    },
                    "sku": {
                        "value": "[parameters('sku')]"
                    },
                    "tagValues": {
                        "value": "[parameters('tagValues')]"
                    },
                    "virtualNetworkType": {
                        "value": "[parameters('virtualNetworkType')]"
                    },
                    "vnet": {
                        "value": "[parameters('vnet')]"
                    },
                    "ipRules": {
                        "value": "[parameters('ipRules')]"
                    },
                    "identity": {
                        "value": "[parameters('identity')]"
                    }
                }
            },
            "condition": "[and(not(parameters('storageEnabled')), parameters('searchEnabled'))]"
        }
    ]
}