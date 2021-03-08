<template>
  <div class="dropdown">
    <select
      name="dropdown-options"
      id="options"
      class="dropdown__content"
      v-model="selectedOption"
      @blur="emitSelected"
      :class="{
        'dropdown__content-small': size === 'small',
        'dropdown__content-medium': size === 'medium',
        'dropdown__content-large': size === 'large',
        'dropdown__content-bordered': bordered === true,
      }"
      required
    >
      <option :selected="selectedOption" disabled>{{ placeholder }}</option>
      <option v-for="option in options" :key="option.id" :value="option">{{ option.name }}</option>
    </select>
  </div>
</template>

<script>
/**
 * 2021-01-16 William: This component is copied from tn-vue-components. Right now the
 *      npm package @thinknimble/dropdown is not working.
 */
export default {
  name: 'Dropdown',
  props: {
    options: { type: Array, default: () => [] },
    size: { type: String, default: 'large' },
    bordered: { type: Boolean, default: true },
    placeholder: { type: String, default: 'Select Option' },
  },
  created() {
    this.selectedOption = this.$props.placeholder
  },
  data() {
    return {
      selectedOption: null,
    }
  },
  methods: {
    emitSelected() {
      this.$emit('selected', this.selectedOption)
    },
  },
  watch: {
    placeholder: function(newVal) {
      this.selectedOption = newVal
    },
  },
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Lato&display=swap');

.dropdown {
}

.dropdown__content {
  border: none;
  -moz-appearance: none;
  -webkit-appearance: none;
  appearance: none;
  background: white
    url("data:image/svg+xml;utf8,<svg viewBox='0 0 140 140' width='16' height='24' xmlns='http://www.w3.org/2000/svg'><g><path stroke-width='5' d='m121.3,34.6c-1.6-1.6-4.2-1.6-5.8,0l-51,51.1-51.1-51.1c-1.6-1.6-4.2-1.6-5.8,0-1.6,1.6-1.6,4.2 0,5.8l53.9,53.9c0.8,0.8 1.8,1.2 2.9,1.2 1,0 2.1-0.4 2.9-1.2l53.9-53.9c1.7-1.6 1.7-4.2 0.1-5.8z' stroke='black' fill='black'/></g></svg>")
    no-repeat;
  background-position: right 5px top 50%;
  font-family: 'Lato', sans-serif;
}

.dropdown__content-bordered {
  border-radius: 4px;
  background-color: #efeff5;
  border: solid 1px #ececee;
  width: 256px;
}

.dropdown__content-small {
  height: 24px;
  font-size: 11px;
  padding: 0 8px;
}

.dropdown__content-medium {
  height: 32px;
  font-size: 14px;
  padding: 0 10px;
}

.dropdown__content-large {
  height: 40px;
  font-size: 16px;
  padding: 0 12px;
}
</style>
