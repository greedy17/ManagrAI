<template>
  <div class="lead">
    <div class="lead-header" v-bind:style="{ 'background-color': headerBackgroundColor }">
      <Checkbox
        class="checkbox"
        :checked="isSelected"
        @checkbox-clicked="$emit('checkbox-clicked', lead)"
      />
      <span class="lead-name" @click="toggleDetails">{{ lead.title }}</span>
      <span class="lead-rating">{{ lead.rating }}</span>
      <div v-if="lead.primaryDescription || lead.secondaryDescription" class="lead-description">
        <div class="primary">{{ lead.primaryDescription || '-Primary Not Set-' }}</div>
        <div class="secondary">{{ lead.secondaryDescription || '-Secondary Not Set-' }}</div>
      </div>
      <div v-else class="lead-description">No Descriptions</div>
      <span v-if="lead.status === Lead.CLOSED" class="lead-amount">
        {{ lead.closingAmount | currency }}
      </span>
      <span v-else class="lead-amount">{{ lead.amount | currency }}</span>
      <span class="lead-expected-close-date">{{ lead.expectedCloseDate | dateShort }}</span>
      <LeadForecastDropdown :lead="lead" />
      <LeadStatusDropdown :lead="lead" />
      <div class="last-action-taken">
        {{ lead.lastActionTaken.actionTimestamp | timeAgo }} - {{ lead.lastActionTaken.activity }}
      </div>
      <button class="route-to-detail">
        <img src="@/assets/images/keyboard-arrow-right.svg" @click="routeToLeadDetail" />
      </button>
    </div>

    <LeadDetails :lead="lead" v-if="showDetails" />
  </div>
</template>

<script>
import Lead from '@/services/leads'

import LeadDetails from '@/components/leads-index/LeadDetails'
import LeadForecastDropdown from '@/components/shared/LeadForecastDropdown'
import LeadStatusDropdown from '@/components/shared/LeadStatusDropdown'
import Checkbox from '@/components/leads-new/CheckBox'
import { getLightenedColor } from '@/services/getColorFromLeadStatus'

export default {
  name: 'Lead',
  props: {
    lead: {
      type: Object,
      required: true,
    },
    isSelected: {
      type: Boolean,
      required: true,
    },
  },
  components: {
    LeadDetails,
    LeadForecastDropdown,
    LeadStatusDropdown,
    Checkbox,
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
  },
  computed: {
    headerBackgroundColor() {
      return this.lead.statusRef
        ? getLightenedColor(this.lead.statusRef.color)
        : getLightenedColor('#9B9B9B')
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

.checkbox {
  margin-left: 1rem;
}

.lead-name {
  @include pointer-on-hover();
  @include base-font-styles();
  width: 15%;
  padding-left: 1%;
  height: 1rem;
  font-weight: bold;
  font-size: 0.875rem;
  line-height: 1.14;
  color: $main-font-gray;
}

.lead-rating {
  @include base-font-styles();
  width: 4%;
  text-align: center;
  opacity: 0.5;
  font-size: 0.75rem;
  font-weight: bold;
  letter-spacing: 0.5px;
  color: $base-gray;
}

.lead-description,
.lead-amount,
.lead-expected-close-date {
  @include base-font-styles();
  font-size: 0.6875rem;
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

.lead-expected-close-date {
  width: 10%;
}

.route-to-detail {
  @include secondary-button;
  margin-left: auto;
  margin-right: 1rem;
  height: 2rem;
  width: 2.5rem;
}

.last-action-taken {
  @include base-font-styles();
  font-size: 0.6875rem;
  margin-left: 4rem;
}
</style>
