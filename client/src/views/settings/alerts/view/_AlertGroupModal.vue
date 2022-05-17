<template>
  <div class="alert-group-modal">
    <AlertGroup :resourceType="resourceType" :form.sync="form" />

    <div class="end">
      <PulseLoadingSpinnerButton
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
import AlertGroup from '../create/_AlertGroup'
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'

/**
 * Services
 */
import { AlertGroupForm, AlertGroup as AlertGroupModel } from '@/services/alerts/'

export default {
  /**
   * NB VUE usually throws an error if the child component is affecting the parent props
   * in this case we are affecting the parent props but no error is thrown because we are changing
   * the object multiple levels deep (this current implementation could be seen as incorrect)
   *
   */
  name: 'AlertGroupModal',
  components: {
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
  &--primary {
    @include primary-button();
  }
  box-shadow: none !important;
}
.alert-group-modal {
  padding: 2rem 1rem;
  border-radius: 0.2rem;
  height: 100%;
  overflow-y: scroll;
  background-color: white;
  max-height: 100%;
  width: 100%;
  color: $base-gray;
  font-family: $base-font-family;
  font-size: 13px;
  box-shadow: none;
}
.end {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}
</style>
