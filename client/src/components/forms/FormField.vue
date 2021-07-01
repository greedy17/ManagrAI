<template>
  <div
    class="tn-input"
    :class="{
      'tn-input--small': isSmall,
      'tn-input--medium': isMedium || (!isSmall && !isLarge && !isAutoSize),
      'tn-input--large': isLarge,
    }"
  >
    <label :for="labelRelation" class="tn-input__label"
      >{{ label }} {{ required ? '*' : '' }}</label
    >
    <!-- v-bind="$attrs" loads attributes from parent -->
    <!-- v-on="$listeners" loads listeners from parent -->
    <slot name="input">
      <InputField
        class="tn-input__input"
        :id="$attrs.id"
        v-bind="$attrs"
        v-on="$listeners"
        :type="inputType"
      />
    </slot>
    <div v-show="errors.length" class="tn-input__errors">
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
@import '@/styles/mixins/inputs';

.tn-input {
  margin-bottom: 1.3rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;

  &__label {
    font-size: 14px;
    margin-bottom: 0.3rem;
  }
  ::v-deep .primary {
    --active-opacity: 1;
  }

  /*   ::v-deep .input-content__active {
    box-shadow: 0 0 10px rgba($color: $dark-green, $alpha: 0.5);
    outline: none;
    background-color: $white;
  } */

  &__errors {
    position: relative;
    top: 2px;
    display: flex;
    flex-direction: column;
    color: $coral;
    font-size: 0.75rem;
    font-family: $base-font-family;
    z-index: 999;
  }
}
::v-deep .input-content {
  @include input-field-white();
}
::v-deep .input-content__active {
  outline: none;
}
::v-deep .input-form__active {
  border: $dark-green;
}
</style>
