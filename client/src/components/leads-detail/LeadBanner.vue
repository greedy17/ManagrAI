<template>
  <div class="lead-banner" :style="bannerBackgroundColor">
    <div class="forecast-container">
      <span class="forecast-label">Forecast</span>
      <LeadForecastDropdown
        class="forecast-dropdown"
        :forecast="lead.forecast && lead.forecastRef.forecast"
        :transparent="true"
        @updated-forecast="emitUpdatedForecast"
      />
    </div>
    <LeadStatusDropdown :status="lead.status" @updated-status="emitUpdatedStatus" />
    <div class="days-in-status-container">
      <span class="days-in-status-label">Days In Status</span>
      <span class="days-in-status">7 Days</span>
    </div>
    <div class="banner-buttons">
      <div class="banner-button" @click="emitReset">
        <img class="button-icon" src="@/assets/images/undo.svg" alt="icon" />
        <span class="button-content">Reset</span>
      </div>
      <div class="banner-button" @click="emitReleased">
        <img class="button-icon" src="@/assets/images/remove.svg" alt="icon" />
        <span class="button-content">Release</span>
      </div>
    </div>
  </div>
</template>

<script>
import { getStatusSecondaryColor } from '@/services/getColorFromLeadStatus'
import LeadForecastDropdown from '@/components/shared/LeadForecastDropdown'
import LeadStatusDropdown from '@/components/shared/LeadStatusDropdown'

export default {
  name: 'LeadBanner',
  props: {
    lead: Object,
  },
  components: {
    LeadForecastDropdown,
    LeadStatusDropdown,
  },
  methods: {
    emitReset() {
      this.$emit('lead-reset')
    },
    emitReleased() {
      this.$emit('lead-released')
    },
    emitUpdatedForecast(value) {
      this.$emit('updated-forecast', value)
    },
    emitUpdatedStatus(value) {
      this.$emit('updated-status', value)
    },
  },
  computed: {
    bannerBackgroundColor() {
      return getStatusSecondaryColor(this.lead.status)
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.lead-banner {
  @include disable-text-select();
  height: 3rem;
  display: flex;
  flex-flow: row;
  align-items: center;
}

.forecast-container {
  width: 25%;
  padding-left: 2%;
  display: flex;
  flex-flow: row;
  align-items: center;

  .forecast-label {
    @include base-font-styles();
    font-size: 12px;
    font-weight: bold;
    line-height: 2.25;
    color: $main-font-gray;
  }

  .forecast-dropdown {
    margin-left: 5%;
  }
}

.days-in-status-container {
  width: 29%;
  display: flex;
  flex-flow: row;
  align-items: center;
  justify-content: center;
}

.days-in-status-label {
  @include base-font-styles();
  font-size: 12px;
  font-weight: bold;
  line-height: 1.71;
  color: $main-font-gray;
  margin-right: 5%;
}

.days-in-status {
  @include base-font-styles();
  font-size: 12px;
  line-height: 2.25;
  color: $main-font-gray;
}

.banner-buttons {
  flex-grow: 1;
  display: flex;
  flex-flow: row;
  align-items: center;
}

.banner-button {
  @include disable-text-select();
  @include pointer-on-hover();
  @include base-font-styles();
  margin: 0 4% 0 auto;
  display: flex;
  flex-flow: row;
  align-items: center;
  justify-content: center;
  width: 5rem;
  height: 1.8rem;
  border-radius: 5px;
  background-color: $soft-gray;
  font-size: 11px;
  font-weight: bold;
  line-height: 1.45;
  color: $main-font-gray;
  border: 1px solid $gray;

  .button-icon {
    height: 1rem;
    width: 1rem;
  }

  &:focus {
    outline: none;
  }

  &:active {
    border-style: solid;
    border-color: $black;
  }
}
</style>
