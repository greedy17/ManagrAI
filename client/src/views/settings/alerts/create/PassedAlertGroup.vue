<template>
  <div class="alert-group-row">
    <!-- <div class="alert-group-row__condition" v-if="form.field.groupOrder.value != 0">
      <label class="alert-group-row__condition-label">AND</label>
      <ToggleCheckBox
        @input="
          selectedCondition == 'AND' ? (selectedCondition = 'OR') : (selectedCondition = 'AND')
        "
        :value="selectedCondition !== 'AND'"
        offColor="#199e54"
        onColor="#199e54"
      />
      <label class="alert-group-row__condition-label">OR</label>
    </div> -->

    <div class="alert-group-row__operands">
      <div
        :key="i"
        v-for="(alertOperand, i) in form.field.alertOperands.groups"
        class="alert-group-row__operands__row rows"
      >
        <PassedAlertOperandRow
          @remove-operand="onRemoveOperand(i)"
          :resourceType="resourceType"
          :form.sync="alertOperand"
        />

        <!-- <div class="add__remove" v-if="form.field.alertOperands.groups.length > 1">
          <button
            class="btn btn--danger btn--icon"
            @click.stop="onRemoveOperand(i)"
            :disabled="form.field.alertOperands.groups.length - 1 <= 0"
          >
            <svg width="24px" height="24px" viewBox="0 0 24 24">
              <use xlink:href="@/assets/images/remove.svg#remove" />
            </svg>
          </button>
          <p class="sub">Remove</p>
        </div>
        <div class="add__remove">
          <button class="btn btn--secondary btn--icon" @click="addOperandForm">
            <svg width="24px" height="24px" viewBox="0 0 24 24">
              <use fill="#199e54" xlink:href="@/assets/images/add.svg#add" />
            </svg>
          </button>
          <p class="sub">Row</p>
        </div> -->
      </div>
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
import PassedAlertOperandRow from '@/views/settings/alerts/create/PassedAlertOperandRow'

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
  name: 'PassedAlertGroup',
  components: { ToggleCheckBox, PassedAlertOperandRow },

  props: {
    form: { type: AlertGroupForm },
    canRemove: { type: Boolean },
    index: { type: Number },
    resourceType: { type: String },
  },
  data() {
    return {}
  },
  watch: {},
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

.btn {
  &--danger {
    @include button-danger();
  }
  &--primary {
    @include primary-button();
  }
  &--secondary {
    @include secondary-button();
  }

  &--icon {
    @include --icon();
  }
}
.alert-group-row {
  display: flex;
  flex-direction: column;
  overflow: visible;
  &__operands {
    &__row {
      display: flex;
      &-remove {
        height: 1rem;
      }
    }
  }
  &--label {
    @include muted-font();
    top: -1.1rem;
    position: relative;
  }
}
.alert-group-row__condition {
  position: relative;
  top: 0rem;
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
.add__remove {
  margin-right: 1.5rem;
  display: flex;
  flex-direction: row;
  margin-bottom: -1rem;
  margin-left: -3rem;
  padding: 1rem;
}
.sub {
  font-size: 13px;
  margin-left: 0.5rem;
}
.rows {
  display: flex;
  align-items: center;
  justify-content: center;
}
.left {
  margin-left: -5rem;
}
</style>
