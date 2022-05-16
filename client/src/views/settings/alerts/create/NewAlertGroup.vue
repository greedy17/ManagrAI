<template>
  <div class="alert-group-row">
    <div class="alert-group-row__operands">
      <div
        :key="i"
        v-for="(alertOperand, i) in form.field.alertOperands.groups"
        class="alert-group-row__operands__row rows"
      >
        <NewAlertOperandRow
          @remove-operand="onRemoveOperand(i)"
          :resourceType="resourceType"
          :form.sync="alertOperand"
        />
      </div>
    </div>
  </div>
</template>

<script>
/**
 * Components
 * */
//Internal
import NewAlertOperandRow from '@/views/settings/alerts/create/NewAlertOperandRow'

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
  name: 'NewAlertGroup',
  components: { NewAlertOperandRow },

  props: {
    form: { type: AlertGroupForm },
    canRemove: { type: Boolean },
    index: { type: Number },
    resourceType: { type: String },
  },
  data() {
    return {}
  },
  async created() {},
  methods: {
    addOperandForm() {
      const order = this.form.field.alertOperands.groups.length
      if (order >= 3) {
        this.$Alert.alert({ message: 'You can only add 3 items per group', timeout: 2000 })
        return
      }
      this.form.addToArray('alertOperands', new AlertOperandForm())
      this.form.field.alertOperands.groups[order].field.operandOrder.value = order
    },
    onRemoveOperand(i) {
      if (this.form.field.alertOperands.groups.length - 1 <= 0) {
        return
      }
      const order = this.form.field.alertOperands.groups[i].field.operandOrder.value
      this.form.removeFromArray('alertOperands', i)
      let greaterThan = this.form.field.alertOperands.groups.slice(i)
      greaterThan.forEach((el, index) => {
        el.field.operandOrder.value = order + index
      })
    },
  },
  computed: {
    selectedCondition: {
      get() {
        return this.form.field.groupCondition.value
      },
      set(val) {
        this.form.field.groupCondition.value = val
      },
    },
  },
  beforeMount() {
    this.addOperandForm()
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
  display: flex;
  flex-direction: column;
  overflow: visible;
  &__operands {
    &__row {
      display: flex;
    }
  }
}
.rows {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
