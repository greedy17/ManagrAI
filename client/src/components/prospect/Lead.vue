<template>
  <div class="lead">
    <div class="header">
      <span class="lead-name"> {{ lead.title }} </span>
      <span class="lead-rating"> {{ lead.rating }} </span>
      <div class="lead-description">
        <span>{{ lead.primaryDescription }}</span>
        <span>{{ lead.secondaryDescription }}</span>
      </div>
      <span class="lead-amount"> {{ lead.amount | currency }} </span>
      <span class="lead-last-update"> {{ lead.lastUpdateDate }} </span>
      <LeadForecastDropdown
        :forecast="lead.forecastRef && lead.forecastRef.forecast"
        :disabled="!belongsToCurrentUser"
        @updated-forecast="updateForecast"
      />
      <LeadStatusDropdown
        :status="lead.status"
        :disabled="!belongsToCurrentUser"
        @updated-status="updateStatus"
      />
      <div class="button-container">
        <button class="claimed-button" v-if="lead.claimedBy">
          <img class="icon" alt="icon" src="@/assets/images/claimed.svg" />
          <span>{{ belongsToCurrentUser ? 'Yours' : lead.claimedByRef.fullName }}</span>
        </button>
        <button v-else class="claim-button" @click="claimLead">
          <span>Claim</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import LeadForecastDropdown from '@/components/shared/LeadForecastDropdown'
import LeadStatusDropdown from '@/components/shared/LeadStatusDropdown'
import Forecast from '@/services/forecasts'
import Lead from '@/services/leads'
export default {
  name: 'Lead',
  props: {
    lead: {
      required: true,
      type: Lead,
    },
  },
  components: {
    LeadForecastDropdown,
    LeadStatusDropdown,
  },
  data() {
    return {
      isClaimed: null,
      rep: null,
    }
  },
  methods: {
    updateStatus(value) {
      if (this.lead.status == 'CLOSED') {
        this.$Alert.alert({
          type: 'warning',
          timeout: 4000,
          message: 'Lead already closed!',
        })
      } else if (value != 'CLOSED') {
        let patchData = { status: value }
        Lead.api.update(this.lead.id, patchData).then(lead => {
          this.lead.status = lead.status
        })
      } else {
        // NOTE (Bruno 5-8-20): Modal positioning has a bug, so currently will only open from LeadDetail page
        // this.modal.isOpen = true
        alert(
          'NOTE (Bruno 5-8-20): Modal positioning has a bug, so currently will only open from LeadDetail page',
        )
      }
    },
    updateForecast(value) {
      if (this.lead.forecast) {
        // since forecast exists, patch forecast
        let patchData = {
          lead: this.lead.id,
          forecast: value,
        }
        Forecast.api.update(this.lead.forecast, patchData).then(forecast => {
          this.lead.forecast = forecast.id
          this.lead.forecastRef = forecast
        })
      } else {
        // since currently null, create forecast
        Forecast.api.create(this.lead.id, value).then(forecast => {
          this.lead.forecast = forecast.id
          this.lead.forecastRef = forecast
        })
      }
    },
    claimLead() {
      alert(
        'Clicking claim should claim the lead and not change the page (so that many leads can be claimed in succession)',
      )
    },
  },
  computed: {
    belongsToCurrentUser() {
      return this.lead.claimedBy == this.$store.state.user.id
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

.lead {
  margin-bottom: 0.625rem;
}

.lead,
.lead > * {
  @include base-font-styles();
  line-height: 1.14;
  color: $main-font-gray;
  font-size: 0.9rem;
}

.header {
  @include disable-text-select();
  display: flex;
  flex-flow: row;
  align-items: center;
  height: 3rem;
  border: 2px solid $off-white;
}
.lead-rating {
  @include base-font-styles();
  width: 4%;
  text-align: center;
  opacity: 0.5;
  font-size: 12px;
  font-weight: bold;
  letter-spacing: 0.5px;
  color: $base-gray;
}

.lead-name {
  @include pointer-on-hover();
  @include base-font-styles();
  width: 20%;
  padding-left: 1%;
  height: 1rem;
  font-weight: bold;
  font-size: 14px;
  line-height: 1.14;
  color: $main-font-gray;
}

.lead-description {
  @include base-font-styles();
  display: flex;
  flex-flow: column;
  font-size: 11px;
  line-height: 1.45;
  color: $main-font-gray;
  width: 20%;
}
.lead-description {
  width: 12.5%;
}

.lead-amount {
  width: 7.5%;
  padding-left: 0.625rem;
}

.lead-last-update {
  width: 5%;
}
.lead-amount,
.lead-last-update {
  @include base-font-styles();
  font-size: 11px;
  line-height: 1.45;
  color: $main-font-gray;
}
.image {
  height: 1.4rem;
  width: 1.4rem;
  border-radius: 50%;
  margin-right: 1rem;
}

.icon {
  height: 1.4rem;
  width: 1.4rem;
  margin-right: 0.5rem;
}

.contacts-container {
  display: flex;
  flex-flow: row;
  align-items: center;
}

.contact {
  display: flex;
  flex-flow: row;
  align-items: center;
  margin-right: 3rem;
}

.button-container {
  width: 15%;
  margin-left: auto;
  margin-right: 5rem;
  display: flex;
  flex-flow: row;
  align-items: center;

  .claimed-button {
    @include secondary-button();
    padding-right: 0.7rem;
    padding-left: 0.5rem;
    width: auto;
    display: flex;
    flex-flow: row;
    align-items: center;
  }

  .claim-button {
    @include primary-button();
    padding-right: 0.7rem;
    padding-left: 0.5rem;
    width: auto;
    display: flex;
    flex-flow: row;
    align-items: center;
  }
}
</style>
