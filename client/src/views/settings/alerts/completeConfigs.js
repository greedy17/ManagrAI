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
            recurrenceDays: ["0"],
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
            recurrenceDays: ["0"],
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
    subtitle: 'Close date within 7 days',
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
            recurrenceDays: ["4"],
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
    subtitle: 'Closing within 7 days',
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
            recurrenceDays: ["4"],
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
            recurrenceDays: ["1"],
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
                    operandValue: "THIS_MONTH",
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
            " Deal.closedate ",
        ],
        body: "<strong>Deal Name</strong> \n { Deal.dealname }\n\n<strong>Close Date</strong> \n { Deal.closedate }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: ["1"],
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
            recurrenceDays: ["3"],
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
    subtitle: 'Closing within 7 days & no recent updates',
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
            recurrenceDays: ["2"],
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
    subtitle: 'Closing within 7 days & no recent updates',
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
            recurrenceDays: ["2"],
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

const ALL_CONFIGS = {
    CLOSE_DATE_PASSED,
    CLOSE_DATE_PASSED_HUBSPOT,
    CLOSE_DATE_APPROACHING,
    CLOSE_DATE_APPROACHING_HUBSPOT,
    CLOSING_THIS_MONTH,
    CLOSING_THIS_MONTH_HUBSPOT,
    CLOSING_THIS_QUARTER,
    DEAL_REVIEW,
    DEAL_REVIEW_HUBSPOT,
}

export default ALL_CONFIGS;