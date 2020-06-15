<template>
  <div class="lead">
    <Modal v-if="modal.isOpen" dimmed @close-modal="closeModal" :width="50">
      <CloseLead :lead="lead" />
    </Modal>
    <div class="lead-header" v-bind:style="headerBackgroundColor">
      <span class="lead-name" @click="toggleDetails">{{ lead.title }}</span>
      <span class="lead-rating">{{ lead.rating }}</span>
      <div v-if="lead.primaryDescription || lead.secondaryDescription" class="lead-description">
        <div class="primary">{{ lead.primaryDescription || '-Primary Not Set-' }}</div>
        <div class="secondary">{{ lead.secondaryDescription || '-Secondary Not Set-' }}</div>
      </div>
      <div v-else class="lead-description">No Descriptions</div>
      <span class="lead-amount">{{ lead.amount | currency }}</span>
      <span class="lead-last-update">{{ lead.lastUpdateDate }}</span>
      <LeadForecastDropdown
        :forecast="lead.forecastRef && lead.forecastRef.forecast"
        @updated-forecast="updateForecast"
      />
      <LeadStatusDropdown :status="lead.status" @updated-status="updateStatus" />
      <button class="route-to-detail">
        <img src="@/assets/images/keyboard_arrow_right.svg" @click="routeToLeadDetail" />
      </button>
    </div>

    <LeadDetails :lead="lead" v-if="showDetails" />
  </div>
</template>

<script>
import { getStatusSecondaryColor } from '@/services/getColorFromLeadStatus'
import LeadDetails from '@/components/leads-index/LeadDetails'
import LeadForecastDropdown from '@/components/shared/LeadForecastDropdown'
import LeadStatusDropdown from '@/components/shared/LeadStatusDropdown'
import Lead from '@/services/leads'
import Forecast from '@/services/forecasts'
import CloseLead from '@/components/shared/CloseLead'

export default {
  name: 'Lead',
  props: {
    lead: {
      type: Object,
      required: true,
    },
  },
  components: {
    LeadDetails,
    LeadForecastDropdown,
    LeadStatusDropdown,
    CloseLead,
  },
  data() {
    return {
      showDetails: false,
      modal: {
        isOpen: false,
      },
    }
  },
  methods: {
    toggleDetails() {
      this.showDetails = !this.showDetails
    },
    updateStatus(value) {
      if (value != 'CLOSED') {
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
    closeModal() {
      this.modal.isOpen = false
    },
    routeToLeadDetail() {
      this.$router.push({ name: 'LeadsDetail', params: { id: this.lead.id } })
    },
  },
  computed: {
    headerBackgroundColor() {
      return getStatusSecondaryColor(this.lead.status)
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';
@import '@/styles/mixins/buttons';

.lead {
  margin-bottom: 0.625rem;
}

.lead-header {
  @include disable-text-select();
  display: flex;
  flex-flow: row;
  align-items: center;
  height: 3rem;
}

.lead-name {
  @include pointer-on-hover();
  @include base-font-styles();
  width: 15%;
  padding-left: 1%;
  height: 1rem;
  font-weight: bold;
  font-size: 14px;
  line-height: 1.14;
  color: $main-font-gray;
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

.lead-description,
.lead-amount,
.lead-last-update {
  @include base-font-styles();
  font-size: 11px;
  line-height: 1.45;
  color: $main-font-gray;
}

.lead-description {
  width: 12.5%;

  .primary,
  .secondary {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 25ch; // this will look for the unicode position of a char and elipse after that char
  }
}

.lead-amount {
  width: 7.5%;
  padding-left: 0.625rem;
}

.lead-last-update {
  width: 5%;
}

.route-to-detail {
  @include secondary-button;
  margin-left: auto;
  margin-right: 1rem;
  height: 2rem;
  width: 2.5rem;
}
</style>
