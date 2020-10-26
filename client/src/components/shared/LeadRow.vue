<template>
  <div class="lead">
    <div
      @click="showDetails = !showDetails"
      class="lead__container"
      v-bind:style="{ 'background-color': headerBackgroundColor }"
    >
      <div class="lead__container__left">
        <slot name="left"></slot>
        <span class="score">
          <LeadScore :lead="lead" />
        </span>
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
        <span class="amount">
          {{
          dataLead.statusRef && dataLead.statusRef.title == Lead.CLOSED
          ? dataLead.closingAmount
          : dataLead.amount | currency
          }}
        </span>

        <div class="actions">
          <LeadForecastDropdown
            :lead="dataLead"
            :disabled="
              (!belongsToCurrentUser && !isManager) || dataLead.status == getIsClosedStatus.id
            "
            @move-lead-in-forecast-list="data => $emit('move-lead-in-forecast-list', data)"
          />
          <LeadStatusDropdown
            :lead="dataLead"
            :disabled="
              (!belongsToCurrentUser && !isManager) || dataLead.status == getIsClosedStatus.id
            "
            @status-changed="onUpdateLocalStatus"
          />
        </div>

        <slot name="center"></slot>
      </div>
      <div class="lead__container__right">
        <slot name="right">
          <span class="claim-label" v-if="dataLead.claimedBy">
            Claimed By:
            <br />
            <span class="claim-info">
              {{
              belongsToCurrentUser
              ? 'You'
              : dataLead.claimedByRef.fullName.trim()
              ? dataLead.claimedByRef.fullName
              : dataLead.claimedByRef.email
              }}
            </span>
          </span>
        </slot>
        <span class="go-to" @click="openLeadDetail">
          <svg class="icon" fill="black" width="24px" height="24px" viewBox="0 0 30 30">
            <use xlink:href="@/assets/images/svg-repo.svg#caret" />
          </svg>
        </span>
      </div>
    </div>
    <LeadDetails :lead="dataLead" v-if="showDetails" />
  </div>
</template>

<script>
import Lead from '@/services/leads'
import { getLightenedColor } from '@/services/getColorFromLeadStatus'

import LeadDetails from '@/components/leads-index/LeadDetails'
import LeadForecastDropdown from '@/components/shared/LeadForecastDropdown'
import LeadStatusDropdown from '@/components/shared/LeadStatusDropdown'
import Checkbox from '@/components/leads-new/CheckBox'
import LeadScore from '@/components/shared/LeadScore'

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
    LeadScore,
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
    onUpdateLocalStatus(val) {
      // if status update was successful or was not closed then update it manually
      // No need to call the whole endpoint again
      this.dataLead = { ...this.dataLead, statusRef: val, status: val.id }
    },
    toggleDetails() {
      this.showDetails = !this.showDetails
    },
    openLeadDetail() {
      let routeData = this.$router.resolve({ name: 'LeadsDetail', params: { id: this.lead.id } })
      window.open(routeData.href, '_blank')
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
      if (this.dataLead.claimedBy) {
        return this.dataLead.claimedBy == this.$store.state.user.id
      }
      return false
    },
    isManager() {
      return this.$store.state.user.isManager
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
  margin: 0.5rem 0rem;
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
    align-items: center;
  }
  &__center {
    display: flex;
    overflow-y: scroll;
    flex: 1 0 auto;
    > * {
      margin: 0rem 0.2rem;
    }
    .actions {
      display: flex;
      justify-content: center;
    }
    .description {
      display: flex;
      flex-direction: column;
      width: 5rem;
      font-size: 0.625rem;
      > * {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    }
    .amount {
      width: 4rem;
      font-size: 0.625rem;
    }
  }
  &__left {
    display: flex;
    justify-self: flex-start;
    justify-content: space-between;
    margin: 0 0.2rem;

    .score {
      margin: 0 0.5rem 0 0.3rem;
    }
    .title {
      font-size: 14px;
      width: 10rem;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .rating {
      width: 3rem;
      font-size: 0.625rem;
    }
  }
  &__right {
    display: flex;
    justify-self: flex-end;
    margin-right: 0.2rem;
    .go-to {
    }
  }
}

.claim-label {
  font-size: 0.625rem;
}

.go-to {
  margin-right: 1rem;
}
</style>
