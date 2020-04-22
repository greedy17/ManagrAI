<template>
  <div class="toolbar">
    <div class="header section-shadow">
      Sort + Filter
    </div>
    <div class="sort section-shadow">
      <div class="sort-header">
        <span class="content">Update Date</span>
        <img class="icon" src="@/assets/images/dropdown-arrow.svg" alt="icon" />
      </div>
    </div>
    <div class="sort section-shadow">
      <div class="sort-header">
        <span class="content">Amount</span>
        <img class="icon" src="@/assets/images/dropdown-arrow.svg" alt="icon" />
      </div>
    </div>
    <div class="filter section-shadow">
      <div class="filter-header">Rating</div>
      <div class="filter-options">
        <LeadRating class="option" :rating="5" />
        <LeadRating class="option" :rating="4" />
        <LeadRating class="option" :rating="3" />
        <LeadRating class="option" :rating="2" />
        <LeadRating class="option" :rating="1" />
      </div>
    </div>
    <div class="filter section-shadow">
      <div class="filter-header">Status</div>
      <div class="filter-options">
        <div class="option" v-for="status in statusEnums" :key="status">{{ status }}</div>
      </div>
    </div>
    <div class="filter section-shadow">
      <div class="filter-header">List</div>
      <div class="filter-options">
        <LeadList
          class="option list"
          :dark="true"
          v-for="list in listEnums"
          :key="list"
          :listName="list"
        />
      </div>
    </div>
    <div class="filter">
      <div class="filter-header">Forecast</div>
      <div class="filter-options">
        <div class="option" v-for="forecast in forecastEnums" :key="forecast">{{ forecast }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import LeadRating from '@/components/shared/LeadRating'
import LeadList from '@/components/shared/LeadList'

const statusEnums = ['Ready', 'Trial', 'Demo', 'Waiting']
const forecastEnums = ['50/50', 'NA', 'Strong', 'Future', 'Verbal']
const listEnums = ['Growth Accounts', 'Q2 Buyers']

export default {
  name: 'ListsToolBar',
  components: {
    LeadRating,
    LeadList,
  },
  data() {
    return {
      statusEnums,
      forecastEnums,
      listEnums,
    }
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
  font-family: $base-font-family, $backup-base-font-family;
  font-stretch: normal;
  font-style: normal;
  letter-spacing: normal;
  line-height: 1.14;
  color: $main-font-gray;
  font-size: 14px;
}

.header,
.sort {
  display: flex;
  flex-flow: column;
  justify-content: center;
  height: 3rem;
}

.header {
  padding-left: 7%;
  font-weight: bold;
}

.sort {
  padding-left: 10%;
  font-weight: normal;
}

.sort-header {
  display: flex;
  flex-flow: row;
  align-items: center;

  .icon {
    margin: 0 10% 0 auto;
  }
}

.filter {
  .filter-header {
    height: 3rem;
    display: flex;
    flex-flow: column;
    justify-content: center;
    padding-left: 10%;
    font-weight: normal;
  }

  .filter-options {
    padding-left: 14%;
    margin-bottom: 1.25rem;
    color: rgba($color: $main-font-gray, $alpha: 0.4);

    .option {
      height: 1.75rem;
    }
  }
}

.list {
  margin-bottom: 0.875rem;
}
</style>
