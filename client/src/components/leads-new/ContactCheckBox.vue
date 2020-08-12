<template>
  <div class="contact-checkbox">
    <div class="check-box">
      <CheckBox :checked="checked" @checkbox-clicked="bubbleCheckboxClick" />
    </div>
    <div class="contact">
      <ContactInformation
        :contact="contact"
        :editable="editable"
        @updated-contact="(contact, editForm) => $emit('updated-contact', contact, editForm)"
      />
    </div>
  </div>
</template>

<script>
import CheckBox from '@/components/leads-new/CheckBox'
import ContactInformation from '@/components/leads-new/ContactInformation'

export default {
  name: 'ContactCheckBox',
  props: {
    contact: {
      required: true,
    },
    checked: {
      type: Boolean,
      required: true,
    },
    editable: {
      type: Boolean,
      default: false,
    },
  },
  components: {
    CheckBox,
    ContactInformation,
  },
  methods: {
    bubbleCheckboxClick(status) {
      let payload = {
        status, // checked vs not checked Boolean
        contactID: this.contact.id,
        email: this.contact.email,
      }
      this.$emit('checkbox-clicked', payload)
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/buttons';

.contact-checkbox {
  display: flex;
  flex-flow: row;
  .contact {
    flex: 1 0 auto;
  }
}
</style>
