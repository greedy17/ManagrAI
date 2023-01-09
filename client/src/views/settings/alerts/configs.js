const CLOSE_DATE_PASSED = {
    title: "Close Date Passed",
    subtitle: "View and update all Opportunities with a passed close date",
    user: null,
    isActive: true,
    crm: 'SALESFORCE',
    resourceType: "Opportunity",
    newGroups: [
        {
            groupCondition: "AND",
            newOperands: [
                {
                    operandCondition: "AND",
                    operandIdentifier: "CloseDate",
                    operandOperator: ">=",
                    operandValue: "-200",
                    operandType: "FIELD",
                    operandOrder: 0,
                    dataType: "DATE",
                    group: "",
                },
                {
                    operandCondition: "AND",
                    operandIdentifier: "CloseDate",
                    operandOperator: "<=",
                    operandValue: "-1",
                    operandType: "FIELD",
                    operandOrder: 1,
                    dataType: "DATE",
                    group: "",
                },
            ],
            groupOrder: 0,
            template: "",
        }
    ],
    messageTemplate: {
        bindings: [
            " __Recipient.full_name ",
            " Opportunity.Name ",
            " Opportunity.CloseDate ",
        ],
        body: "<strong>Opportunity Name</strong> \n { Opportunity.Name } <br><br> <strong>Close Date</strong> \n { Opportunity.CloseDate }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [0],
            recurrenceDay: "0",
            recipients: ["default"],
            alertTargets: ["SELF"],
            recipientType: "SLACK_CHANNEL",
            alertTemplateId: "",
            template: "",
        }
    ],
    alertLevel: "ORGANIZATION",
}

const CLOSE_DATE_PASSED_HUBSPOT = {
    title: "Close Date Passed",
    subtitle: "View and update all Deals with a passed close date",
    user: null,
    isActive: true,
    crm: 'HUBSPOT',
    resourceType: "Deal",
    newGroups: [
        {
            groupCondition: "AND",
            newOperands: [
                {
                    operandCondition: "AND",
                    operandIdentifier: "closedate",
                    operandOperator: ">=",
                    operandValue: "-200",
                    operandType: "FIELD",
                    operandOrder: 0,
                    dataType: "DATE",
                    group: "",
                },
                {
                    operandCondition: "AND",
                    operandIdentifier: "closedate",
                    operandOperator: "<=",
                    operandValue: "-1",
                    operandType: "FIELD",
                    operandOrder: 1,
                    dataType: "DATE",
                    group: "",
                },
            ],
            groupOrder: 0,
            template: "",
        }
    ],
    messageTemplate: {
        bindings: [
            " __Recipient.full_name ",
            " Deal.dealname ",
            " Deal.closedate ",
        ],
        body: "<strong>Deal Name</strong> \n { Deal.dealname } <br><br> <strong>Close Date</strong> \n { Deal.closedate }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [0],
            recurrenceDay: "0",
            recipients: ["default"],
            alertTargets: ["SELF"],
            recipientType: "SLACK_CHANNEL",
            alertTemplateId: "",
            template: "",
        }
    ],
    alertLevel: "ORGANIZATION",
}

const NINETY_DAY_PIPELINE = {
    title: "90 Day Pipeline",
    subtitle: 'Update your Pipeline',
    user: null,
    isActive: true,
    crm: 'SALESFORCE',
    resourceType: "Opportunity",
    newGroups: [
        {
            groupCondition: "AND",
            newOperands: [
                // {
                //     operandCondition: "AND",
                //     operandIdentifier: "ForecastCategoryName",
                //     operandOperator: "<=",
                //     operandValue: 'Commit',
                //     operandType: "FIELD",
                //     operandOrder: 0,
                //     dataType: "STRING",
                //     group: "",
                // },
                {
                    operandCondition: "AND",
                    operandIdentifier: "CloseDate",
                    operandOperator: "<=",
                    operandValue: "90",
                    operandType: "FIELD",
                    operandOrder: 0,
                    dataType: "DATE",
                    group: "",
                },
                {
                    operandCondition: "AND",
                    operandIdentifier: "CloseDate",
                    operandOperator: ">=",
                    operandValue: "0",
                    operandType: "FIELD",
                    operandOrder: 1,
                    dataType: "DATE",
                    group: "",
                },
            ],
            groupOrder: 0,
            template: "",
        }
    ],
    messageTemplate: {
        bindings: [
            " Opportunity.Name ",
            " Opportunity.CloseDate ",
            " Opportunity.StageName ",
            " Opportunity.LastActivityDate ",
        ],
        body: "<strong>Opportunity Name</strong> \n { Opportunity.Name } <br><br> <strong>Close Date</strong> \n { Opportunity.CloseDate } <br><br> <strong>Stage</strong> \n { Opportunity.StageName } <br><br> <strong>Last Activity</strong> \n { Opportunity.LastActivityDate }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [0],
            recurrenceDay: "0",
            recipients: ["default"],
            alertTargets: ["SELF"],
            recipientType: "SLACK_CHANNEL",
            alertTemplateId: "",
            template: "",
        }
    ],
    alertLevel: "ORGANIZATION",
}

const NINETY_DAY_PIPELINE_HUBSPOT = {
    title: "90 Day Pipeline",
    subtitle: 'Update your Pipeline',
    user: null,
    isActive: true,
    crm: 'HUBSPOT',
    resourceType: "Deal",
    newGroups: [
        {
            groupCondition: "AND",
            newOperands: [
                {
                    operandCondition: "AND",
                    operandIdentifier: "closedate",
                    operandOperator: "<=",
                    operandValue: "90",
                    operandType: "FIELD",
                    operandOrder: 0,
                    dataType: "DATE",
                    group: "",
                },
                {
                    operandCondition: "AND",
                    operandIdentifier: "closedate",
                    operandOperator: ">=",
                    operandValue: "0",
                    operandType: "FIELD",
                    operandOrder: 1,
                    dataType: "DATE",
                    group: "",
                },
            ],
            groupOrder: 0,
            template: "",
        }
    ],
    messageTemplate: {
        bindings: [
            " Deal.dealname ",
            " Deal.closedate ",
            " Deal.dealstage ",
        ],
        body: "<strong>Deal Name</strong> \n { Deal.dealname } <br><br> <strong>Close Date</strong> \n { Deal.closedate }</strong> <br><br> <strong>Stage</strong> \n { Deal.dealstage }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [0],
            recurrenceDay: "0",
            recipients: ["default"],
            alertTargets: ["SELF"],
            recipientType: "SLACK_CHANNEL",
            alertTemplateId: "",
            template: "",
        }
    ],
    alertLevel: "ORGANIZATION",
}

const DEAL_REVIEW = {
    title: "Deal Review",
    subtitle: 'View and update all Opportunities that havent been worked in the last week',
    user: null,
    isActive: true,
    crm: 'SALESFORCE',
    resourceType: "Opportunity",
    newGroups: [
        {
            groupCondition: "AND",
            newOperands: [
                {
                    operandCondition: "AND",
                    operandIdentifier: "LastModifiedDate", // Select your Amount
                    operandOperator: "<=",
                    operandValue: "-6", // Amount is greater than
                    operandType: "FIELD",
                    operandOrder: 0,
                    dataType: "DATETIME",
                    group: "",
                },
            ],
            groupOrder: 0,
            template: "",
        }
    ],
    messageTemplate: {
        bindings: [
            " __Recipient.full_name ",
            " Opportunity.Name ",
            " Opportunity.LastModifiedDate ",
        ],
        body: "<strong>Opportunity Name</strong> \n { Opportunity.Name } <br><br> <strong>Last Modified Date</strong> \n { Opportunity.LastModifiedDate }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [0, 3],
            recurrenceDay: "0",
            recipients: ["default"],
            alertTargets: ["SELF"],
            recipientType: "SLACK_CHANNEL",
            alertTemplateId: "",
            template: "",
        }
    ],
    alertLevel: "ORGANIZATION",
}

const DEAL_REVIEW_HUBSPOT = {
    title: "Deal Review",
    subtitle: 'View and update all Deals that havent been worked in the last week',
    user: null,
    isActive: true,
    crm: 'HUBSPOT',
    resourceType: "Deal",
    newGroups: [
        {
            groupCondition: "AND",
            newOperands: [
                {
                    operandCondition: "AND",
                    operandIdentifier: "hs_lastmodifieddate", // Select your Amount
                    operandOperator: "<=",
                    operandValue: "-6", // Amount is greater than
                    operandType: "FIELD",
                    operandOrder: 0,
                    dataType: "DATE",
                    group: "",
                },
            ],
            groupOrder: 0,
            template: "",
        }
    ],
    messageTemplate: {
        bindings: [
            " __Recipient.full_name ",
            " Deal.dealname ",
            " Deal.hs_lastmodifieddate ",
        ],
        body: "<strong>Deal Name</strong> \n { Deal.dealname } <br><br> <strong>Last Modified Date</strong> \n { Deal.hs_lastmodifieddate }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [0, 3],
            recurrenceDay: "0",
            recipients: ["default"],
            alertTargets: ["SELF"],
            recipientType: "SLACK_CHANNEL",
            alertTemplateId: "",
            template: "",
        }
    ],
    alertLevel: "ORGANIZATION",
}

const CLOSE_DATE_APPROACHING = {
    title: "Close Date Approaching",
    subtitle: 'View and update all Opportunities with an upcoming close date',
    user: null,
    isActive: true,
    crm: 'SALESFORCE',
    resourceType: "Opportunity",
    newGroups: [
        {
            groupCondition: "AND",
            newOperands: [
                {
                    operandCondition: "AND",
                    operandIdentifier: "CloseDate",
                    operandOperator: "<=",
                    operandValue: "7",
                    operandType: "FIELD",
                    operandOrder: 0,
                    dataType: "DATE",
                    group: "",
                },
                {
                    operandCondition: "AND",
                    operandIdentifier: "CloseDate",
                    operandOperator: ">",
                    operandValue: "-1",
                    operandType: "FIELD",
                    operandOrder: 1,
                    dataType: "DATE",
                    group: "",
                },
            ],
            groupOrder: 0,
            template: "",
        }
    ],
    messageTemplate: {
        bindings: [
            " __Recipient.full_name ",
            " Opportunity.Name ",
            " Opportunity.CloseDate ",
        ],
        body: "<strong>Opportunity Name</strong> \n { Opportunity.Name } <br><br> <strong>Close Date</strong> \n { Opportunity.CloseDate }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [0],
            recurrenceDay: "0",
            recipients: ["default"],
            alertTargets: ["SELF"],
            recipientType: "SLACK_CHANNEL",
            alertTemplateId: "",
            template: "",
        }
    ],
    alertLevel: "ORGANIZATION",
}

const CLOSE_DATE_APPROACHING_HUBSPOT = {
    title: "Close Date Approaching",
    subtitle: 'View and update all Deals with an upcoming close date',
    user: null,
    isActive: true,
    crm: 'HUBSPOT',
    resourceType: "Deal",
    newGroups: [
        {
            groupCondition: "AND",
            newOperands: [
                {
                    operandCondition: "AND",
                    operandIdentifier: "closedate",
                    operandOperator: "<=",
                    operandValue: "7",
                    operandType: "FIELD",
                    operandOrder: 0,
                    dataType: "DATE",
                    group: "",
                },
                {
                    operandCondition: "AND",
                    operandIdentifier: "closedate",
                    operandOperator: ">",
                    operandValue: "-1",
                    operandType: "FIELD",
                    operandOrder: 1,
                    dataType: "DATE",
                    group: "",
                },
            ],
            groupOrder: 0,
            template: "",
        }
    ],
    messageTemplate: {
        bindings: [
            " __Recipient.full_name ",
            " Deal.dealname ",
            " Deal.closedate ",
        ],
        body: "<strong>Deal Name</strong> \n { Deal.dealname } <br><br> <strong>Close Date</strong> \n { Deal.closedate }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [0],
            recurrenceDay: "0",
            recipients: ["default"],
            alertTargets: ["SELF"],
            recipientType: "SLACK_CHANNEL",
            alertTemplateId: "",
            template: "",
        }
    ],
    alertLevel: "ORGANIZATION",
}

const UPCOMING_NEXT_STEP = {
    title: "Upcoming Next Step",
    subtitle: "View and update all Opportunities with Next Steps due this Week",
    user: null,
    isActive: true,
    crm: 'SALESFORCE',
    resourceType: "Opportunity",
    newGroups: [
        {
            groupCondition: "AND",
            newOperands: [
                {
                    operandCondition: "AND",
                    operandIdentifier: "CloseDate",
                    operandOperator: "=",
                    operandValue: '0',
                    operandType: "FIELD",
                    operandOrder: 0,
                    dataType: "DATE",
                    group: "",
                },
            ],
            groupOrder: 0,
            template: "",
        }
    ],
    messageTemplate: {
        bindings: [
            " __Recipient.full_name ",
            " Opportunity.Name ",
        ],
        body: "<strong>Opporunity Name</strong> \n { Opportunity.Name }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [0, 1, 2, 3, 4, 5],
            recurrenceDay: "0",
            recipients: ["default"],
            alertTargets: ["SELF"],
            recipientType: "SLACK_CHANNEL",
            alertTemplateId: "",
            template: "",
        }
    ],
    alertLevel: "ORGANIZATION",
}

const UPCOMING_NEXT_STEP_HUBSPOT = {
    title: "Upcoming Next Step",
    subtitle: "View and update all Deals with Next Steps due this Week",
    user: null,
    isActive: true,
    crm: 'HUBSPOT',
    resourceType: "Deal",
    newGroups: [
        {
            groupCondition: "AND",
            newOperands: [
                {
                    operandCondition: "AND",
                    operandIdentifier: "closedate",
                    operandOperator: "=",
                    operandValue: '0',
                    operandType: "FIELD",
                    operandOrder: 0,
                    dataType: "DATE",
                    group: "",
                },
            ],
            groupOrder: 0,
            template: "",
        }
    ],
    messageTemplate: {
        bindings: [
            " __Recipient.full_name ",
            " Deal.dealname ",
        ],
        body: "<strong>Deal Name</strong> \n { Deal.dealname }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [0, 1, 2, 3, 4, 5],
            recurrenceDay: "0",
            recipients: ["default"],
            alertTargets: ["SELF"],
            recipientType: "SLACK_CHANNEL",
            alertTemplateId: "",
            template: "",
        }
    ],
    alertLevel: "ORGANIZATION",
}

const LARGE_OPPORTUNITIES = {
    title: "Large Opportunities",
    subtitle: "View and update all your Opportunities that exceed a certain amount",
    user: null,
    isActive: true,
    crm: 'SALESFORCE',
    resourceType: "Opportunity",
    newGroups: [
        {
            groupCondition: "AND",
            newOperands: [
                {
                    operandCondition: "AND",
                    operandIdentifier: "",
                    operandOperator: ">",
                    operandValue: 'null',
                    operandType: "FIELD",
                    operandOrder: 0,
                    dataType: "",
                    group: "",
                },
            ],
            groupOrder: 0,
            template: "",
        }
    ],
    messageTemplate: {
        bindings: [
            " __Recipient.full_name ",
            " Opportunity.Name ",
        ],
        body: "<strong>Opportunity Name</strong> \n { Opportunity.Name }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [0, 1, 2, 3, 4, 5],
            recurrenceDay: "0",
            recipients: ["default"],
            alertTargets: ["SELF"],
            recipientType: "SLACK_CHANNEL",
            alertTemplateId: "",
            template: "",
        }
    ],
    alertLevel: "ORGANIZATION",
}

const LARGE_DEALS_HUBSPOT = {
    title: "Large Deals",
    subtitle: "View and update all your Deals that exceed a certain amount",
    user: null,
    isActive: true,
    crm: 'HUBSPOT',
    resourceType: "Deal",
    newGroups: [
        {
            groupCondition: "AND",
            newOperands: [
                {
                    operandCondition: "AND",
                    operandIdentifier: "",
                    operandOperator: ">",
                    operandValue: 'null',
                    operandType: "FIELD",
                    operandOrder: 0,
                    dataType: "",
                    group: "",
                },
            ],
            groupOrder: 0,
            template: "",
        }
    ],
    messageTemplate: {
        bindings: [
            " __Recipient.full_name ",
            " Deal.dealname ",
        ],
        body: "<strong>Deal Name</strong> \n { Deal.dealname }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [0, 1, 2, 3, 4, 5],
            recurrenceDay: "0",
            recipients: ["default"],
            alertTargets: ["SELF"],
            recipientType: "SLACK_CHANNEL",
            alertTemplateId: "",
            template: "",
        }
    ],
    alertLevel: "ORGANIZATION",
}

const TEAM_PIPELINE = {
    title: "Team Pipeline",
    subtitle: "View your entire team’s pipeline of deals closing this month",
    user: null,
    isActive: true,
    crm: 'SALESFORCE',
    resourceType: "Opportunity",
    newGroups: [
        {
            groupCondition: "AND",
            newOperands: [
                {
                    operandCondition: "AND",
                    operandIdentifier: "CloseDate",
                    operandOperator: "<=",
                    operandValue: 30,
                    operandType: "FIELD",
                    operandOrder: 0,
                    dataType: "DATE",
                    group: "",
                },
            ],
            newOperands: [
                {
                    operandCondition: "AND",
                    operandIdentifier: "CloseDate",
                    operandOperator: ">",
                    operandValue: -1,
                    operandType: "FIELD",
                    operandOrder: 0,
                    dataType: "DATE",
                    group: "",
                },
            ],
            groupOrder: 0,
            template: "",
        },

    ],
    messageTemplate: {
        bindings: [
            " __Recipient.full_name ",

        ],
        body: "<strong>Opportunity Name</strong> \n { Opportunity.Name }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "MONTHLY",
            recurrenceDays: [0],
            recurrenceDay: "1",
            recipients: ["default"],
            alertTargets: ["TEAM"],
            recipientType: "SLACK_CHANNEL",
            alertTemplateId: "",
            template: "",
        }
    ],
    alertLevel: "ORGANIZATION",
}

const TEAM_PIPELINE_HUBSPOT = {
    title: "Team Pipeline",
    subtitle: "View your entire team’s pipeline of deals closing this month",
    user: null,
    isActive: true,
    crm: 'HUBSPOT',
    resourceType: "Deal",
    newGroups: [
        {
            groupCondition: "AND",
            newOperands: [
                {
                    operandCondition: "AND",
                    operandIdentifier: "closedate",
                    operandOperator: "<=",
                    operandValue: 30,
                    operandType: "FIELD",
                    operandOrder: 0,
                    dataType: "DATE",
                    group: "",
                },
            ],
            groupOrder: 0,
            template: "",
        },
        {
            groupCondition: "AND",
            newOperands: [
                {
                    operandCondition: "AND",
                    operandIdentifier: "closedate",
                    operandOperator: ">",
                    operandValue: -1,
                    operandType: "FIELD",
                    operandOrder: 0,
                    dataType: "DATE",
                    group: "",
                },
            ],
            groupOrder: 1,
            template: "",
        }
    ],
    messageTemplate: {
        bindings: [
            " __Recipient.full_name ",

        ],
        body: "<strong>Deal Name</strong> \n { Deal.dealname }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "MONTHLY",
            recurrenceDays: [0],
            recurrenceDay: "1",
            recipients: ["default"],
            alertTargets: ["TEAM"],
            recipientType: "SLACK_CHANNEL",
            alertTemplateId: "",
            template: "",
        }
    ],
    alertLevel: "ORGANIZATION",
}

const ALL_CONFIGS = {
    CLOSE_DATE_PASSED,
    CLOSE_DATE_PASSED_HUBSPOT,
    NINETY_DAY_PIPELINE,
    NINETY_DAY_PIPELINE_HUBSPOT,
    DEAL_REVIEW,
    DEAL_REVIEW_HUBSPOT,
    CLOSE_DATE_APPROACHING,
    CLOSE_DATE_APPROACHING_HUBSPOT,
    UPCOMING_NEXT_STEP,
    UPCOMING_NEXT_STEP_HUBSPOT,
    LARGE_OPPORTUNITIES,
    LARGE_DEALS_HUBSPOT,
    TEAM_PIPELINE,
    TEAM_PIPELINE_HUBSPOT,
}

export default ALL_CONFIGS;