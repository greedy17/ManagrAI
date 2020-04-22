<template>
  <div class="forecast-dropdown">
    <select @change="onChange" :style="computedStyles">
      <option :selected="option === forecast" v-for="option in enums" :key="option" :value="option">
        {{ option }}
      </option>
    </select>
  </div>
</template>

<script>
const enums = ['50/50', 'Strong', 'Verbal', 'Future', 'Unforecasted']

export default {
  name: 'LeadForecastDropdown',
  props: {
    forecast: {
      type: String,
      required: true,
    },
    transparent: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      enums,
    }
  },
  methods: {
    onChange(e) {
      this.$emit('updated-forecast', e.target.value)
    },
  },
  computed: {
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
    width: 96%;
    height: 100%;
    padding: 0.125rem 1rem;

    font-family: $base-font-family, $backup-base-font-family;
    font-stretch: normal;
    font-style: normal;
    line-height: 1.6;
    letter-spacing: normal;

    border: unset;

    &:focus {
      outline: none;
    }
  }
}
</style>
