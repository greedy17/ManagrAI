<template>
  <div class="alert-operand-modal">
    <AlertOperandRow v-if="form" :resourceType="resourceType" :form.sync="form" />

    <div class="middle">
      <PulseLoadingSpinnerButton
        style="margin-top: 2rem"
        text="save"
        @click="onSave"
        class="btn btn--primary"
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
import DropDownSearch from '@/components/DropDownSearch'
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
    DropDownSearch,
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

.alert-operand-modal {
  padding: 2rem;
  height: 100%;
  overflow-y: scroll;
  background-color: $white;
  border-radius: 0.5rem;
  color: $base-gray;
  font-weight: bold;
  max-height: 100%;
  width: 100%;
  font-family: $base-font-family;
}
.middle {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
