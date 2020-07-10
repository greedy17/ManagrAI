<template>
  <div class="add-contact">
    <label v-if="isEditForm">Edits will affect this contact on an account-wide basis.</label>
    <label v-else>Add Contact</label>
    <div class="errors" v-if="error">
      <span v-if="isEditForm">Must be fully completed.</span>
      <span v-else>Must be blank or fully completed.</span>
    </div>
    <div class="form-field">
      <input
        v-model="form.firstName"
        class="first-name input"
        tabindex="0"
        type="text"
        placeholder="First Name"
      />
      <input
        v-model="form.lastName"
        class="last-name input"
        tabindex="0"
        type="text"
        placeholder="Last Name"
      />
      <input
        v-model="form.title"
        class="title input"
        tabindex="0"
        type="text"
        placeholder="Title"
      />
    </div>
    <div class="form-field">
      <input
        v-model="form.email"
        class="email input"
        tabindex="0"
        type="text"
        placeholder="Email"
      />
      <input
        v-model="form.phone"
        class="phone input"
        tabindex="0"
        placeholder="Phone"
        v-mask="'(###) ###-####'"
      />
    </div>
    <div v-if="isEditForm" style="display: flex; flex-flow: row;">
      <button class="cancel-button" @click.stop="$emit('cancel-edit-form')">
        Cancel
      </button>
      <button
        class="update-button"
        style="margin-left: 0.5rem;"
        @click.stop="$emit('updated-contact')"
      >
        Update
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AddContact',
  props: {
    form: {
      required: true,
      type: Object,
    },
    error: {
      required: false,
      type: Boolean,
    },
    isEditForm: {
      type: Boolean,
      default: false,
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

label {
  @include base-font-styles();
  color: $main-font-gray;
  font-weight: bold;
  margin-bottom: 1rem;
  display: inline-block;
}

.input {
  @include input-field();
  height: 2rem;
  margin-bottom: 1rem;
}

.form-field {
  display: flex;
  flex-flow: row;
  width: 100%;

  .first-name {
    width: 15rem;
    margin-right: 1rem;
  }

  .last-name {
    width: 18rem;
    margin-right: 1rem;
  }

  .title {
    width: 15rem;
  }

  .email {
    width: 30rem;
    margin-right: 1rem;
  }

  .phone {
    width: 19rem;
  }
}

.errors {
  color: $coral;
}

.cancel-button {
  @include secondary-button;
}

.update-button {
  @include primary-button;
}
</style>
