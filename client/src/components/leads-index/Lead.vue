<template>
  <div class="lead">
    <div class="lead-header" v-bind:style="headerBackgroundColor">
      <span class="lead-name" @click="toggleDetails"> {{ lead.name }} </span>
      <span class="lead-rank"> {{ lead.rank }} </span>
      <span class="lead-description"> {{ leadDescription }} </span>
      <span class="lead-amount"> {{ leadAmount }} </span>
      <span class="lead-last-update"> {{ lead.lastUpdateDate }} </span>
      <div class="lead-forecast-container">
        <span class="lead-forecast"> {{ lead.forecast }} </span>
        <img src="@/assets/images/dropdown-arrow.svg" alt="dropdown arrow icon" />
      </div>
      <div class="lead-status-container">
        <span class="lead-status" :style="statusBackgroundColor">
          {{ lead.status }}
        </span>
        <img src="@/assets/images/dropdown-arrow.svg" alt="dropdown arrow icon" />
      </div>
      <div class="lead-lists">
        <div class="lead-list-container">
          <span class="lead-list">
            Growth Accounts
          </span>
          <img class="remove-list-icon" src="@/assets/images/remove.svg" alt="remove icon" />
        </div>
        <div class="lead-list-container">
          <span class="lead-list">
            Q2 Buyers
          </span>
          <img class="remove-list-icon" src="@/assets/images/remove.svg" alt="remove icon" />
        </div>
      </div>
      <span class="lead-add-list">
        <img class="add-list-icon" src="@/assets/images/add.svg" alt="add icon" />
      </span>
    </div>
    <LeadDetails :lead="lead" v-if="showDetails" />
  </div>
</template>

<script>
import { getStatusPrimaryColor, getStatusSecondaryColor } from '@/services/getColorFromLeadStatus'
import currencyFormatter from '@/services/currencyFormatter'
import LeadDetails from '@/components/leads-index/LeadDetails'

export default {
  name: 'Lead',
  props: ['lead'],
  components: {
    LeadDetails,
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
    statusBackgroundColor() {
      return getStatusPrimaryColor(this.lead.status)
    },
    leadAmount() {
      return currencyFormatter.format(this.lead.amount)
    },
  },
}
</script>

<style lang="scss" scoped>
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');

.lead {
  margin-bottom: 10px;
}

.lead-header {
  display: flex;
  flex-flow: row;
  align-items: center;
  height: 49px;
}

.lead-name {
  width: 15%;
  padding-left: 1%;
  height: 16px;
  font-family: 'Lato', sans-serif;
  font-weight: bold;
  font-size: 14px;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.14;
  letter-spacing: normal;
  color: #110f24;

  &:hover {
    cursor: pointer;
  }
}

.lead-rank {
  width: 4%;
  text-align: center;
  opacity: 0.5;
  font-family: 'Lato', sans-serif;
  font-size: 12px;
  font-weight: bold;
  font-stretch: normal;
  font-style: normal;
  line-height: normal;
  letter-spacing: 0.5px;
  color: #444444;
}

.lead-description,
.lead-amount,
.lead-last-update {
  font-family: 'Lato', sans-serif;
  font-size: 11px;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.45;
  letter-spacing: normal;
  color: #110f24;
}

.lead-description {
  width: 12.5%;
}

.lead-amount {
  width: 7.5%;
  padding-left: 10px;
}

.lead-last-update {
  width: 5%;
}

.lead-forecast-container {
  width: 12%;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.lead-forecast {
  border-radius: 100px;
  width: 65px;
  padding: 2px 15px;
  background-color: #9596b4;
  font-family: 'Lato', sans-serif;
  font-size: 10px;
  font-weight: bold;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.6;
  letter-spacing: normal;
  text-align: center;
  color: #ffffff;
}

.lead-status-container {
  width: 9%;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.lead-status {
  border-radius: 100px;
  width: 35px;
  padding: 2px 15px;
  font-family: Lato;
  font-size: 10px;
  font-weight: bold;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.6;
  letter-spacing: normal;
  text-align: center;
  color: #ffffff;
}

.lead-lists {
  width: 28%;
  display: flex;
}

.lead-list-container {
  display: flex;
  align-items: center;
  margin: 0 1vh;
  width: 142px;
  height: 24px;
  border-radius: 5px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  background-color: #ffffff;
}

.lead-list {
  padding-left: 5%;
  width: 70%;
  font-family: Lato;
  font-size: 11px;
  font-weight: bold;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.45;
  letter-spacing: normal;
  color: #484a6e;
  text-decoration: underline;
}

.remove-list-icon {
  height: 55%;
  margin-left: auto;
  padding-right: 5%;
}

.lead-add-list {
  width: 5%;
  display: flex;
}

.add-list-icon {
  background-color: #eff0f5;
  border-radius: 5px;
  height: 15px;
  width: 15px;
  margin-left: auto;
  margin-right: 15%;
}
</style>
