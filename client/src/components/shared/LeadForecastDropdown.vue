<template>
  <div class="forecast-dropdown">
    <select @change="onChange" :style="computedStyles" :disabled="disabled">
      <option
        v-for="option in selectableOptions"
        :selected="option.toUpperCase() === forecast"
        :key="option"
        :value="option"
      >
        {{ option }}
      </option>
      <option disabled :selected="forecast == null" value="">Unforecasted</option>
    </select>
  </div>
</template>

<script>
import { forecastEnums } from '@/services/leads/enumerables'

export default {
  name: 'LeadForecastDropdown',
  props: {
    forecast: {
      required: true,
    },
    transparent: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    onChange(e) {
      this.$emit('updated-forecast', e.target.value.toUpperCase())
    },
  },
  computed: {
    selectableOptions() {
      // all options are selectable except 'Unforecasted'. A lead is only 'Unforecasted' on creation.
      return forecastEnums.filter(option => option != 'Unforecasted')
    },
    computedStyles() {
      if (this.transparent) {
        return {
          'background-color': 'rgba(149, 150, 180, 0)',
          color: '#110f24',
          'font-size': '12px',
          'font-weight': 'normal',
        }
      } else {
        return {
          'background-color': '#9596b4',
          color: '#fff',
          'font-size': '10px',
          'font-weight': 'bold',
        }
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.forecast-dropdown {
  width: 8rem;
  height: 1.25rem;
  background-color: rgba(0, 0, 0, 0); // rgb irrelevant, this is for the alpha / transparency

  select {
    @include pointer-on-hover();
    @include base-font-styles();
    width: 96%;
    height: 100%;
    padding: 0.125rem 1rem;
    line-height: 1.6;
    border: unset;

    &:focus {
      outline: none;
    }
  }
}
</style>
