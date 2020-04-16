<template>
  <div class="add-contact">
    <label>Add Contact</label>
    <div class="form-field">
      <input v-model="name" class="first input" tabindex="0" type="text" placeholder="Name" />
      <input v-model="title" class="second input" tabindex="0" type="text" placeholder="Title" />
    </div>
    <div class="form-field">
      <input v-model="email" class="first input" tabindex="0" type="text" placeholder="Email" />
      <input v-model="phone" class="second input" tabindex="0" type="text" placeholder="Phone" />
    </div>
  </div>
</template>

<script>
export default {
  name: 'AddContact',
  data() {
    return {
      name: '',
      title: '',
      email: '',
      phone: '',
    }
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';

label {
  font-family: $base-font-family, $backup-base-font-family;
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

  .first {
    width: 60%;
    margin-right: 5%;
  }

  .second {
    flex-grow: 1;
  }
}
</style>
