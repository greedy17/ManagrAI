<template>
  <div class="alert-group-modal">
    <AlertGroup :resourceType="resourceType" :form.sync="form" />
    <button @click="onSave" class="btn btn--primary">Save</button>
  </div>
</template>

<script>
/**
 * Components
 * */
// Pacakges
import AlertGroup from '../create/_AlertGroup'
import ToggleCheckBox from '@thinknimble/togglecheckbox'

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
  components: { ListContainer, ToggleCheckBox, DropDownSearch, FormField, AlertGroup },
  props: {
    form: { type: AlertGroupForm },
    resourceType: { type: String },
  },
  data() {
    return {}
  },
  created() {},
  methods: {
    async onSave() {
      this.form.validate()
      if (this.form.isValid) {
        try {
          await AlertGroupModel.api.createGroup(this.form.toAPI)
          this.$Alert.alert({
            message: 'Successfully Added new group and operands',
            type: 'success',
            timeout: 2000,
          })
          this.$modal.hideAll()
        } catch (e) {
          console.log(e)
        }
      }
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
