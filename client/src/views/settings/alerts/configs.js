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
                    operandValue: -200,
                    operandType: "FIELD",
                    operandOrder: 0,
                    dataType: "DATE",
                    group: "",
                },
                {
                    operandCondition: "AND",
                    operandIdentifier: "CloseDate",
                    operandOperator: "<=",
                    operandValue: -1,
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
            recurrenceDay: 0,
            recipients: ["default"],
            alertTargets: ["SELF"],
            recipientType: "SLACK_CHANNEL",
            alertTemplateId: "",
            template: "",
        }
    ],
    alertLevel: "ORGANIZATION",
}

const UPDATE_FORECAST = {
    title: "Update Forecast", 
    subtitle: 'Update your forecast here',
    user: null,
    isActive: true,
    resourceType: "Opportunity",
    newGroups: [
        {
            groupCondition: "AND",
            newOperands: [
                {
                    operandCondition: "AND",
                    operandIdentifier: "ForecastCategoryName", 
                    operandOperator: "!=", 
                    operandValue: 'Commit', 
                    operandType: "FIELD",
                    operandOrder: 0,
                    dataType: "DATE",
                    group: "",
                },
                {
                    operandCondition: "AND",
                    operandIdentifier: "CloseDate", 
                    operandOperator: "<=", 
                    operandValue: 14, 
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
            " Opportunity.ForecastCategoryName ",
            " Opportunity.NextStep ",
        ],
        body: "Please update the forecast for <strong>{ Opportunity.Name }</strong> ! it’s expected to close on <strong>{ Opportunity.CloseDate }</strong> and forecasted as <strong>{ Opportunity.ForecastCategoryName }</strong> - please either move to Commit or update the Close Date.<br><br> <strong>Next Step</strong>: { Opportunity.NextStep }",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [0],
            recurrenceDay: 0,
            recipients: ["default"],
            alertTargets: ["SELF"],
            recipientType: "SLACK_CHANNEL",
            alertTemplateId: "",
            template: "",
        }
    ],
    alertLevel: "ORGANIZATION",
}

const DEAL_ROTTING = {
    title: "Deal Rotting", 
    subtitle: 'View and update all Opportunities that havent been worked in 30 days',
    user: null,
    isActive: true,
    resourceType: "Opportunity",
    newGroups: [
        {
            groupCondition: "AND",
            newOperands: [
                {
                    operandCondition: "AND",
                    operandIdentifier: "LastActivityDate", 
                    operandOperator: "<", 
                    operandValue: -30, 
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
            " Opportunity.LastActivityDate ",
        ],
        body: "Hey  <strong>{ __Recipient.full_name }</strong>, your deal <strong>{ Opportunity.Name }</strong>, hasnt been touched since <strong>{ Opportunity.LastActivityDate }</strong>",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [0],
            recurrenceDay: 0,
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
                    operandValue: 7, 
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
            recurrenceDay: 0,
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
            recurrenceDay: 0,
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
                    operandIdentifier: "CloseDate", 
                    operandOperator: "=", 
                    operandValue: 'null', 
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
        body: "Hey <strong>{ __Recipient.full_name }</strong>, your deal <strong>{ Opportunity.Name }</strong> has a required field that has not been filled out.",
    },
    newConfigs: [
        {
            recurrenceFrequency: "WEEKLY",
            recurrenceDays: [0, 1, 2, 3, 4, 5],
            recurrenceDay: 0,
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
    UPDATE_FORECAST,
    DEAL_ROTTING,
    CLOSE_DATE_APPROACHING,
    UPCOMING_NEXT_STEP,
    REQUIRED_FIELD_EMPTY,
}

export default ALL_CONFIGS;