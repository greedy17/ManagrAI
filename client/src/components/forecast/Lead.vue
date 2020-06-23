<template>
  <div class="lead">
    <div class="lead-header" v-bind:style="headerBackgroundColor">
      <span class="lead-name" @click="toggleDetails"> {{ lead.title }} </span>
      <span class="lead-rating"> {{ lead.rating }} </span>
      <div v-if="lead.primaryDescription || lead.secondaryDescription" class="lead-description">
        <div class="primary">
          {{ lead.primaryDescription || '-Primary Not Set-' }}
        </div>
        <div class="secondary">
          {{ lead.secondaryDescription || '-Secondary Not Set-' }}
        </div>
      </div>
      <div v-else class="lead-description">
        No Descriptions
      </div>
      <span class="lead-amount"> {{ lead.amount | currency }} </span>
      <span class="lead-last-update"> {{ lead.lastUpdateDate }} </span>
      <LeadForecastDropdown
        :inForecastView="true"
        :forecastProp="forecast"
        :lead="lead"
        :disabled="!belongsToCurrentUser"
        @move-lead-in-forecast-list="ePayload => $emit('move-lead-in-forecast-list', ePayload)"
      />
      <LeadStatusDropdown :lead="lead" :disabled="!belongsToCurrentUser" />
      <div class="claimed-by">
        <button>
          <img class="icon" alt="icon" src="@/assets/images/claimed.svg" />
          <span>{{ belongsToCurrentUser ? 'Yours' : lead.claimedByRef.fullName }}</span>
        </button>
      </div>
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
  },
  data() {
    return {
      showDetails: false,
    }
  },
  methods: {
    toggleDetails() {
      this.showDetails = !this.showDetails
    },
    routeToLeadDetail() {
      this.$router.push({ name: 'LeadsDetail', params: { id: this.lead.id } })
    },
  },
  computed: {
    headerBackgroundColor() {
      return getStatusSecondaryColor(this.lead.status)
    },
    belongsToCurrentUser() {
      return this.$store.state.user.id == this.lead.claimedBy
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

.claimed-by {
  width: 28%;
  display: flex;
  align-items: center;
  padding-left: 2rem;

  button {
    @include secondary-button;
    padding-right: 0.7rem;
    padding-left: 0.5rem;
    width: auto;
    display: flex;
    flex-flow: row;
    align-items: center;

    span {
      margin-left: 1rem;
    }
  }
}

.route-to-detail {
  @include secondary-button;
  margin-left: auto;
  margin-right: 1rem;
  height: 2rem;
  width: 2.5rem;
}
</style>
