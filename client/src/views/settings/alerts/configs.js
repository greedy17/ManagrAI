import { DateTime } from "luxon"

const CLOSE_DATE_PASSED = {
    title: "Close Date Passed",
    subtitle: "Close date is in the past",
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
            " Opportunity.Name ",
            " Opportunity.CloseDate ",
        ],
        body: "<strong>Opportunity Name</strong> \n { Opportunity.Name }\n\n<strong>Close Date</strong> \n { Opportunity.CloseDate }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [],
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
    subtitle: "Close date is in the past",
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
            " Deal.dealname ",
            " Deal.closedate ",
        ],
        body: "<strong>Deal Name</strong> \n { Deal.dealname }\n\n<strong>Close Date</strong> \n { Deal.closedate }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [],
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

const THIRTY_DAY_PIPELINE = {
    title: "30 Day Pipeline",
    subtitle: 'Rolling 30 day pipeline based on closed date',
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
                    operandValue: "30",
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
        body: "<strong>Opportunity Name</strong> \n { Opportunity.Name }\n\n<strong>Close Date</strong> \n { Opportunity.CloseDate }\n\n<strong>Stage</strong> \n { Opportunity.StageName }\n\n<strong>Last Activity</strong> \n { Opportunity.LastActivityDate }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [],
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

const THIRTY_DAY_PIPELINE_HUBSPOT = {
    title: "30 Day Pipeline",
    subtitle: 'Rolling 30 day pipeline based on closed date',
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
                    operandValue: "30",
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
        body: "<strong>Deal Name</strong> \n { Deal.dealname }\n\n<strong>Close Date</strong> \n { Deal.closedate }</strong>\n\n<strong>Stage</strong> \n { Deal.dealstage }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [],
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
    subtitle: 'Closing within 14 days & no recent updates',
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
                {
                    operandCondition: "AND",
                    operandIdentifier: "CloseDate",
                    operandOperator: "<=",
                    operandValue: "14",
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
            " Opportunity.Name ",
            " Opportunity.LastModifiedDate ",
        ],
        body: "<strong>Opportunity Name</strong> \n { Opportunity.Name }\n\n<strong>Last Modified Date</strong> \n { Opportunity.LastModifiedDate }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [],
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
    subtitle: 'Closing within 14 days & no recent updates',
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
                {
                    operandCondition: "AND",
                    operandIdentifier: "closedate",
                    operandOperator: "<=",
                    operandValue: "14",
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
            " Deal.dealname ",
            " Deal.hs_lastmodifieddate ",
        ],
        body: "<strong>Deal Name</strong> \n { Deal.dealname }\n\n<strong>Last Modified Date</strong> \n { Deal.hs_lastmodifieddate }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [],
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
    subtitle: 'Close date within 14 days',
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
            " Opportunity.Name ",
            " Opportunity.CloseDate ",
        ],
        body: "<strong>Opportunity Name</strong> \n { Opportunity.Name }\n\n<strong>Close Date</strong> \n { Opportunity.CloseDate }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [],
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
    subtitle: 'Close date within 14 days',
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
            " Deal.dealname ",
            " Deal.closedate ",
        ],
        body: "<strong>Deal Name</strong> \n { Deal.dealname }\n\n<strong>Close Date</strong> \n { Deal.closedate }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [],
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
    subtitle: "Next Step is due today",
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
            " Opportunity.Name ",
        ],
        body: "<strong>Opportunity Name</strong> \n { Opportunity.Name }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: ["0", "1", "2", "3", "4", "5"],
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
    subtitle: "Next Step is due today",
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
            " Deal.dealname ",
        ],
        body: "<strong>Deal Name</strong> \n { Deal.dealname }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: ["0", "1", "2", "3", "4", "5"],
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
    subtitle: "Opportunities that exceed a certain amount",
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
            " Opportunity.Name ",
        ],
        body: "<strong>Opportunity Name</strong> \n { Opportunity.Name }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: ["0", "1", "2", "3", "4", "5"],
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
    subtitle: "Deals that exceed a certain amount",
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
            " Deal.dealname ",
        ],
        body: "<strong>Deal Name</strong> \n { Deal.dealname }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: ["0", "1", "2", "3", "4", "5"],
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
    subtitle: "Rolling 30 day team pipeline",
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
            " Opportunity.Name ",
        ],
        body: "<strong>Opportunity Name</strong> \n { Opportunity.Name }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "MONTHLY",
            recurrenceDays: ["0"],
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
    subtitle: "Rolling 30 day team pipeline",
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
            groupOrder: 0,
            template: "",
        },
    ],
    messageTemplate: {
        bindings: [
            " Deal.dealname ",
        ],
        body: "<strong>Deal Name</strong> \n { Deal.dealname }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "MONTHLY",
            recurrenceDays: ["0"],
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

const CLOSING_THIS_MONTH = {
    title: "Closing This Month",
    subtitle: "Opportunities closing this month",
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
                    operandValue: 'THIS_MONTH',
                    operandType: "FIELD",
                    operandOrder: 0,
                    dataType: "String",
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
        ],
        body: "<strong>Opportunity Name</strong> \n { Opportunity.Name }\n\n<strong>Close Date</strong> \n { Opportunity.CloseDate }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [],
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

const CLOSING_THIS_MONTH_HUBSPOT = {
    title: "Closing This Month",
    subtitle: "Deals closing this month",
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
                    operandOperator: "BETWEEN",
                    operandValue: `${new Date(new Date().getFullYear(), new Date().getMonth(), 1).getTime()};${new Date(new Date().getFullYear(), new Date().getMonth() + 1, 0).getTime()}`,
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
            groupCondition: "OR",
            newOperands: [
                {
                    operandCondition: "AND",
                    operandIdentifier: "closedate",
                    operandOperator: "=",
                    operandValue: "0",
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
            " Deal.dealname ",
            " Deal.closedate ",
        ],
        body: "<strong>Deal Name</strong> \n { Deal.dealname }\n\n<strong>Close Date</strong> \n { Deal.closedate }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [],
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

const CLOSING_NEXT_MONTH = {
    title: "Closing Next Month",
    subtitle: "Opportunities closing next month",
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
                    operandValue: 'NEXT_MONTH',
                    operandType: "FIELD",
                    operandOrder: 0,
                    dataType: "String",
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
        ],
        body: "<strong>Opportunity Name</strong> \n { Opportunity.Name }\n\n<strong>Close Date</strong> \n { Opportunity.CloseDate }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [],
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

const CLOSING_NEXT_MONTH_HUBSPOT = {
    title: "Closing Next Month",
    subtitle: "Deals closing next month",
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
                    operandOperator: "BETWEEN",
                    operandValue: `${new Date(new Date().getFullYear(), new Date().getMonth() + 1, 1).getTime()};${new Date(new Date().getFullYear(), new Date().getMonth() + 2, 0).getTime()}`,
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
            " Deal.dealname ",
            " Deal.closedate ",
        ],
        body: "<strong>Deal Name</strong> \n { Deal.dealname }\n\n<strong>Close Date</strong> \n { Deal.closedate }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [],
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

const CLOSING_THIS_QUARTER = {
    title: "Closing This Quarter",
    subtitle: "Opportunities closing this quarter",
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
                    operandValue: 'THIS_QUARTER',
                    operandType: "FIELD",
                    operandOrder: 0,
                    dataType: "String",
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
        ],
        body: "<strong>Opportunity Name</strong> \n { Opportunity.Name }\n\n<strong>Close Date</strong> \n { Opportunity.CloseDate }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [],
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

// const CLOSING_THIS_QUARTER_HUBSPOT = {
//     title: "Closing This Quarter",
//     subtitle: "Close date's this quarter",
//     user: null,
//     isActive: true,
//     crm: 'HUBSPOT',
//     resourceType: "Deal",
//     newGroups: [
//         {
//             groupCondition: "AND",
//             newOperands: [
//                 {
//                     operandCondition: "AND",
//                     operandIdentifier: "closedate",
//                     operandOperator: "BETWEEN",
//                     operandValue: ';',
//                     operandType: "FIELD",
//                     operandOrder: 0,
//                     dataType: "DATE",
//                     group: "",
//                 },
//             ],
//             groupOrder: 0,
//             template: "",
//         }
//     ],
//     messageTemplate: {
//         bindings: [
//             " Deal.dealname ",
//             " Deal.closedate ",
//         ],
//         body: "<strong>Deal Name</strong> \n { Deal.dealname }\n\n<strong>Close Date</strong> \n { Deal.closedate }",
//     },
//     newConfigs: [
//         {
//             recurrenceFrequency: "WEEKLY",
//             recurrenceDays: [],
//             recurrenceDay: "0",
//             recipients: ["default"],
//             alertTargets: ["SELF"],
//             recipientType: "SLACK_CHANNEL",
//             alertTemplateId: "",
//             template: "",
//         }
//     ],
//     alertLevel: "ORGANIZATION",
// }

const date = new Date();
const firstDay = new Date(date.getFullYear(), date.getMonth(), 1).getTime();
const lastDay = new Date(date.getFullYear(), date.getMonth() + 1, 0).getTime();
// const date = new Date(), y = date.getFullYear(), m = date.getMonth();
// const firstDay = new Date(y, m, 1);
// const lastDay = new Date(y, m + 1, 0);

const ALL_CONFIGS = {
    CLOSE_DATE_PASSED,
    CLOSE_DATE_PASSED_HUBSPOT,
    THIRTY_DAY_PIPELINE,
    THIRTY_DAY_PIPELINE_HUBSPOT,
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
    CLOSING_THIS_MONTH,
    CLOSING_THIS_MONTH_HUBSPOT,
    CLOSING_NEXT_MONTH,
    CLOSING_NEXT_MONTH_HUBSPOT,
    CLOSING_THIS_QUARTER,
}

export default ALL_CONFIGS;