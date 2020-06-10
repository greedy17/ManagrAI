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
    <LeadStatusDropdown :lead="lead" />
    <div class="days-in-status-container">
      <span class="days-in-status-label">Days In Status</span>
      <span class="days-in-status">7 Days</span>
    </div>
    <div class="banner-buttons">
      <div v-if="isOwnedByUser" class="banner-button" @click="emitReset">
        <img class="button-icon" src="@/assets/images/undo.svg" alt="icon" />
        <span class="button-content">Reset</span>
      </div>
      <div v-if="isOwnedByUser" class="banner-button" @click="emitRelease">
        <img class="button-icon" src="@/assets/images/remove.svg" alt="icon" />
        <span class="button-content">Release</span>
      </div>
      <div v-if="!isOwnedByUser && !isOwnedByAnother" class="banner-button" @click="emitClaim">
        <img class="button-icon" src="@/assets/images/claimed.svg" alt="icon" />
        <span class="button-content">Claim</span>
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
    emitRelease() {
      this.$emit('lead-released')
    },
    emitClaim() {
      this.$emit('lead-claimed')
    },
    emitUpdatedForecast(value) {
      this.$emit('updated-forecast', value)
    },
  },
  computed: {
    bannerBackgroundColor() {
      return getStatusSecondaryColor(this.lead.status && this.lead.status.toLowerCase())
    },
    isOwnedByUser() {
      return this.lead.claimedBy && this.lead.claimedBy == this.$store.state.user.id
    },
    isOwnedByAnother() {
      return this.lead.claimedBy && this.lead.claimedBy != this.$store.state.user.id
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
  margin-bottom: 1.25rem;
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
