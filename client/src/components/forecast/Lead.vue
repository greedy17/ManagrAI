<template>
  <div class="lead">
    <Modal v-if="modal.isOpen" dimmed @close-modal="closeModal" :width="50">
      <CloseLead :lead="lead" />
    </Modal>
    <div class="lead-header" v-bind:style="headerBackgroundColor">
      <span class="lead-name" @click="toggleDetails"> {{ lead.title }} </span>
      <span class="lead-rating"> {{ lead.rating }} </span>
      <span class="lead-description">
        {{
          lead.primaryDescription || lead.secondaryDescription ? leadDescription : 'No Descriptions'
        }}
      </span>
      <span class="lead-amount"> {{ lead.amount | currency }} </span>
      <span class="lead-last-update"> {{ lead.lastUpdateDate }} </span>
      <LeadForecastDropdown :forecast="forecast.forecast" @updated-forecast="updateForecast" />
      <LeadStatusDropdown :status="lead.status" @updated-status="updateStatus" />
      <div class="lead-lists">
        <LeadList class="lead-list" :listName="'Growth Accounts'" />
        <LeadList class="lead-list" :listName="'Q2 Buyers'" />
      </div>
      <span class="lead-add-list">
        <img class="add-list-icon" src="@/assets/images/add.svg" alt="icon" />
      </span>
    </div>
    <LeadDetails :lead="lead" v-if="showDetails" />
  </div>
</template>

<script>
import { getStatusSecondaryColor } from '@/services/getColorFromLeadStatus'
import LeadDetails from '@/components/leads-index/LeadDetails'
import LeadForecastDropdown from '@/components/shared/LeadForecastDropdown'
import LeadStatusDropdown from '@/components/shared/LeadStatusDropdown'
import LeadList from '@/components/shared/LeadList'
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
    forecast: {
      type: Object,
      required: true,
    },
  },
  components: {
    LeadDetails,
    LeadForecastDropdown,
    LeadStatusDropdown,
    LeadList,
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
      if (this.forecast && this.forecast.id) {
        // since forecast exists, patch forecast
        let patchData = {
          lead: this.lead.id,
          forecast: value,
        }
        Forecast.api.update(this.forecast.id, patchData).then(() => {
          this.$emit('delete-lead', this.lead.id)
        })
      } else {
        // since currently null, create forecast
        Forecast.api.create(this.lead.id, value).then(response => {
          this.lead.forecastRef = response
          this.lead.forecast = response.id
        })
      }
    },
    closeModal() {
      this.modal.isOpen = false
    },
  },
  computed: {
    leadDescription() {
      let { primaryDescription, secondaryDescription } = this.lead
      let description = ''
      if (primaryDescription) {
        description += primaryDescription
      }
      if (secondaryDescription) {
        if (primaryDescription) {
          description += ' + ' + secondaryDescription
        } else {
          description += secondaryDescription
        }
      }
      let sliced = description.slice(0, 50)
      if (sliced.length > description.length) {
        sliced += '...'
      }
      return sliced
    },
    headerBackgroundColor() {
      return getStatusSecondaryColor(this.lead.status)
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

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
}

.lead-amount {
  width: 7.5%;
  padding-left: 0.625rem;
}

.lead-last-update {
  width: 5%;
}

.lead-lists {
  width: 28%;
  display: flex;
  align-items: center;
}

.lead-list {
  margin: 0 1vh;
}

.lead-add-list {
  width: 5%;
  display: flex;
}

.add-list-icon {
  @include pointer-on-hover();
  background-color: $soft-gray;
  border-radius: 5px;
  height: 1rem;
  width: 1rem;
  margin-left: auto;
  margin-right: 15%;
}
</style>
