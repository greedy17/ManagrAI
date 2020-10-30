<template>
  <div class="lead-banner" :style="{ 'background-color': bannerBackgroundColor }">
    <div style="margin: 0 0.5rem 0 1rem;">
      <LeadScore :lead="lead" />
    </div>
    <div class="forecast-container">
      <span class="forecast-label">Forecast</span>
      <LeadForecastDropdown
        class="forecast-dropdown"
        :lead="lead"
        :transparent="true"
        :disabled="!isOwnedByUser"
      />
    </div>
    <LeadStatusDropdown :lead="lead" :disabled="!isOwnedByUser && !isManager" />
    <div class="days-in-status-container">
      <span class="days-in-status-label">Time In Stage</span>
      <span class="days-in-status">{{ this.lead.statusLastUpdate | timeToNow }}</span>
    </div>
    <div class="banner-buttons">
      <div v-if="isOwnedByUser" class="banner-button" @click="emitReset">
        <img class="button-icon" src="@/assets/images/undo.svg" alt="icon" />
        <span class="button-content">Reset</span>
      </div>
      <div v-if="isOwnedByUser && !isClosed" class="banner-button" @click="emitRelease">
        <img class="button-icon" src="@/assets/images/remove.svg" alt="icon" />
        <span class="button-content">Release</span>
      </div>
      <div v-if="!isOwnedByUser && !isOwnedByAnother" class="banner-button" @click="emitClaim">
        <img class="button-icon" src="@/assets/images/claimed.svg" alt="icon" />
        <span class="button-content">Claim</span>
      </div>
      <div v-if="!isOwnedByUser && isOwnedByAnother" class="banner-button banner-item">
        <img class="button-icon" alt="icon" src="@/assets/images/claimed.svg" />
        <span class="button-content">
          {{
          lead.claimedByRef.fullName.trim() ? lead.claimedByRef.fullName : lead.claimedByRef.email
          }}
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import Lead from '@/services/leads'
import { getLightenedColor } from '@/services/getColorFromLeadStatus'

import LeadForecastDropdown from '@/components/shared/LeadForecastDropdown'
import LeadStatusDropdown from '@/components/shared/LeadStatusDropdown'
import LeadScore from '@/components/shared/LeadScore'

export default {
  name: 'LeadBanner',
  props: {
    lead: {
      type: Object,
      required: true,
    },
  },
  components: {
    LeadForecastDropdown,
    LeadStatusDropdown,
    LeadScore,
  },
  methods: {
    emitReset() {
      if (this.lead.statusRef && this.lead.statusRef.title === Lead.CLOSED) {
        this.$Alert.alert({
          type: 'error',
          timeout: 3000,
          message: 'Cannot reset a lead that is closed.',
        })
      } else {
        this.$emit('lead-reset')
      }
    },
    emitRelease() {
      this.$emit('lead-released')
    },
    emitClaim() {
      this.$emit('lead-claimed')
    },
  },
  computed: {
    bannerBackgroundColor() {
      return this.lead.statusRef
        ? getLightenedColor(this.lead.statusRef.color)
        : getLightenedColor('#9B9B9B')
    },
    isOwnedByUser() {
      return this.lead.claimedBy && this.lead.claimedBy == this.$store.state.user.id
    },
    isManager() {
      return this.$store.state.user.isManager
    },
    isOwnedByAnother() {
      return this.lead.claimedBy && this.lead.claimedBy != this.$store.state.user.id
    },
    isClosed() {
      return this.lead.statusRef && this.lead.statusRef.title === Lead.CLOSED
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.lead-banner {
  @include disable-text-select();
  @include standard-border();
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
    font-size: 0.625rem;

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
  font-size: 0.625rem;
  font-weight: bold;
  line-height: 1.71;
  color: $main-font-gray;
  margin-right: 5%;
}

.days-in-status {
  @include base-font-styles();
  font-size: 0.625rem;
  line-height: 2.25;
  color: $main-font-gray;
}

.banner-buttons {
  flex-grow: 1;
  display: flex;
  flex-flow: row;
  align-items: center;
  padding-right: 1rem;
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
    margin-right: 0.3rem;
  }

  &:focus {
    outline: none;
  }

  &:active {
    border-style: solid;
    border-color: $black;
  }
}

.banner-item {
  font-size: 0.9rem;
  min-width: 8rem;
  height: 2rem;
  border: 1px solid $mid-gray;

  &:active {
    border: 1px solid $mid-gray;
  }

  &:hover {
    cursor: unset;
  }

  .button-icon {
    margin-right: 0.5rem;
  }
}
</style>
