<template>
  <div class="filter-selection">
    <div>
      <p>Testing</p>

      <div class="filter-selection__title">
        <div>
          <input />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FilterSelection',
  data() {
    return {}
  },
  computed: {
    filteredFilters() {
      return this.oppFilters.filter((opp) =>
        opp.title.toLowerCase().includes(this.searchFilterText.toLowerCase()),
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
.filter-selection {
  z-index: 4;
  position: absolute;
  top: 6vh;
  left: 10vw;
  border-radius: 0.33rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  background-color: $white;
  min-width: 40vw;
  max-height: 25vh;
  overflow: scroll;
  box-shadow: 1px 1px 7px 2px $very-light-gray;
  padding: 1rem;
  &__title {
    position: sticky;
    top: 0;
    margin-bottom: 1rem;
    width: 100%;
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
  height: 4.5vh;
  background-color: transparent;
  border-bottom: 1px solid $very-light-gray;
  display: flex;
  align-items: center;
  padding: 2px;
  margin-right: 0.5rem;
}
</style>