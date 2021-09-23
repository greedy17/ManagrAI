<template>
  <div class="alert-summary">
    <div>
      <div class="alert__summary">
        <h2 style="color: #beb5cc; text-align: center">
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
            This alert will run every <b style="color: #ff7649">week</b> on
            <b style="color: #ff7649">{{
              config._recurrenceDay ? config._recurrenceDay.key : ''
            }}</b>
            , checking

            <b style="color: #ff7649">{{ getListOfTargets(config._alertTargets) }}</b>

            pipelines, and alerting

            <b style="color: #ff7649">{{ getListOfRecipients(config._recipients) }}</b>
          </div>
          <div
            class="box__content-recipient-group__recipient-group__recipient"
            v-else-if="config.recurrenceFrequency == 'MONTHLY'"
          >
            This alert will run every <b style="color: #ff7649">Month</b> on the

            <b style="color: #ff7649">{{ config.recurrenceDay | numberSuffix }}</b>

            , checking

            <b style="color: #ff7649">{{ getListOfTargets(config._alertTargets) }}</b>

            pipelines, and alerting
            <b style="color: #ff7649">{{ config._recipients }}</b>
            <b style="color: #ff7649">{{ getListOfRecipients(config._recipients) }}</b>
          </div>

          <div
            style="margin-top: 1rem"
            class="box__content-recipient-group__recipient-group__conditions"
            :key="i"
            v-for="(group, i) in form.value.alertGroups"
          >
            <span class="box__content-recipient-group__recipient-group__conditions-condition">
              {{
                group.groupOrder == 0
                  ? `It will only run for ${form.value.resourceType}'s that meet the following criteria: `
                  : `${group.groupCondition} `
              }}
            </span>

            <div
              style="margin-top: 1rem; color: #ff7649"
              class="box__content-recipient-group__recipient-group__conditions__operands"
              :key="key"
              v-for="(operandRow, key) in group.alertOperands"
            >
              <span
                class="
                  box__content-recipient-group__recipient-group__conditions__operands-condition
                "
                v-if="key != 0"
              >
                {{ operandRow.operandCondition }}
              </span>
              <div
                style="display: flex; justify-content: space-evenly"
                class="box__content-recipient-group__recipient-group__conditions__operands-operand"
              >
                <!-- <span>{{ form.value.resourceType }} </span> -->
                <span>
                  {{
                    operandRow._operandIdentifier
                      ? operandRow._operandIdentifier.referenceDisplayLabel
                      : ''
                  }}</span
                >
                <span>{{ operandRow._operandOperator.value }}</span>
                <!-- If this is a monthly alert (with a datetime or date type) show the calculated period -->

                <span
                  v-if="
                    operandRow._operandIdentifier &&
                    (operandRow._operandIdentifier.dataType == 'Date' ||
                      operandRow._operandIdentifier.dataType == 'DateTime')
                  "
                >
                  <!-- <span v-if="operandRow.operandValue === 0">is the current day</span>
                  <span v-else-if="operandRow.operandValue === 1">is the next</span>
                  <span v-else-if="operandRow.operandValue === -1">has passed</span> -->

                  <!-- {{
                    operandDateValToStr(
                      config.recurrenceFrequency,
                      config.recurrenceDay,
                      operandRow.operandValue,
                    )
                  }} -->
                  <span>{{ changeNeg(operandRow.operandValue) }} days </span>
                  <span>{{
                    checkVal(operandRow.operandValue) ? ' in the past' : ' in the future'
                  }}</span>
                </span>
                <!-- If this is a weekly alert (with a datetime or date type show) the calculated period -->
                <span
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
                <span v-else>
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
import { AlertOperandForm, AlertGroupForm, AlertTemplateForm } from '@/services/alerts/'
import moment from 'moment'

export default {
  /**
   * NB VUE usually throws an error if the child component is affecting the parent props
   * in this case we are affecting the parent props but no error is thrown because we are changing
   * the object multiple levels deep (this current implementation could be seen as incorrect)
   *
   */
  name: 'AlertSummary',
  components: {},

  props: {
    form: { type: AlertTemplateForm },
  },
  data() {
    return {
      moment,
    }
  },
  watch: {},
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
    operandDateValToStr(frequency, day, diffValue) {
      /**
       * Helper for converting the selected recurrence frequency to
       * a real date for use in the SUMMARY COMPONENT
       *
       * */

      if (frequency == 'MONTHLY') {
        // get current date start of month
        let d = moment().startOf('month')
        // get the selected day of the month (-1)
        let selectedD = d.add(day - 1, 'd').add(diffValue, 'd')
        // return diff based on operand value
        return selectedD.format('MM/DD')
      } else {
        // assume weekly
        // get todays weekday (as iso 1-7)
        let m = moment().startOf('isoweek').add(day, 'd')
        m.add(diffValue, 'd')
        return m.format('MM/DD')
      }
    },
  },
  computed: {},
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
// .alert-group-row {
//   // @include standard-border();
//   margin: 0.5rem;
//   padding: 0.5rem 1rem;
//   display: flex;
//   flex-direction: column;
//   overflow: visible;
//   &--label {
//     @include muted-font();
//     top: -1.1rem;
//     position: relative;
//   }
// }
// .alert-group-row__condition {
//   position: relative;
//   top: -2.4rem;
//   display: flex;
//   align-items: center;
//   justify-content: center;
//   &-label {
//     @include muted-font();
//     margin: 0 0.5rem;
//   }
// }
.alert__summary {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}
</style>
