<template>
  <div class="forecast-dropdown" @click.stop.prevent>
    <select @change="updateForecast" :style="computedStyles" :disabled="disabled">
      <template v-if="Forecast.CLOSED == forecast">
        <option class="forecast-dropdown__options" selected>Closed</option>
      </template>
      <template v-else>
        <option disabled :selected="forecast == null" :value="null">Select Forecast</option>
        <option
          class="forecast-dropdown__options"
          v-for="option in selectableOptions"
          :selected="option.toUpperCase() === forecast"
          :key="option"
          :value="option"
        >{{ option == Forecast.NA ? 'Unforecasted' : option }}</option>
      </template>
    </select>
  </div>
</template>

<script>
import { forecastEnums } from '@/services/leads/enumerables'
import Forecast from '@/services/forecasts'

export default {
  name: 'LeadForecastDropdown',
  props: {
    lead: {
      required: true,
      type: Object,
    },
    inForecastView: {
      // the serialized data from /views/leads/Forecast is different, and so has to be handled differently
      // the optional forecast prop is passed in only from /views/leads/Forecast, due to that difference in data
      optional: true,
      default: false,
    },
    forecastProp: {
      // only passed in from Forecast view
      optional: true,
      type: Object,
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
  data() {
    return {
      Forecast,
    }
  },
  methods: {
    updateForecast(e) {
      let value = e.target.value.toUpperCase()
      if (this.inForecastView) {
        // handle specific case
        this.forecastViewUpdate(value)
      } else {
        // handle generic case
        this.genericUpdate(value)
      }
    },
    genericUpdate(value) {
      if (this.lead.forecast) {
        // since forecast exists, patch forecast
        let patchData = {
          lead: this.lead.id,
          forecast: value,
        }
        Forecast.api.update(this.lead.forecast, patchData).then(forecast => {
          let prevForecast = this.lead.forecastRef.forecast
          this.lead.forecast = forecast.id
          this.lead.forecastRef = forecast
          let eventPayload = {
            forecast, // includes the leadRef
            from: prevForecast,
            to: value,
          }
          this.$emit('move-lead-in-forecast-list', eventPayload)
        })
      } else {
        // since currently null, create forecast
        Forecast.api.create(this.lead.id, value).then(forecast => {
          this.lead.forecast = forecast.id
          this.lead.forecastRef = forecast
        })
      }
    },
    forecastViewUpdate(value) {
      if (this.forecastProp && this.forecastProp.id) {
        // since forecast exists, patch forecast
        let patchData = {
          lead: this.lead.id,
          forecast: value,
        }
        Forecast.api.update(this.forecastProp.id, patchData).then(data => {
          let eventPayload = {
            forecast: data, // includes the leadRef
            from: this.forecastProp.forecast,
            to: value,
          }
          this.$emit('move-lead-in-forecast-list', eventPayload)
        })
      } else {
        // since currently null, create forecast
        Forecast.api.create(this.lead.id, value).then(response => {
          this.lead.forecastRef = response
          this.lead.forecast = response.id
        })
      }
    },
  },
  computed: {
    selectableOptions() {
      return forecastEnums
    },
    forecast() {
      if (this.inForecastView) {
        return this.forecastProp ? this.forecastProp.forecast : null
      } else {
        return this.lead.forecastRef ? this.lead.forecastRef.forecast : null
      }
    },

    computedStyles() {
      if (this.transparent) {
        return {
          'background-color': 'rgba(149, 150, 180, 0)',
          color: '#110f24',
          'font-size': '.625rem',
          'font-weight': 'normal',
        }
      } else {
        return {
          'background-color': '#9596b4',
          color: '#fff',
          'font-size': '.625rem',
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
    padding: 0.125rem 1.25rem;
    line-height: 1.6;
    border: unset;

    &:focus {
      outline: none;
    }
  }
}
</style>
