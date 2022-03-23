<template>
  <div v-if="filtering" class="filter-section">
    <div class="flex-row-spread wide">
      <p class="filter-section__title">All Filters</p>
      <img @click="closeFilters" class="exit" src="@/assets/images/close.png" alt="" />
    </div>
    <div class="wide" style="display: flex; justify-content: center">
      <div style="margin-left: 0.5rem" class="search-bar wide">
        <input class="wide" type="search" v-model="searchFilterText" placeholder="Search filters" />
        <img src="@/assets/images/search.png" style="height: 1rem" alt="" />
      </div>
    </div>

    <small v-if="filterTitle" class="filter-title"
      >{{ filterTitle + ' ' + (filterOption ? filterOption : '') }}:</small
    >
    <div v-if="filterType && !enteringAmount" class="filter-option-section">
      <button
        @click="selectFilterOption(option)"
        class="filter-option-button"
        :key="option"
        v-for="option in monetaryOptions"
      >
        {{ option }}
      </button>
    </div>
    <div v-if="filterType && enteringAmount" class="filter-option-section">
      <input class="search-bar" v-model="amountValue" type="text" />
      <button
        @click="applyAmountFilter"
        :disabled="!amountValue"
        :class="!amountValue ? 'disabled-button' : 'add-button'"
      >
        add
      </button>
    </div>

    <div :key="i" v-for="(filter, i) in filteredFilters" class="filter-section__filters">
      <button
        @click="selectFilter(filter.type, filter.title)"
        style="margin-top: -0.5rem"
        class="list-button"
      >
        <img
          v-if="filter.type === 'monetary'"
          src="@/assets/images/monetary.png"
          class="img"
          alt=""
        />
        <img v-if="filter.type === 'date'" src="@/assets/images/date.png" class="img" alt="" />
        <img v-if="filter.type === 'time'" src="@/assets/images/time.png" class="img" alt="" />
        <img v-if="filter.type === 'person'" src="@/assets/images/person.png" class="img" alt="" />
        {{ filter.title }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Filters',
  data() {
    return {
      oppFilters: [
        {
          title: 'Amount',
          type: 'monetary',
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
          type: 'time',
        },
        {
          title: 'Last modified',
          type: 'time',
        },
        {
          title: 'Owner',
          type: 'person',
        },
      ],
      monetaryOptions: ['less than', 'greater than', 'equals'],
    }
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