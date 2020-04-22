<template>
  <div class="status-dropdown">
    <select @change="onChange" :style="computedStyles">
      <option :selected="option === status" v-for="option in enums" :key="option" :value="option">
        {{ option }}
      </option>
    </select>
  </div>
</template>

<script>
import { getStatusPrimaryColor } from '@/services/getColorFromLeadStatus'
const enums = ['Ready', 'Trial', 'Demo', 'Waiting', 'Closed', 'Lost']

export default {
  name: 'LeadStatusDropdown',
  props: {
    status: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      enums,
    }
  },
  methods: {
    onChange(e) {
      this.$emit('updated-status', e.target.value)
    },
  },
  computed: {
    computedStyles() {
      return getStatusPrimaryColor(this.status) // returns a plain-object with the key/val of backgroundColor: '#<HEX>'
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.status-dropdown {
  width: 6.25rem;
  height: 1.25rem;
  background-color: rgba(0, 0, 0, 0); // rgb irrelevant, this is for the alpha / transparency

  select {
    @include pointer-on-hover();
    @include base-font-styles();
    width: 96%;
    height: 100%;
    padding: 0.125rem 1rem;
    line-height: 1.6;
    color: $white;
    font-size: 10px;
    font-weight: bold;
    border: unset;

    &:focus {
      outline: none;
    }
  }
}
</style>
