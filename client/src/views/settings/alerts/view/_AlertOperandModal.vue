<template>
  <div class="alert-operand-modal">
    <div class="alert-operand-modal__header">
      <h3>Add Condition</h3>
    </div>
    <AlertOperandRow v-if="form" :resourceType="resourceType" :form.sync="form" />

    <div class="alert-operand-modal__save">
      <PulseLoadingSpinnerButton
        text="save"
        @click="onSave"
        class="primary-button"
        :loading="isSaving"
        :disabled="!form.isValid"
      />
    </div>
  </div>
</template>

<script>
/**
 * Components
 * */
// Pacakges
import AlertOperandRow from '../create/_AlertOperandRow.vue'
import ToggleCheckBox from '@thinknimble/togglecheckbox'

//Internal
import ListContainer from '@/components/ListContainer'
import FormField from '@/components/forms/FormField'
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
    ListContainer,
    ToggleCheckBox,
    FormField,
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
          this.$Alert.alert({
            message: 'Successfully Added added and operand',
            type: 'success',
            timeout: 2000,
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

.primary-button {
  padding: 0.4rem 1.5rem;
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
    outline: 1px solid #e8e8e8;
    display: flex;
    align-items: center;
    justify-content: space-between;
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
