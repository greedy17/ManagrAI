<template>
  <div>
    <AlertOperandRow :resourceType="resourceType" :form.sync="form" />
    <input
      type="date"
      v-model="form.field.dateField.value"
      @blur="form.field.dateField.validate()"
    />
    <button @click="onSave" class="btn btn--primary">Save</button>
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
/**
 * Services
 */
import { AlertOperandForm } from '@/services/alerts/'

export default {
  /**
   * NB VUE usually throws an error if the child component is affecting the parent props
   * in this case we are affecting the parent props but no error is thrown because we are changing
   * the object multiple levels deep (this current implementation could be seen as incorrect)
   *
   */
  name: 'AlertOperandModal',
  components: { ListContainer, ToggleCheckBox, DropDownSearch, FormField, AlertOperandRow },
  props: {
    form: { type: AlertOperandForm },
    resourceType: { type: String },
  },
  data() {
    return {}
  },
  created() {},
  methods: {
    onSave() {
      console.log(this.form.value)
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
}
</style>
