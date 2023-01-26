<template>
  <div>
    <div class="centered">
      <div class="toggle__switch" v-if="form.field.groupOrder.value != 0">
        <label v-if="userCRM !== 'HUBSPOT'" :class="this.selectedCondition !== 'AND' ? 'inactive' : ''">AND</label>
        <ToggleCheckBox
          v-if="userCRM !== 'HUBSPOT'"
          @input="
            selectedCondition == 'AND' ? (selectedCondition = 'OR') : (selectedCondition = 'AND')
          "
          :value="selectedCondition !== 'AND'"
          offColor="#41b883"
          onColor="#41b883"
        />
        <label :class="this.selectedCondition !== 'OR' ? 'inactive' : ''">OR</label>
      </div>

      <!-- <small v-if="form.field.groupOrder.value != 0" @click="toggleSelectedCondition" class="andOr">
        <span :class="this.selectedCondition !== 'AND' ? 'inactive' : ''">AND</span>
        <span class="space-s">|</span>
        <span :class="this.selectedCondition !== 'OR' ? 'inactive' : ''">OR</span></small
      > -->
    </div>

    <div>
      <!-- <small class="small-gray-text">Condition 1</small> -->
      <div
        style="margin-top: 8px"
        :key="i"
        v-for="(alertOperand, i) in form.field.alertOperands.groups"
      >
        <AlertOperandRow
          @remove-operand="onRemoveOperand(i)"
          :resourceType="resourceType"
          :form="alertOperand"
        />
        <div
          v-if="
            form.field.alertOperands.groups.length === i + 1 &&
            form.field.alertOperands.groups.length < 3 &&
            validateAlertOperands(form.field.alertOperands.groups)
          "
          class="column"
        >
          <small>|</small>
        </div>
        <div class="row__buttons">
          <span
            v-if="
              form.field.alertOperands.groups.length === i + 1 &&
              form.field.alertOperands.groups.length < 3 &&
              validateAlertOperands(form.field.alertOperands.groups)
            "
            class="plus_button"
            @click="emitAddOperandForm"
          >
            <button>+</button>
          </span>
          <span v-else></span>

          <small
            @click.stop="onRemoveOperand(i)"
            v-if="form.field.alertOperands.groups.length > 1"
            class="small-gray-text"
          >
            <img src="@/assets/images/remove.svg" height="20px" alt="" />
          </small>
        </div>
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
import AlertOperandRow from '@/views/settings/alerts/create/_AlertOperandRow'

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
    canRemove: { type: Boolean },
    index: { type: Number },
    resourceType: { type: String },
  },
  data() {
    return {}
  },
  async created() {},
  methods: {
    test(log) {
      console.log('log', log)
    },
    toggleSelectedCondition() {
      this.selectedCondition == 'AND'
        ? (this.selectedCondition = 'OR')
        : (this.selectedCondition = 'AND')
    },
    emitAddOperandForm() {
      const order = this.form.field.alertOperands.groups.length
      if (order >= 3) {
        this.$toast('You can only add 3 conditions per group', {
          timeout: 2200,
          position: 'top-left',
          type: 'default',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        return
      }
      this.form.addToArray('alertOperands', new AlertOperandForm())
      this.form.field.alertOperands.groups[order].field.operandOrder.value = order
      this.$emit('scroll-to-view')
    },
    validateAlertOperands(operands) {
      for (let i = 0; i < operands.length; i++) {
        if (!operands[i].field.operandIdentifier.isValid) {
            return false
          }
          if (!operands[i].field.operandOperator.isValid) {
            return false
          }
        if (!operands[i].field.operandValue.isValid) {
          return false
        }
      }
      return true
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
  mounted() {
    if (this.userCRM === 'HUBSPOT') {
      this.selectedCondition = 'OR'
    }
  },
  computed: {
    userCRM() {
      return this.$store.state.user.crm
    },
    selectedCondition: {
      get() {
        return this.form.field.groupCondition.value
      },
      set(val) {
        this.form.field.groupCondition.value = val
      },
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

// .andOr {
//   border: 1px solid $soft-gray;
//   padding: 6px 8px;
//   border-radius: 6px;
//   cursor: pointer;
//   color: $base-gray;
// }
.inactive {
  color: $very-light-gray;
  font-size: 9px;
  border-radius: 4px;
}
// .space-s {
//   margin: 0 4px;
// }
.plus_button {
  border: none;
  background-color: transparent;
  border-radius: 0.3rem;
  padding: 0.1rem;
  display: flex;
  align-items: center;
  cursor: pointer;
  color: $dark-green;
  margin-right: 8px;

  button {
    background-color: white;
    border: 1px solid $dark-green;
    border-radius: 100%;
    color: $dark-green;
    font-size: 18px;
    cursor: pointer;
  }
}
.centered {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 16px;
}
.row__buttons {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin-left: 4px;
}
.toggle__switch {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  margin-bottom: 2rem;
  font-size: 11px;
  letter-spacing: 0.75px;
  color: $base-gray;

  label {
    padding: 0rem 0.2rem;
  }
}
.small-gray-text {
  font-size: 10px;
  color: $coral;
  background-color: $off-white;
  padding: 2px;
  border-radius: 4px;
  margin-right: 8px;
  cursor: pointer;

  img {
    filter: invert(48%) sepia(24%) saturate(1368%) hue-rotate(309deg) brightness(105%) contrast(96%);
  }
}
.column {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-left: 14px;
  margin-top: -22px;
  color: $very-light-gray;
}
</style>
