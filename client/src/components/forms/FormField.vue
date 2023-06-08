<template>
  <!-- This file should not be used anywhere in the future. 
  When that happens, delete this file. -->
  <div>
    <label :for="labelRelation" class="tn-input__label"
      >{{ label }} {{ required ? '*' : '' }}</label
    >
    <!-- v-bind="$attrs" loads attributes from parent -->
    <!-- v-on="$listeners" loads listeners from parent -->
    <slot name="input">
      <InputField
        style="width: 21vw !important"
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
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';
@import '@/styles/mixins/inputs';

.tn-input {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  width: 100% !important;

  &__label {
    font-size: 14px;
    margin-top: 0.3rem;
  }

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
  background-img {
    display: none;
  }
}

::v-deep .input-content {
  background-color: white;
  width: 100% !important;
}
::v-deep .input-content__large {
  width: 100% !important;
}
</style>
