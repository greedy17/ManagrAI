<template>
  <div
    class="form-field"
    :class="{
      'form-field--small': isSmall,
      'form-field--medium': isMedium || (!isSmall && !isLarge && !isAutoSize),
      'form-field--large': isLarge,
      'form-field--bordered': isBordered,
    }"
    @blur="$emit('blur')"
    @input="$emit('input', $event.target.value)"
  >
    <label :for="labelRelation" class="form-field__label"
      >{{ label }} {{ required ? '*' : '' }}</label
    >
    <!-- v-bind="$attrs" loads attributes from parent  if they are common must be explicit-->
    <!-- v-on="$listeners" loads listeners from parent -->
    <slot name="input">
      <Input
        :id="$attrs.id"
        :disabled="$attrs.disabled"
        :type="$attrs.type"
        @blur="$emit('blur')"
      />
    </slot>
    <div v-show="errors.length" class="form-field__errors">
      <span :key="`${error.code}-${i}`" v-for="(error, i) in errors">{{ error.message }}</span>
    </div>
  </div>
</template>

<script>
import Input from '@/components/forms/inputs/Input.vue'
export default {
  components: {
    Input,
  },
  props: {
    errors: {
      type: Array,
      default: () => [],
    },
    label: {
      type: String,
      default: '',
    },
    labelRelation: {
      type: String,
      required: false,
    },
    inputType: {
      type: String,
      default: 'text',
    },
    required: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    isSmall() {
      return this.$attrs.hasOwnProperty('small')
    },
    isMedium() {
      return this.$attrs.hasOwnProperty('medium')
    },
    isLarge() {
      return this.$attrs.hasOwnProperty('large')
    },
    isAutoSize() {
      return this.$attrs.hasOwnProperty('autoSize')
    },
    isBordered() {
      return this.$attrs.hasOwnProperty('bordered')
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/utils';

.form-field {
  padding: 0.3rem;
  &--large {
    width: 20rem;
  }
  &--small {
    width: 5rem;
  }
  &--medium {
    width: 10rem;
  }
  &__input {
    width: 100%;
  }
  &__label {
    @include field-label();
  }
  &__errors {
    @include field-errors();
  }
}
.form-field__input {
  @include input-field-white();
}
</style>
