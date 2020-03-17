<template>
  <div class="lead">
    <div class="lead-header" @click="toggleDetails" v-bind:style="headerBackgroundColor">
      <span class="lead-name"> {{ lead.name }} </span>
      <span class="lead-rank"> {{ lead.rank }} </span>
      <span class="lead-description"> {{ leadDescription }} </span>
      <span class="lead-amount"> {{ lead.amount }} </span>
      <span class="lead-last-update"> {{ lead.lastUpdateDate }} </span>
      <span class="lead-forecast"> {{ lead.forecast }} </span>
      <span class="lead-status" v-bind:style="statusBackgroundColor">
        {{ lead.status }}
      </span>
      <div class="lead-lists">
        <span class="lead-list"> List One </span>
        <span class="lead-list"> List Two </span>
      </div>
    </div>
    <div class="lead-details" v-if="showDetails">
      Showing Lead Details...
    </div>
  </div>
</template>

<script>
import { getStatusPrimaryColor, getStatusSecondaryColor } from '@/services/getColorFromLeadStatus'

export default {
  name: 'Lead',
  props: ['lead'],
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
      return description.slice(0, 34) + '...'
    },
    headerBackgroundColor() {
      return getStatusSecondaryColor(this.lead.status)
    },
    statusBackgroundColor() {
      return getStatusPrimaryColor(this.lead.status)
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

  &:hover {
    cursor: pointer;
  }

  /* temprorary: */
  & > * {
    flex-grow: 1;
  }
}

.lead-name {
  margin-left: 1%;
  height: 16px;
  font-family: 'Lato', sans-serif;
  font-weight: bold;
  font-size: 14px;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.14;
  letter-spacing: normal;
  color: #110f24;
}

.lead-rank {
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

.lead-forecast {
  border-radius: 100px;
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

.lead-status {
  border-radius: 100px;
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
}

.lead-details {
  padding-left: 4%;
}

.lead-lists {
  display: inline-block;
}
</style>
