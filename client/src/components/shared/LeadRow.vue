<template>
  <div class="lead" @click="showDetails = !showDetails">
    <div class="lead__container" v-bind:style="{ 'background-color': headerBackgroundColor }">
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
          <LeadForecastDropdown :lead="dataLead" :disabled="!belongsToCurrentUser" />
          <LeadStatusDropdown :lead="dataLead" :disabled="!belongsToCurrentUser" />
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
  &:hover {
    cursor: pointer;
  }
}
.lead__container {
  display: flex;
  align-items: center;
  width: 100%;
  height: 50px;
  font-size: 12px;
  > * {
    margin: 0.5rem;
    align-items: center;
  }
  &__center {
    display: flex;
    flex: 1 0 auto;

    .actions {
      display: flex;
      justify-content: center;
    }
    .description {
      display: flex;
      flex-direction: column;
      width: 200px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .amount {
      width: 100px;
    }
  }
  &__left {
    display: flex;
    width: 300px;
    justify-self: flex-start;
    justify-content: space-between;

    .title {
      width: 200px;
      font-size: 14px;

      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .rating {
    }
  }
  &__right {
    display: flex;
    justify-self: flex-end;
  }
}
</style>
