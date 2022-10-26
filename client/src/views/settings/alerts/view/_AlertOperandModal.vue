<template>
  <div class="alert-operand-modal">
    <div class="alert-operand-modal__header"></div>
    <AlertOperandRow v-if="form" :resourceType="resourceType" :form.sync="form" />

    <div class="alert-operand-modal__save">
      <button
        text="save"
        @click="onSave"
        class="primary-button"
        :loading="isSaving"
        :disabled="!form.isValid"
      >
        Add Condition
      </button>
    </div>
  </div>
</template>

<script>
/**
 * Components
 * */
// Pacakges
import AlertOperandRow from '../create/_AlertOperandRow.vue'

//Internal
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
/**
 * Services
 */
import { AlertOperandForm, AlertGroupOperand } from '@/services/alerts/'

export default {
  /**
   * NB VUE usually throws an error if the child component is affecting the parent props
   * in this case we are affecting the parent props but no error is thrown because we are changing
   * the object multiple levels deep (this current implementation could be seen as incorrect)
   *
   */
  name: 'AlertOperandModal',
  components: {
    AlertOperandRow,
    AlertGroupOperand,
    PulseLoadingSpinnerButton,
  },
  props: {
    form: { type: AlertOperandForm },
    resourceType: { type: String },
  },
  data() {
    return {
      isSaving: false,
      createdObj: null,
    }
  },
  created() {},
  methods: {
    async onSave() {
      this.isSaving = true
      this.form.validate()
      if (this.form.isValid) {
        try {
          const res = await AlertGroupOperand.api.createOperand(this.form.toAPI)
          this.$toast('Successfully added operand', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          this.createdObj = res
          this.$modal.hide('alert-operands-modal', { createdObj: this.createdObj })
          this.isSaving = false
        } finally {
          this.isSaving = false
        }
      }
      this.isSaving = false
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.primary-button {
  padding: 0.4rem 1rem;
  box-shadow: none;
  font-weight: 400;
}
.primary-button:disabled {
  background-color: $soft-gray;
}

.alert-operand-modal {
  overflow-y: scroll;
  background-color: $white;
  border-radius: 0.3rem;
  color: $base-gray;
  width: 100%;
  font-family: $base-font-family;

  &__header {
    padding: 0.25rem 1.5rem;
    letter-spacing: 1px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
  }

  &__save {
    display: flex;
    align-items: flex-end;
    justify-content: flex-end;
    padding-right: 1rem;
    height: 200px;
    width: 100%;
  }
}
</style>
