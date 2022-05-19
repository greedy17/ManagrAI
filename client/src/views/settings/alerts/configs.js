
const CLOSE_DATE_PASSED = {
    title: "Close Date Passed",
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
    title: "Update Forecast", // Change
    user: null,
    isActive: true,
    resourceType: "Opportunity",
    newGroups: [
        {
            groupCondition: "AND",
            newOperands: [
                {
                    operandCondition: "AND",
                    operandIdentifier: "ForecastCategoryName", // Change
                    operandOperator: "!=", // Change
                    operandValue: 'Commit', // Change
                    operandType: "FIELD",
                    operandOrder: 0,
                    dataType: "DATE",
                    group: "",
                },
                {
                    operandCondition: "AND",
                    operandIdentifier: "CloseDate", // Change
                    operandOperator: "<=", // Change
                    operandValue: 14, // Change
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
        // Change V
        bindings: [
            " Opportunity.Name ",
            " Opportunity.CloseDate ",
            " Opportunity.ForecastCategoryName ",
            " Opportunity.NextStep ",
        ],
        // Change V
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
    title: "Deal Rotting", // Change
    user: null,
    isActive: true,
    resourceType: "Opportunity",
    newGroups: [
        {
            groupCondition: "AND",
            newOperands: [
                {
                    operandCondition: "AND",
                    operandIdentifier: "LastActivityDate", // Change
                    operandOperator: "<", // Change
                    operandValue: -30, // Change
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
        // Change V
        bindings: [
            " __Recipient.full_name ",
            " Opportunity.Name ",
            " Opportunity.LastActivityDate ",
        ],
        // Change V
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
    title: "Close Date Approaching", // Change
    user: null,
    isActive: true,
    resourceType: "Opportunity",
    newGroups: [
        {
            groupCondition: "AND",
            newOperands: [
                {
                    operandCondition: "AND",
                    operandIdentifier: "CloseDate", // Change
                    operandOperator: "<=", // Change
                    operandValue: 7, // Change
                    operandType: "FIELD",
                    operandOrder: 0,
                    dataType: "DATE",
                    group: "",
                },
                {
                    operandCondition: "AND",
                    operandIdentifier: "CloseDate", // Change
                    operandOperator: ">", // Change
                    operandValue: -1, // Change
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
        // Change V
        bindings: [
            " __Recipient.full_name ",
            " Opportunity.Name ",
            " Opportunity.CloseDate ",
        ],
        // Change V
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

const ALL_CONFIGS = {
    CLOSE_DATE_PASSED,
    UPDATE_FORECAST,
    DEAL_ROTTING
}

export default ALL_CONFIGS;