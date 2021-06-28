<template>
  <input
    class="form-field__input"
    :id="id"
    :type="type"
    :name="name ? name : id"
    :disabled="disabled"
    v-on="$listeners"
    @input="$emit('input', $event)"
    @blur="$emit('blur')"
  />
</template>

<script>
export default {
  components: {},
  props: {
    id: {
      type: String,
    },
    type: {
      type: String,
    },
    name: {
      type: String,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  computed: {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/utils';

.form-field__input {
  @include input-field-white();
  width: 100%;
}
</style>
