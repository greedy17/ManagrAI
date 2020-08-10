<template>
  <div class="lead">
    <div class="lead-header" :style="{ 'background-color': headerBackgroundColor }">
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
      <span class="lead-amount" v-if="lead.status === Lead.CLOSED">
        {{ lead.closingAmount | currency }}
      </span>
      <span class="lead-amount" v-else>{{ lead.amount | currency }}</span>
      <div class="close-date">
        <div v-if="lead.status === Lead.CLOSED">
          Closed On:
        </div>
        <div v-else>
          Expected Close:
        </div>
        <div>{{ lead.expectedCloseDate | dateShort }}</div>
      </div>
      <LeadForecastDropdown
        :inForecastView="true"
        :forecastProp="forecast"
        :lead="lead"
        :disabled="!belongsToCurrentUser"
        @move-lead-in-forecast-list="ePayload => $emit('move-lead-in-forecast-list', ePayload)"
      />
      <LeadStatusDropdown
        :lead="lead"
        :disabled="!belongsToCurrentUser"
        @closed-lead="emitMoveNewlyClosedLead"
      />

      <div class="last-action-taken">
        <template v-if="lead.lastActionTaken.actionTimestamp">
          <div>{{ lead.lastActionTaken.activity }}</div>
          <div>{{ lead.lastActionTaken.actionTimestamp | timeAgo }}</div>
        </template>
      </div>
      <div class="claimed-by">
        <button>
          <img class="icon" alt="icon" src="@/assets/images/claimed.svg" />
          <span>
            {{
              belongsToCurrentUser
                ? 'Yours'
                : lead.claimedByRef.fullName.trim()
                ? lead.claimedByRef.fullName
                : lead.claimedByRef.email
            }}
          </span>
        </button>
      </div>
      <button class="route-to-detail" @click="routeToLeadDetail">
        <img src="@/assets/images/keyboard-arrow-right.svg" />
      </button>
    </div>
    <LeadDetails :lead="lead" v-if="showDetails" />
  </div>
</template>

<script>
import Lead from '@/services/leads'
import Forecast from '@/services/forecasts'

import LeadDetails from '@/components/leads-index/LeadDetails'
import LeadForecastDropdown from '@/components/shared/LeadForecastDropdown'
import LeadStatusDropdown from '@/components/shared/LeadStatusDropdown'

import { getLightenedColor } from '@/services/getColorFromLeadStatus'

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
      Lead,
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
    emitMoveNewlyClosedLead() {
      let payload = {
        forecast: this.forecast,
        from: this.forecast.forecast,
        to: Forecast.CLOSED,
      }
      this.forecast.forecast = Forecast.CLOSED
      this.$emit('move-lead-in-forecast-list', payload)
    },
  },
  computed: {
    headerBackgroundColor() {
      return this.lead.statusRef
        ? getLightenedColor(this.lead.statusRef.color)
        : getLightenedColor('#9B9B9B')
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
.lead-amount {
  @include base-font-styles();
  font-size: 11px;
  line-height: 1.45;
  color: $main-font-gray;
}

.lead-description {
  width: 12%;

  .primary,
  .secondary {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 25ch; // this will look for the unicode position of a char and elipse after that char
  }
}

.lead-amount {
  width: 6.5%;
  padding-left: 0.625rem;
}

.claimed-by {
  min-width: 10%;
  margin-left: auto;
  display: flex;
  align-items: left;

  button {
    @include secondary-button;
    padding-right: 0.7rem;
    padding-left: 0.5rem;
    width: auto;
    display: flex;
    flex-flow: row;
    align-items: center;
    justify-content: left;
    width: 100%;

    span {
      margin-left: 1rem;
      overflow-x: hidden;
      text-overflow: ellipsis;
      max-width: 12ch; // this will look for the unicode position of a char and elipse after that char
    }
  }
}

.route-to-detail {
  @include secondary-button;
  border: 1px solid $mid-gray;
  margin-left: 1rem;
  margin-right: 1rem;
  height: 2rem;
  width: 2.5rem;
}

.close-date {
  font-size: 0.6875rem;
  width: 10%;
  margin-right: 2%;
}

.last-action-taken {
  font-size: 0.6875rem;
  margin-left: 2%;
}
</style>
