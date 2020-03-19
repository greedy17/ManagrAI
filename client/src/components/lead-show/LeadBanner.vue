<template>
  <div class="lead-banner" v-bind:style="bannerBackgroundColor">
    <div class="forecast-container">
      <span class="forecast-label">Forecast</span>
      <div class="forecast-dropdown">
        <span class="forecast"> {{ lead.forecast }} </span>
        <img src="@/assets/images/dropdown-arrow.svg" alt="dropdown arrow icon" />
      </div>
    </div>
    <div class="status-container">
      <div class="status-dropdown">
        <span class="status" :style="statusBackgroundColor">
          {{ lead.status }}
        </span>
        <img src="@/assets/images/dropdown-arrow.svg" alt="dropdown arrow icon" />
      </div>
    </div>
    <div class="days-in-status-container">
      <span class="days-in-status-label">Days In Status</span>
      <span class="days-in-status">7 Days</span>
    </div>
    <div class="banner-buttons">
      <div class="banner-button">
        <img class="button-icon" src="@/assets/images/undo.svg" alt="reset icon" />
        <span class="button-content">Reset</span>
      </div>
      <div class="banner-button">
        <img class="button-icon" src="@/assets/images/remove.svg" alt="release icon" />
        <span class="button-content">Release</span>
      </div>
    </div>
  </div>
</template>

<script>
import { getStatusPrimaryColor, getStatusSecondaryColor } from '@/services/getColorFromLeadStatus'

export default {
  name: 'LeadBanner',
  props: {
    lead: Object,
  },
  computed: {
    bannerBackgroundColor() {
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

.lead-banner {
  height: 49px;
  display: flex;
  flex-flow: row;
  align-items: center;
}

.forecast-container {
  width: 25%;
  padding-left: 2%;
  display: flex;
  flex-flow: row;
  align-items: center;

  .forecast-label {
    font-family: 'Lato', sans-serif;
    font-size: 12px;
    font-weight: bold;
    font-stretch: normal;
    font-style: normal;
    line-height: 2.25;
    letter-spacing: normal;
    color: #110f24;
  }

  .forecast-dropdown {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-left: auto;

    .forecast {
      border-radius: 100px;
      padding: 2px 8px;
      font-family: 'Lato', sans-serif;
      font-size: 12px;
      font-weight: normal;
      font-stretch: normal;
      font-style: normal;
      line-height: 1.6;
      letter-spacing: normal;
      text-align: center;
      color: #110f24;
    }

    &:hover {
      cursor: pointer;
    }
  }
}

.status-container {
  width: 18%;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;

  .status-dropdown {
    display: flex;
    flex-flow: row;
    align-items: center;

    .status {
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

    &:hover {
      cursor: pointer;
    }
  }
}

.days-in-status-container {
  width: 29%;
  display: flex;
  flex-flow: row;
  align-items: center;
  justify-content: center;
}

.days-in-status-label {
  font-family: 'Lato', sans-serif;
  font-size: 12px;
  font-weight: bold;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.71;
  letter-spacing: normal;
  color: #110f24;
  margin-right: 5%;
}

.days-in-status {
  font-family: 'Lato', sans-serif;
  font-size: 12px;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  line-height: 2.25;
  letter-spacing: normal;
  color: #110f24;
}

.banner-buttons {
  flex-grow: 1;
  display: flex;
  flex-flow: row;
  align-items: center;
}

.banner-button {
  margin: 0 4% 0 auto;
  display: flex;
  flex-flow: row;
  align-items: center;
  padding: 5px 10px;
  border-radius: 5px;
  background-color: #efeff5;
  font-family: 'Lato', sans-serif;
  font-size: 11px;
  font-weight: bold;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.45;
  letter-spacing: normal;
  color: #110f24;

  .button-icon {
    height: 16px;
    width: 16px;
  }

  &:hover {
    cursor: pointer;
  }
}
</style>
