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
            Will run every week on {{ config.recurrenceDay }} and will check all user's resources
            but only alert {{ config._recipients ? config._recipients.key : '' }}
          </div>
          <div
            class="box__content-recipient-group__recipient-group__recipient"
            v-else-if="config.recurrenceFrequency == 'MONTHLY'"
          >
            Will run every Month on the {{ config.recurrenceDay | numberSuffix }} and will check all
            user's resources but only alert
            {{ config._recipients ? config._recipients.key : '' }}
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

                <span
                  v-if="
                    operandRow._operandIdentifier &&
                      (operandRow._operandIdentifier.dataType == 'Date' ||
                        operandRow._operandIdentifier.dataType == 'DateTime')
                  "
                >
                  {{
                    moment()
                      .add(operandRow.operandValue, 'd')
                      .format('MM/DD')
                  }}
                  <em>(or current month at run time)</em>
                </span>
                <span v-else>{{
                  operandRow._operandValue
                    ? operandRow._operandValue.referenceDisplayLabel
                    : operandRow.operandValue
                }}</span>
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
  methods: {},
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
.alert-group-row__operands {
}
</style>
