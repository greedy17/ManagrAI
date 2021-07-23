<template>
  <div class="alert-group-modal">
    <AlertGroup :resourceType="resourceType" :form.sync="form" />
    <PulseLoadingSpinnerButton
      text="save"
      @click="onSave"
      class="btn btn--primary"
      :loading="isSaving"
      :disabled="!form.isValid"
    />
  </div>
</template>

<script>
/**
 * Components
 * */
// Pacakges
import AlertGroup from '../create/_AlertGroup'
import ToggleCheckBox from '@thinknimble/togglecheckbox'
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'

//Internal
import ListContainer from '@/components/ListContainer'
import FormField from '@/components/forms/FormField'
import DropDownSearch from '@/components/DropDownSearch'
/**
 * Services
 */
import { AlertOperandForm, AlertGroupForm, AlertGroup as AlertGroupModel } from '@/services/alerts/'

export default {
  /**
   * NB VUE usually throws an error if the child component is affecting the parent props
   * in this case we are affecting the parent props but no error is thrown because we are changing
   * the object multiple levels deep (this current implementation could be seen as incorrect)
   *
   */
  name: 'AlertGroupModal',
  components: {
    ListContainer,
    ToggleCheckBox,
    DropDownSearch,
    FormField,
    AlertGroup,
    PulseLoadingSpinnerButton,
  },
  props: {
    form: { type: AlertGroupForm },
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
          const res = await AlertGroupModel.api.createGroup(this.form.toAPI)
          this.$Alert.alert({
            message: 'Successfully Added new group and operands',
            type: 'success',
            timeout: 2000,
          })
          this.createdObj = res
          this.$modal.hide('alert-groups-modal', { createdObj: this.createdObj })
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
.alert-group-modal {
  padding: 0.5rem;
  height: 100%;
  overflow-y: scroll;

  max-height: 100%;
  width: 100%;
}
</style>
