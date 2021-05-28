<template>
  <div class="alert-summary">
    <div class="box">
      <div class="box__header">
        <div class="box__header-title"></div>
        <div class="box__header-subtitle"></div>
      </div>
      <div class="box__content">
        <h2>
          {{ form.value.title ? form.value.title : 'No title' }} for {{ form.value.resourceType }}
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
            Will run every <u><b>week</b></u> on
            <u
              ><b>{{ config._recurrenceDay ? config._recurrenceDay.key : '' }}</b></u
            >
            and will check all <u><b>users</b></u> resources but only alert
            <u
              ><b>{{ config._recipients ? config._recipients.key : '' }}</b></u
            >
          </div>
          <div
            class="box__content-recipient-group__recipient-group__recipient"
            v-else-if="config.recurrenceFrequency == 'MONTHLY'"
          >
            Will run every <u><b>Month</b></u> on the
            <u
              ><b>{{ config.recurrenceDay | numberSuffix }}</b></u
            >
            and will check <u><b>all users'</b></u> resources but only alert
            <u
              ><b>{{ config._recipients ? config._recipients.key : '' }}</b></u
            >
          </div>

          <div
            class="box__content-recipient-group__recipient-group__conditions"
            :key="i"
            v-for="(group, i) in form.value.alertGroups"
          >
            <span class="box__content-recipient-group__recipient-group__conditions-condition">
              {{ group.groupOrder == 0 ? 'If ' : `${group.groupCondition} ` }} Group
              {{ ` ${i + 1}` }}
            </span>

            <div
              class="box__content-recipient-group__recipient-group__conditions__operands"
              :key="key"
              v-for="(operandRow, key) in group.alertOperands"
            >
              <span
                class="box__content-recipient-group__recipient-group__conditions__operands-condition"
                v-if="key != 0"
              >
                {{ operandRow.operandCondition }}
              </span>
              <div
                style="display:flex;justify-content:space-evenly;"
                class="box__content-recipient-group__recipient-group__conditions__operands-operand"
              >
                <span>{{ form.value.resourceType }} </span>
                <span>
                  {{
                    operandRow._operandIdentifier
                      ? operandRow._operandIdentifier.referenceDisplayLabel
                      : ''
                  }}</span
                >
                <span>{{
                  operandRow._operandOperator ? operandRow._operandOperator.label : ''
                }}</span>
                <!-- If this is a monthly alert (with a datetime or date type) show the calculated period -->

                <span
                  v-if="
                    operandRow._operandIdentifier &&
                      (operandRow._operandIdentifier.dataType == 'Date' ||
                        operandRow._operandIdentifier.dataType == 'DateTime')
                  "
                >
                  {{
                    operandDateValToStr(
                      config.recurrenceFrequency,
                      config.recurrenceDay,
                      operandRow.operandValue,
                    )
                  }}
                  <small><em>(or current month at run time)</em></small>
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
        let m = moment()
          .startOf('isoweek')
          .add(day, 'd')
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
.alert-group-row {
  @include standard-border();
  margin: 0.5rem;
  padding: 0.5rem 1rem;
  display: flex;
  flex-direction: column;
  overflow: visible;
  &--label {
    @include muted-font();
    top: -1.1rem;
    position: relative;
  }
}
.alert-group-row__condition {
  position: relative;
  top: -2.4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  &-label {
    @include muted-font();
    margin: 0 0.5rem;
  }
}
.box__content-recipient-group__recipient-group {
  padding: 1rem;
  border-bottom: 1px solid gray;
}
</style>
