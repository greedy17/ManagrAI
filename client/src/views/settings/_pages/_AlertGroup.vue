<template>
  <div class="alert-group-row">
    <span class="alert-group-row--label">Alert Group</span>
    <div class="alert-group-row__condition">
      <label class="alert-group-row__condition-label">AND</label>
      <ToggleCheckBox
        @input="
          selectedCondition == 'AND' ? (selectedCondition = 'OR') : (selectedCondition = 'AND')
        "
        :value="selectedCondition == 'AND'"
        offColor="#199e54"
        onColor="#199e54"
      />
      <label class="alert-group-row__condition-label">OR</label>
    </div>
    <div class="alert-group-row__operands">
      <template v-for="(alertOperand, i) in form.field.alertOperand.groups">
        <AlertOperandRow :resourceType="resourceType" :key="i" :form.sync="alertOperand" />
      </template>
      <button @click="addOperandForm">+ Opperand</button>
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
import { AlertOperandForm, AlertGroupForm } from '@/services/alerts/'

export default {
  /**
   * NB VUE usually throws an error if the child component is affecting the parent props
   * in this case we are affecting the parent props but no error is thrown because we are changing
   * the object multiple levels deep (this current implementation could be seen as incorrect)
   *
   */
  name: 'AlertGroup',
  components: { ToggleCheckBox, AlertOperandRow },

  props: {
    form: { type: AlertGroupForm },
    resourceType: { type: String },
  },
  data() {
    return {
      selectedCondition: 'AND',
    }
  },
  watch: {
    selectedCondition: {
      immediate: true,
      handler(val) {
        this.form.field.groupCondition.value = val
      },
    },
  },
  async created() {},
  methods: {
    addOperandForm() {
      this.form.addToArray('alertOperand', new AlertOperandForm())
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
.alert-group-row {
  @include standard-border();
  margin: 0.5rem;
  padding: 0.5rem 1rem;
  display: flex;
  flex-direction: column;
  overflow: none;
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
