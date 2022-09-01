const CLOSE_DATE_PASSED = {
    title: "Close Date Passed",
    subtitle: "View and update all Opportunities with a passed close date",
    user: null,
    isActive: true,
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
        body: "Hey <strong>{ __Recipient.full_name }</strong>, your deal <strong>{ Opportunity.Name }</strong> has a passed close date of <strong>{ Opportunity.CloseDate }</strong>. Please update it!",
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
        body: "<strong>{ Opportunity.Name }</strong> has a Close Date of <strong>{ Opportunity.CloseDate }</strong> \n \n <strong>Stage</strong>: { Opportunity.StageName } \n \n <strong>Last Activity</strong>: { Opportunity.LastActivityDate }",
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
        body: "Hey <strong>{ __Recipient.full_name }</strong>, your Opp <strong>{ Opportunity.Name }</strong> hasnt been updated since <strong>{ Opportunity.LastModifiedDate }</strong>",
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
        body: "Hey <strong>{ __Recipient.full_name }</strong>, your deal <strong>{ Opportunity.Name }</strong> has an upcoming close date of <strong>{ Opportunity.CloseDate }</strong>. Please update it!",
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
        body: "Hey <strong>{ __Recipient.full_name }</strong>, your deal <strong>{ Opportunity.Name }</strong> has an upcoming Next Step Date due this week.",
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

const REQUIRED_FIELD_EMPTY = {
    title: "Required Field Empty",
    subtitle: "View and update all Opportunities with required fields that have not been filled out",
    user: null,
    isActive: true,
    resourceType: "Opportunity",
    newGroups: [
        {
            groupCondition: "AND",
            newOperands: [
                {
                    operandCondition: "AND",
                    operandIdentifier: "",
                    operandOperator: "=",
                    operandValue: 'null',
                    operandType: "FIELD",
                    operandOrder: 0,
                    dataType: "STRING",
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
        body: "Hey <strong>{ __Recipient.full_name }</strong>, your deal <strong>{ Opportunity.Name }</strong> has a required field that has not been filled out.",
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
        body: "Hey <strong>{ __Recipient.full_name }</strong>, your deal <strong>{ Opportunity.Name }</strong> is a large opportunity.",
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

const ALL_CONFIGS = {
    CLOSE_DATE_PASSED,
    NINETY_DAY_PIPELINE,
    DEAL_REVIEW,
    CLOSE_DATE_APPROACHING,
    UPCOMING_NEXT_STEP,
    REQUIRED_FIELD_EMPTY,
    LARGE_OPPORTUNITIES,
}

export default ALL_CONFIGS;