<template>
  <div class="alert-summary">
    <div class="box">
      <div class="box__header">
        <div class="box__header-title"></div>
        <div class="box__header-subtitle"></div>
      </div>
      <div class="box__content">
        {{ form.value.title }} for {{ form.value.resourceType }}
        <div class="box__content-recipients">
          <p>
            will send to
            <strong :key="key" v-for="(config, key) in form.value.alertConfig"
              >{{ config._recipients ? config._recipients.key : '' }} on day
              {{ config.recurrenceDay }} {{ config.recurrenceFrequency
              }}{{ key != form.value.alertConfig.length - 1 ? ', ' : '' }}</strong
            >
          </p>
          <span> </span>
        </div>
        <div class="box__content-conditions">
          if the following conditions are met,
          <div :key="i" v-for="(group, i) in form.value.alertGroups">
            <span v-if="i != 0">
              {{ group.groupCondition }}
            </span>
            <span>Group {{ i + 1 }}</span>
            <div :key="key" v-for="(operandRow, key) in group.alertOperands">
              <span v-if="key != 0">
                {{ operandRow.operandCondition }}
              </span>
              <div>
                <span>{{
                  operandRow._operandIdentifier
                    ? operandRow._operandIdentifier.referenceDisplayLabel
                    : ''
                }}</span>
                <span>{{
                  operandRow._operandOperator ? operandRow._operandOperator.label : ''
                }}</span>
                <span>{{
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
import ToggleCheckBox from '@thinknimble/togglecheckbox'
//Internal
import AlertOperandRow from '@/views/settings/_pages/_AlertOperandRow'

/**
 * Services
 */
import { AlertOperandForm, AlertGroupForm, AlertTemplateForm } from '@/services/alerts/'

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
    form: { type: AlertGroupForm },
  },
  data() {
    return {}
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
