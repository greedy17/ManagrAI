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
const enums = ['Ready', 'Trial', 'Demo', 'Waiting']

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
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');

.status-dropdown {
  width: 100px;
  height: 20px;
  background-color: rgba(0, 0, 0, 0); // rgb irrelevant, this is for the alpha / transparency

  select {
    width: 96%;
    height: 100%;
    padding: 2px 15px;

    font-family: 'Lato', sans-serif;
    font-stretch: normal;
    font-style: normal;
    line-height: 1.6;
    letter-spacing: normal;
    color: #ffffff;
    font-size: 10px;
    font-weight: bold;

    border: unset;

    &:hover {
      cursor: pointer;
    }

    &:focus {
      outline: none;
    }
  }
}
</style>
