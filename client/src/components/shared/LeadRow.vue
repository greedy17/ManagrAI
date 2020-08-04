<template>
  <div class="lead">
    <div class="lead__container">
      <div class="lead__container__left">
        <span class="title">{{ lead.title }}</span>
        <span class="rating">{{ lead.rating }}</span>

        <slot name="left"></slot>
      </div>
      <div class="lead__container__center">
        <div v-if="lead.primaryDescription || lead.secondaryDescription" class="description">
          <div class="primary">{{ lead.primaryDescription || '-Primary Not Set-' }}</div>
          <div class="secondary">{{ lead.secondaryDescription || '-Secondary Not Set-' }}</div>
        </div>
        <div v-else class="description">No Descriptions</div>
        <span class="amount">{{
          lead.statusRef && lead.statusRef.title == Lead.CLOSED
            ? lead.closingAmount
            : lead.amount | currency
        }}</span>
        <div class="actions">
          <LeadForecastDropdown :lead="lead" :disabled="!belongsToCurrentUser" />
          <LeadStatusDropdown :lead="lead" :disabled="!belongsToCurrentUser" />
        </div>

        <slot name="center"></slot>
      </div>
      <div class="lead__container__right">
        <span>
          Claimed By
          {{
            belongsToCurrentUser
              ? 'You'
              : lead.claimedByRef.fullName.trim()
              ? lead.claimedByRef.fullName
              : lead.claimedByRef.email
          }}
        </span>
        <slot name="right"></slot>
      </div>
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
  name: 'LeadRow',
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
    belongsToCurrentUser() {
      return this.lead.claimedBy == this.$store.state.user.id
    },
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

.lead__container {
  display: flex;
  width: 100%;

  &__center {
    display: flex;
    flex: 1 0 auto;

    .actions {
      display: flex;
      justify-content: center;
    }
    .description {
      background-color: red;
      display: flex;
      flex-direction: column;
      width: 200px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .amount {
      width: 50px;
    }
  }
  &__left {
    display: flex;
    width: 300px;
    justify-self: flex-start;
    justify-content: space-between;

    .title {
      width: 200px;
      background-color: red;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .rating {
      background-color: green;
    }
  }
  &__right {
    display: flex;
    justify-self: flex-end;
  }
}
</style>
