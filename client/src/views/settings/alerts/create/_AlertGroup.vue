<template>
  <div>
    <!-- <span class="alert-group-row--label">create automation</span> -->
    <div class="centered">
      <div class="toggle__switch" v-if="form.field.groupOrder.value != 0">
        <label>AND</label>
        <ToggleCheckBox
          @input="
            selectedCondition == 'AND' ? (selectedCondition = 'OR') : (selectedCondition = 'AND')
          "
          :value="selectedCondition !== 'AND'"
          offColor="#41b883"
          onColor="#41b883"
        />
        <label>OR</label>
      </div>
    </div>

    <div>
      <div :key="i" v-for="(alertOperand, i) in form.field.alertOperands.groups">
        <AlertOperandRow
          @remove-operand="onRemoveOperand(i)"
          :resourceType="resourceType"
          :form="alertOperand"
        />
        <div class="row__buttons">
          <button
            class="plus_button"
            style="margin-right: 0.5rem"
            @click.stop="onRemoveOperand(i)"
            v-if="form.field.alertOperands.groups.length > 1"
            :disabled="form.field.alertOperands.groups.length - 1 <= 0"
          >
            <img src="@/assets/images/trash.png" class="filtered" alt="" />
          </button>

          <button class="plus_button" @click="addOperandForm">
            <img src="@/assets/images/plusOne.png" class="filtered" alt="" />
          </button>
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

::v-deep input[type='checkbox'].toggle + div {
  height: 20px;
  width: 40px;
  margin: 0rem 0.5rem;
}
.plus_button {
  border: 1px solid #e8e8e8;
  background-color: transparent;
  border-radius: 0.3rem;
  padding: 0.1rem;
  display: flex;
  align-items: center;
  cursor: pointer;
  color: $dark-green;
}
.filtered {
  filter: invert(80%);
  height: 1rem;
}
.filtered__red {
  filter: invert(29%) sepia(33%) saturate(3647%) hue-rotate(348deg) brightness(94%) contrast(86%);
}
.alert-group-row {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: scroll;
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
.centered {
  display: flex;
  justify-content: center;
  align-items: center;
}
.row__buttons {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: center;
}
.toggle__switch {
  display: flex;
  flex-direction: row;
  margin-bottom: 2rem;
  font-size: 12px;
  letter-spacing: 1px;
}

.remove_button {
  color: $panther-orange;
  border: none;
  font-weight: bold;
  background: transparent;
  cursor: pointer;
}

.sub {
  font-size: 13px;
  margin-left: 0.5rem;
}
.row {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
}
.rows {
  display: flex;
  align-items: center;
  justify-content: center;
}
.left {
  margin-left: -5rem;
}
.column {
  display: flex;
  align-items: center;
}
</style>
