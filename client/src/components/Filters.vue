<template>
  <div class="filter-section">
    <div class="filter-section__title">
      <div class="filter-search-bar wide">
        <input class="wide" type="search" v-model="searchFilterText" placeholder="Search filters" />
        <img src="@/assets/images/search.png" style="height: 1rem" alt="" />
      </div>
    </div>

    <div :key="i" v-for="(filter, i) in filteredFilters" class="filter-section__filters">
      <button
        @click="
          $emit('select-filter', filter.apiName, filter.dataType, filter.referenceDisplayLabel)
        "
        class="filter-button"
      >
        {{ filter.referenceDisplayLabel }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Filters',
  props: {
    filterFields: {},
  },
  data() {
    return {
      searchFilterText: '',
      oppFilters: [
        {
          title: 'Amount',
          type: 'number',
        },
        {
          title: 'Close date',
          type: 'date',
        },
        {
          title: 'Next step date',
          type: 'date',
        },
        {
          title: 'Last activity',
          type: 'date',
        },
        {
          title: 'Last modified',
          type: 'date',
        },
        {
          title: 'Owner',
          type: 'picklist',
        },
      ],
      monetaryOptions: ['less than', 'greater than', 'equals'],
    }
  },
  computed: {
    filteredFilters() {
      return this.filterFields.filter((filter) =>
        filter.referenceDisplayLabel.toLowerCase().includes(this.searchFilterText.toLowerCase()),
      )
    },
  },
  methods: {
    selectFilterOption(option) {
      if (option === 'less than' || option === 'greater than' || option === 'equals') {
        this.amountInput(option)
      }
    },
    amountInput(option) {
      this.enteringAmount = !this.enteringAmount
      this.filterOption = option
    },
    monetaryFilter(type, title) {
      this.filterType = type
      this.filterTitle = title
    },
    dateFilter(type, title) {
      this.filterType = type
      this.filterTitle = title
    },
    timeFilter(type, title) {
      this.filterType = type
      this.filterTitle = title
    },
    personFilter(type, title) {
      this.filterType = type
      this.filterTitle = title
    },
    closeFilters() {
      this.showList ? (this.showList = !this.showList) : (this.showList = this.showList)
      this.filtering = !this.filtering
    },
    applyAmountFilter() {
      // this.allOpps = this.allOpps.filter((opp) => opp.amount > this.amountValue)
    },
    selectFilter(type, title) {
      switch (type) {
        case 'monetary':
          this.monetaryFilter(type, title)
          break
        case 'date':
          this.dateFilter(type, title)
          break
        case 'time':
          this.timeFilter(type, title)
          break
        case 'person':
          this.personFilter(type, title)
          break
      }
    },
  },
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';
// @import '@/styles/buttons';

::placeholder {
  color: $very-light-gray;
}
.wide {
  display: flex;
  justify-content: center;
  width: 100%;
  background-color: white;
}
.filter-section {
  z-index: 4;
  position: absolute;
  top: 6vh;
  left: 0;
  border-radius: 0.33rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  background-color: $white;
  min-width: 20vw;
  max-height: 40vh;
  overflow: scroll;
  box-shadow: 1px 1px 7px 2px $very-light-gray;
  padding: 0rem 1rem;
  &__title {
    position: sticky;
    z-index: 5;
    background-color: white;
    top: 0;
    margin-bottom: 1rem;
    width: 100%;
    padding-top: 0.5rem;
  }
  &__filters {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    color: $gray;
    cursor: pointer;
    width: 100%;
    img {
      height: 0.8rem;
      filter: invert(30%);
      margin-right: 0.5rem;
    }
  }
}
.filter-button {
  display: flex;
  align-items: center;
  min-height: 4.5vh;
  width: 100%;
  background-color: transparent;
  border: none;
  padding: 0.75 0rem;
  border-radius: 0.2rem;
  color: #7a7777;
  cursor: pointer;
  font-size: 14px;
}
.filter-button:hover {
  color: $base-gray;
  background-color: $off-white;

  img {
    filter: invert(50%) sepia(20%) saturate(1581%) hue-rotate(94deg) brightness(93%) contrast(90%);
  }
}

.filter-search-bar {
  min-height: 5vh;
  background-color: white;
  border-bottom: 1px solid $very-light-gray;
  display: flex;
  align-items: center;
  // padding: 2px;
  margin: auto;
  padding: auto;
  // margin-right: 0.5rem;
}
</style>