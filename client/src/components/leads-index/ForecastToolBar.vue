<template>
  <div class="toolbar">
    <div class="header section-shadow">
      KPIs
    </div>
    <div class="single-statistic section-shadow">
      <span class="title">Total Closed Value</span>
      <span class="statistic"> {{ 33000 | currency }}</span>
    </div>
    <div class="single-statistic section-shadow">
      <span class="title">Average Contract Value</span>
      <span class="statistic"> {{ 12000 | currency }}</span>
    </div>
    <div class="single-statistic section-shadow">
      <span class="title">Forecast</span>
      <span class="statistic"> {{ 747000 | currency }}</span>
    </div>
    <div class="statistics-container section-shadow">
      <span class="title">Statistics</span>
      <div class="graphic-statistic section-shadow">
        <div class="icon-container">
          <img class="icon" src="@/assets/images/telephone.svg" alt="icon" />
        </div>
        <div class="information">
          <span class="top">
            50 Calls
          </span>
          <span class="bottom">
            Yesterday
          </span>
        </div>
      </div>
      <div class="graphic-statistic section-shadow">
        <div class="icon-container">
          <img class="icon" src="@/assets/images/email.svg" alt="icon" />
        </div>
        <div class="information">
          <span class="top">
            100 Emails
          </span>
          <span class="bottom">
            Today
          </span>
        </div>
      </div>
      <div class="graphic-statistic section-shadow">
        <div class="icon-container">
          <img class="icon" src="@/assets/images/message.svg" alt="icon" />
        </div>
        <div class="information">
          <span class="top">
            270 Actions
          </span>
          <span class="bottom">
            Today
          </span>
        </div>
      </div>
      <div class="graphic-statistic section-shadow">
        <div class="icon-container">
          <img class="icon" src="@/assets/images/check-box-filled-checked.svg" alt="icon" />
        </div>
        <div class="information">
          <span class="top">
            14 Closed
          </span>
          <span class="bottom">
            2/10/20
          </span>
        </div>
      </div>
      <div class="graphic-statistic section-shadow">
        <div class="icon-container">
          <img class="icon" src="@/assets/images/calendar.svg" alt="icon" />
        </div>
        <div class="information">
          <span class="top">
            10 Demos
          </span>
          <span class="bottom">
            1/30/20
          </span>
        </div>
      </div>
    </div>
    <div class="filter-container">
      <FilterByRep
        :reps="reps"
        :activeReps="activeReps"
        @toggle-rep-in-filter="toggleRepInFilter"
      />
    </div>
  </div>
</template>

<script>
import FilterByRep from '@/components/shared/FilterByRep'

const statusEnums = ['Ready', 'Trial', 'Demo', 'Waiting']
const forecastEnums = ['50/50', 'NA', 'Strong', 'Future', 'Verbal']
const exampleReps = [
  { id: 1, name: 'Marcy Ewald' },
  { id: 2, name: 'Pari Baker' },
  { id: 3, name: 'Bruno Garcia Gonzalez' },
]

export default {
  name: 'ForecastToolBar',
  components: { FilterByRep },
  data() {
    return {
      statusEnums,
      forecastEnums,
      reps: exampleReps,
      activeReps: {}, // for reps filter
    }
  },
  methods: {
    toggleRepInFilter(repID) {
      // depending on state of this.activeReps --> add or make false at that key
      // plainObject is used instead of an array because of O(1) lookup for <div class="rep" v-for.. />
      if (!this.activeReps[repID]) {
        this.activeReps = Object.assign({}, this.activeReps, { [repID]: true })
      } else {
        this.activeReps = Object.assign({}, this.activeReps, { [repID]: false })
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.toolbar {
  @include disable-text-select();
  @include standard-border();
  background-color: $white;
  width: 78%;
  height: auto;
  display: flex;
  flex-flow: column;
}

.toolbar,
.toolbar > * {
  @include base-font-styles();
  line-height: 1.14;
  color: $main-font-gray;
  font-size: 0.875rem;
}

.header {
  display: flex;
  flex-flow: column;
  justify-content: center;
  height: 3rem;
  padding-left: 7%;
  font-weight: bold;
}

.single-statistic {
  display: flex;
  flex-flow: column;
  align-items: center;
  justify-content: center;
  height: 4rem;
  .statistic {
    color: rgba($color: $main-font-gray, $alpha: 0.5);
    margin-top: 0.5rem;
  }
}

.statistics-container {
  height: auto;
  .title {
    display: flex;
    flex-flow: column;
    justify-content: center;
    height: 3rem;
    padding-left: 7%;
  }
}

.graphic-statistic {
  display: flex;
  flex-flow: row;
  align-items: center;
  height: 3rem;

  .icon-container {
    width: 30%;
    display: flex;
    align-items: center;
    justify-content: center;

    .icon {
      height: 1.25rem;
      width: 1.25rem;
    }
  }

  .information {
    display: flex;
    flex-flow: column;
    flex-grow: 1;

    .top {
      @include base-font-styles();
      font-size: 0.875rem;
      line-height: 1.14;
      color: $main-font-gray;
    }

    .bottom {
      @include base-font-styles();
      font-size: 0.875rem;
      line-height: 1.14;
      color: rgba($color: $main-font-gray, $alpha: 0.4);
    }
  }
}
.filter-container {
  height: auto;
  margin: 1.5rem 0;
}
</style>
