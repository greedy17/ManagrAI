<template>
  <div class="status-dropdown">
    <select :value="value" @change="onChange">
      <option :value="null">---</option>
      <option v-for="option in items" :key="option[valueKey]" :value="option[valueKey]">
        {{ option[displayKey] }}
      </option>
    </select>
  </div>
</template>

<script>
export default {
  name: 'LeadStatusDropdown',
  props: {
    items: {
      type: Array,
    },
    valueKey: {
      type: String,
    },
    displayKey: {
      type: String,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    value: {},
  },
  data() {
    return {}
  },
  methods: {
    onChange(e) {
      this.$emit('input', e.target.value)
      this.$emit('selected', e.target.value)
    },
  },
  computed: {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';
</style>
