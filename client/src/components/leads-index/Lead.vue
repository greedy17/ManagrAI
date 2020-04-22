<template>
  <div class="lead">
    <div class="lead-header" v-bind:style="headerBackgroundColor">
      <span class="lead-name" @click="toggleDetails"> {{ lead.name }} </span>
      <span class="lead-rating"> {{ lead.rating }} </span>
      <span class="lead-description"> {{ leadDescription }} </span>
      <span class="lead-amount"> {{ lead.amount | currency }} </span>
      <span class="lead-last-update"> {{ lead.lastUpdateDate }} </span>
      <LeadForecastDropdown :forecast="lead.forecast" />
      <LeadStatusDropdown :status="lead.status" />
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

export default {
  name: 'Lead',
  props: ['lead'],
  components: {
    LeadDetails,
    LeadForecastDropdown,
    LeadStatusDropdown,
    LeadList,
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
  },
  computed: {
    leadDescription() {
      let { primaryNote, secondaryNote } = this.lead
      let description = ''
      if (primaryNote) {
        description += primaryNote
      }
      if (secondaryNote) {
        if (primaryNote) {
          description += ' + ' + secondaryNote
        } else {
          description += secondaryNote
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
  width: 15%;
  padding-left: 1%;
  height: 1rem;
  font-family: $base-font-family, $backup-base-font-family;
  font-weight: bold;
  font-size: 14px;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.14;
  letter-spacing: normal;
  color: $main-font-gray;
}

.lead-rating {
  width: 4%;
  text-align: center;
  opacity: 0.5;
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 12px;
  font-weight: bold;
  font-stretch: normal;
  font-style: normal;
  line-height: normal;
  letter-spacing: 0.5px;
  color: $base-gray;
}

.lead-description,
.lead-amount,
.lead-last-update {
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 11px;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.45;
  letter-spacing: normal;
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
