<template>
  <div class="contact-information" v-if="!showEditForm">
    <div class="container contact-name">
      <img class="image" src="@/assets/images/sara-smith.png" alt="contact image" />
      <span>{{ contact.fullName }}</span>
      <img
        v-if="editable"
        class="edit-contact-icon"
        src="@/assets/images/more_horizontal.svg"
        @click="showEditForm = true"
      />
    </div>
    <div class="container background-color">
      <img class="icon" src="@/assets/images/contact.svg" alt="icon" />
      <span>{{ contact.title || 'N/A' }}</span>
    </div>
    <div class="container background-color">
      <img class="icon" src="@/assets/images/telephone.svg" alt="icon" />
      <span class="contact-phone-number">{{ contact.phoneNumber1 || 'N/A' }}</span>
    </div>
    <div class="container background-color">
      <img class="icon" src="@/assets/images/email.svg" alt="icon" />
      <span class="contact-email">{{ contact.email }}</span>
    </div>
  </div>
  <div v-else class="edit-contact-form">
    <AddContact
      :form="editForm"
      :error="!editFormValid"
      :isEditForm="true"
      @updated-contact="onUpdateAttempt"
      @cancel-edit-form="onCancelUpdate"
    />
  </div>
</template>

<script>
import AddContact from '@/components/leads-new/AddContact'

function generateEditForm(contact) {
  return {
    firstName: contact.firstName || '',
    lastName: contact.lastName || '',
    title: contact.title || '',
    email: contact.email || '',
    phone: contact.phoneNumber1 || '',
  }
}

export default {
  name: 'ContactInformation',
  props: {
    contact: {
      required: true,
    },
    editable: {
      type: Boolean,
      default: false,
    },
  },
  components: {
    AddContact,
  },
  data() {
    return {
      showEditForm: false,
      editFormValid: true,
      editForm: generateEditForm(this.contact),
    }
  },
  methods: {
    onUpdateAttempt() {
      this.editFormValid = true
      if (this.isEditFormValid()) {
        this.$emit('updated-contact', this.contact, this.editForm)
        this.showEditForm = false
      } else {
        this.editFormValid = false
      }
    },
    isEditFormValid() {
      let anyFieldBlank =
        !this.editForm.firstName.length ||
        !this.editForm.lastName.length ||
        !this.editForm.email.length ||
        !this.editForm.title.length ||
        !this.editForm.phone.length

      return !anyFieldBlank
    },
    onCancelUpdate() {
      this.editForm = generateEditForm(this.contact)
      this.showEditForm = false
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.contact-information {
  @include base-font-styles();
  display: flex;
  flex-flow: column;
  box-sizing: border-box;
  padding-left: 0.5rem;
  margin-bottom: 1rem;
  width: 20rem;
}

.container {
  display: flex;
  flex-flow: row;
  align-items: center;
  margin-bottom: 0.2rem;
  padding-right: 1rem;
  padding-left: 0.5rem;
  border-radius: 0.3rem;
  height: 2rem;

  .contact-name {
    padding-right: 0;
  }
}

.background-color {
  background-color: rgba($color: $light-gray-blue, $alpha: 0.2);
}

.image {
  height: 1.4rem;
  width: 1.4rem;
  border-radius: 50%;
  margin-right: 1rem;
}

.icon {
  height: 1.4rem;
  width: 1.4rem;
  margin-right: 1rem;
}

.edit-contact-icon {
  @include pointer-on-hover;
  margin-left: auto;
}

.edit-contact-form {
  width: 100%;
  padding-left: 0.5rem;
  margin-bottom: 1rem;
}
</style>
