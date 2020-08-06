<template>
  <div class="lead">
    <div
      @click="showDetails = !showDetails"
      class="lead__container"
      v-bind:style="{ 'background-color': headerBackgroundColor }"
    >
      <div class="lead__container__left">
        <slot name="left"></slot>
        <span class="title">{{ dataLead.title }}</span>
        <span class="rating">{{ dataLead.rating }}</span>
      </div>
      <div class="lead__container__center">
        <div
          v-if="dataLead.primaryDescription || dataLead.secondaryDescription"
          class="description"
        >
          <div class="primary">{{ dataLead.primaryDescription || '-Primary Not Set-' }}</div>
          <div class="secondary">{{ dataLead.secondaryDescription || '-Secondary Not Set-' }}</div>
        </div>
        <div v-else class="description">No Descriptions</div>
        <span class="amount">{{
          dataLead.statusRef && dataLead.statusRef.title == Lead.CLOSED
            ? dataLead.closingAmount
            : dataLead.amount | currency
        }}</span>

        <div class="actions">
          <LeadForecastDropdown
            :lead="dataLead"
            :disabled="!belongsToCurrentUser || dataLead.status == getIsClosedStatus.id"
          />
          <LeadStatusDropdown
            :lead="dataLead"
            :disabled="!belongsToCurrentUser || dataLead.status == getIsClosedStatus.id"
          />
        </div>

        <slot name="center"></slot>
      </div>
      <div class="lead__container__right">
        <span>
          Claimed By
          {{
            belongsToCurrentUser
              ? 'You'
              : dataLead.claimedByRef.fullName.trim()
              ? dataLead.claimedByRef.fullName
              : dataLead.claimedByRef.email
          }}
        </span>
        <slot name="right"></slot>
      </div>
    </div>
    <LeadDetails :lead="dataLead" v-if="showDetails" />
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
  name: 'LeadRow',
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
    Checkbox,
  },
  data() {
    return {
      Lead,
      showDetails: false,
      dataLead: this.lead,
    }
  },
  created() {
    this.dataLead = this.lead
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
    getStatuses() {
      return this.$store.state.stages
    },
    getIsClosedStatus() {
      return this.getStatuses.find(s => s.title == Lead.CLOSED)
    },
    belongsToCurrentUser() {
      return this.dataLead.claimedBy == this.$store.state.user.id
    },
    headerBackgroundColor() {
      return this.dataLead.statusRef
        ? getLightenedColor(this.dataLead.statusRef.color)
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
  width: 100%;
}
.lead__container {
  &:hover {
    cursor: pointer;
  }
  display: flex;
  align-items: center;

  height: 50px;
  font-size: 12px;
  > * {
    margin: 0.5rem;
    align-items: center;
  }
  &__center {
    display: flex;
    width: 33.3%;
    .actions {
      display: flex;
      justify-content: center;
      width: 10%;
    }
    .description {
      display: flex;
      flex-direction: column;

      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      width: 10%;
    }
    .amount {
      width: 10%;
    }
  }
  &__left {
    display: flex;
    width: 33.3%;

    justify-self: flex-start;
    justify-content: space-between;

    .title {
      font-size: 14px;
      width: 10%;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .rating {
      width: 10%;
    }
  }
  &__right {
    display: flex;
    justify-self: flex-end;
    width: 33.3%;
  }
}
</style>
