<template>
  <div class="status-dropdown">
    <select @change="onChange" :style="computedStyles" :disabled="status === 'CLOSED'">
      <option disabled :selected="status == null" value="">---</option>
      <option
        :selected="option.toUpperCase() === status"
        v-for="option in statusEnums"
        :key="option"
        :value="option"
      >
        {{ option }}
      </option>
    </select>
  </div>
</template>

<script>
import { getStatusPrimaryColor } from '@/services/getColorFromLeadStatus'
import { statusEnums } from '@/services/leads/enumerables'

export default {
  name: 'LeadStatusDropdown',
  props: {
    status: {
      required: true,
    },
  },
  data() {
    return {
      statusEnums,
    }
  },
  methods: {
    onChange(e) {
      this.$emit('updated-status', e.target.value.toUpperCase())
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
