<template>
  <div class="lead-banner" :style="bannerBackgroundColor">
    <div class="forecast-container">
      <span class="forecast-label">Forecast</span>
      <LeadForecastDropdown
        class="forecast-dropdown"
        :forecast="lead.forecast"
        :transparent="true"
      />
    </div>
    <LeadStatusDropdown :status="lead.status" />
    <div class="days-in-status-container">
      <span class="days-in-status-label">Days In Status</span>
      <span class="days-in-status">7 Days</span>
    </div>
    <div class="banner-buttons">
      <div class="banner-button">
        <img class="button-icon" src="@/assets/images/undo.svg" alt="reset icon" />
        <span class="button-content">Reset</span>
      </div>
      <div class="banner-button" @click="emitClickedReleased">
        <img class="button-icon" src="@/assets/images/remove.svg" alt="release icon" />
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
    emitClickedReleased() {
      this.$emit('clicked-release')
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

.lead-banner {
  height: 49px;
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
    font-family: $base-font-family, $backup-base-font-family;
    font-size: 12px;
    font-weight: bold;
    font-stretch: normal;
    font-style: normal;
    line-height: 2.25;
    letter-spacing: normal;
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
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 12px;
  font-weight: bold;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.71;
  letter-spacing: normal;
  color: $main-font-gray;
  margin-right: 5%;
}

.days-in-status {
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 12px;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  line-height: 2.25;
  letter-spacing: normal;
  color: $main-font-gray;
}

.banner-buttons {
  flex-grow: 1;
  display: flex;
  flex-flow: row;
  align-items: center;
}

.banner-button {
  -webkit-user-select: none; /* Safari */
  -moz-user-select: none; /* Firefox */
  -ms-user-select: none; /* IE10+/Edge */
  user-select: none; /* Standard */
  margin: 0 4% 0 auto;
  display: flex;
  flex-flow: row;
  align-items: center;
  justify-content: center;
  width: 5rem;
  height: 1.8rem;
  border-radius: 5px;
  border: 1px solid #d1d1d1;
  background-color: #efeff5;
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 11px;
  font-weight: bold;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.45;
  letter-spacing: normal;
  color: $main-font-gray;

  .button-icon {
    height: 16px;
    width: 16px;
  }

  &:hover {
    cursor: pointer;
  }

  &:focus {
    outline: none;
  }

  &:active {
    border-style: solid;
    border-color: black;
  }
}
</style>
