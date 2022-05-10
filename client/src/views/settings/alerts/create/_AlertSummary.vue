<template>
  <div class="alert-summary">
    <div>
      <div class="alert__summary">
        <h2 style="text-align: center">
          {{ form.value.title ? form.value.title : 'No title' }}
        </h2>

        <div
          class="box__content-recipient-group__recipient-group"
          :key="key"
          v-for="(config, key) in form.value.alertConfig"
        >
          <div
            class="box__content-recipient-group__recipient-group__recipient"
            v-if="config.recurrenceFrequency == 'WEEKLY'"
          >
            This alert will run every <b style="color: #199e54">week</b> on
            <b style="color: #199e54">{{
              config._recurrenceDay ? config._recurrenceDay.key : ''
            }}</b>
            , checking

            <b style="color: #199e54">{{ getListOfTargets(config._alertTargets) }}</b>

            pipelines, and alerting
            <b v-if="config.recipientType === 'SLACK_CHANNEL'" style="color: #199e54">{{
              config._recipients.name
            }}</b>
            <b v-else style="color: #199e54">{{ getListOfRecipients(config._recipients) }}</b>
          </div>
          <div
            class="box__content-recipient-group__recipient-group__recipient"
            v-else-if="config.recurrenceFrequency == 'MONTHLY'"
          >
            This alert will run every <b style="color: #199e54">Month</b> on the

            <b style="color: #199e54">{{ addSuffix(config.recurrenceDay) }}</b>

            , checking

            <b style="color: #199e54">{{ getListOfTargets(config._alertTargets) }}</b>

            pipelines, and alerting
            <b v-if="config.recipientType === 'SLACK_CHANNEL'" style="color: #199e54">{{
              config._recipients.nameNormalized
            }}</b>
            <b v-else style="color: #199e54">{{ getListOfRecipients(config._recipients) }}:</b>
          </div>

          <div style="margin-top: 1rem" :key="i" v-for="(group, i) in form.value.alertGroups">
            <span class="condition">
              {{ group.groupOrder == 0 ? '' : `${group.groupCondition} ` }}
            </span>

            <div
              class="box__content-recipient-group__recipient-group__conditions__operands"
              :key="key"
              v-for="(operandRow, key) in group.alertOperands"
            >
              <span class="condition" v-if="key != 0">
                {{ operandRow.operandCondition }}
              </span>
              <div
                style="display: flex; justify-content: space-evenly"
                class="box__content-recipient-group__recipient-group__conditions__operands-operand"
              >
                <span class="green__item">
                  {{
                    operandRow._operandIdentifier
                      ? operandRow._operandIdentifier.referenceDisplayLabel
                      : ''
                  }}</span
                >
                <span class="green__item">{{ operandRow._operandOperator.label }}</span>
                <!-- If this is a monthly alert (with a datetime or date type) show the calculated period -->

                <span
                  class="green__item"
                  v-if="
                    operandRow._operandIdentifier &&
                    (operandRow._operandIdentifier.dataType == 'Date' ||
                      operandRow._operandIdentifier.dataType == 'DateTime')
                  "
                >
                  <span>{{ changeNeg(operandRow.operandValue) }} days </span>
                  <span>{{
                    checkVal(operandRow.operandValue) ? ' in the past' : ' in the future'
                  }}</span>
                </span>
                <!-- If this is a weekly alert (with a datetime or date type show) the calculated period -->
                <span
                  class="green__item"
                  v-else-if="
                    operandRow._operandIdentifier &&
                    operandRow._operandIdentifier.dataType == 'Picklist'
                  "
                  >{{
                    operandRow._operandValue
                      ? operandRow._operandValue.label
                      : operandRow.operandValue
                  }}</span
                >
                <span class="green__item" v-else>
                  {{ operandRow.operandValue }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="box__footer"></div>
    </div>
  </div>
</template>

<script>
/**
 * Components
 * */
// Pacakges

//Internal

/**
 * Services
 */
import { AlertTemplateForm } from '@/services/alerts/'
import moment from 'moment'

export default {
  /**
   * NB VUE usually throws an error if the child component is affecting the parent props
   * in this case we are affecting the parent props but no error is thrown because we are changing
   * the object multiple levels deep (this current implementation could be seen as incorrect)
   *
   */
  name: 'AlertSummary',
  props: {
    form: { type: AlertTemplateForm },
  },
  data() {
    return {
      moment,
    }
  },
  async created() {},
  methods: {
    checkVal(val) {
      if (val < 0) {
        return true
      } else {
        return false
      }
    },
    changeNeg(val) {
      if (val < 0) {
        return val * -1
      } else {
        return val
      }
    },
    addSuffix(num) {
      if ((num > 3 && num < 21) || (num > 23 && num < 31)) {
        return num + 'th'
      } else if (num == 1 || num == 21 || num == 31) {
        return num + 'st'
      } else if (num == 2 || num == 22) {
        return num + 'nd'
      } else if (num == 3 || num == 23) {
        return num + 'rd'
      }
    },
    getListOfTargets(targets) {
      if (targets && targets.length) {
        return targets
          .map((opt) => {
            return opt.id == 'SELF' ? 'Your' : opt.fullName + "'s"
          })
          .join(', ')
      }
    },
    getListOfRecipients(targets) {
      if (targets && targets.length) {
        return targets
          .map((opt) => {
            return opt.id == 'SELF' ? 'You' : opt.fullName + "'s"
          })
          .join(', ')
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/forms';
@import '@/styles/emails';
@import '@/styles/sidebars';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';
@import '@/styles/buttons';
.alert__summary {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}
.condition {
  display: flex;
  align-items: center;
  justify-content: center;
}
.green__item {
  padding: 0.5rem 1rem;
  margin: 0.5rem;
  background-color: $panther-orange;
  border: 2px solid $panther-orange;
  border-radius: 0.33rem;

  text-align: center;
  filter: drop-shadow(4px 2px 4px black);
}
</style>
