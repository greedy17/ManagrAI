<template>
  <div class="tn-input">
    <label :for="labelRelation" class="tn-input__label"
      >{{ label }} {{ required ? '*' : '' }}</label
    >
    <!-- v-bind="$attrs" loads attributes from parent -->
    <!-- v-on="$listeners" loads listeners from parent -->
    <slot name="input">
      <InputField
        class="tn-input__input"
        :id="labelRelation"
        :class="{
          'tn-input__input--small': isSmall,
          'tn-input__input--medium': isMedium || (!isSmall && !isLarge && !isAutoSize),
          'tn-input__input--large': isLarge,
          'tn-input__input--bordered': isBordered,
        }"
        v-bind="$attrs"
        v-on="$listeners"
      />
    </slot>
    <div v-if="errors.length" class="tn-input__errors">
      <span :key="`${error.code}-${i}`" v-for="(error, i) in errors">{{ error.message }}</span>
    </div>
  </div>
</template>

<script>
import InputField from '@thinknimble/input-field'

export default {
  components: {
    InputField,
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

.tn-input {
  width: 100%;
  margin-bottom: 1.3rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  ::v-deep .primary {
    --active-opacity: 1;
  }

  &__input {
    margin: 0.5rem 0;
    &--small {
      width: 7.4375rem;
    }
    &--medium {
      width: 13rem;
    }
    &--large {
      width: 19.6875rem;
    }
    &--bordered {
      border: lightgray 1px solid;
    }
  }

  &__errors {
    display: flex;
    flex-direction: column;
    color: red;
    font-size: 0.75rem;
    font-family: $base-font-family;
  }
}
</style>
