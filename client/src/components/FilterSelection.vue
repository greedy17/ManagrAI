<template>
  <div class="filter-selection">
    <div>
      <div class="filter-selection__title">
        <select id="operators">
          <!-- <option value="" disabled selected hidden>{{ currentVals[field.apiName] }}</option> -->
          <option v-for="(option, i) in operators" :key="i">
            <p>{{ option }}</p>
          </option>
        </select>
      </div>

      <div class="filter-selection__body">
        <input id="update-input" type="text" />
      </div>
      <div class="filter-selection__footer">
        <p @click="$emit('filter-added')">Done</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FilterSelection',
  data() {
    return {
      operators: [
        'equals',
        'greater than',
        'greater or equal',
        'less than',
        'less or equal',
        'contains',
        'range',
      ],
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
  },
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';
// @import '@/styles/buttons';

#operators {
  border: none;
  border-bottom: 1px solid $very-light-gray;
  border-radius: 0.25rem;
  background-color: white;
  height: 3.5rem;
  width: 14vw;
}
#operators:focus {
  outline: none;
}
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
  z-index: 5;
  position: absolute;
  top: 6vh;
  left: 0;
  border-radius: 0.33rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: $white;
  width: 24vw;
  overflow: scroll;
  box-shadow: 1px 1px 7px 2px $very-light-gray;

  &__title {
    margin-top: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    position: sticky;
    top: 0;
    color: $base-gray;
  }

  &__body {
    display: flex;
    margin-top: 2rem;
    align-items: center;
    justify-content: center;
    width: 24vw;
  }

  &__footer {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 1rem;
    width: 100%;
    height: 2rem;
    border-top: 1px solid $soft-gray;
    p {
      cursor: pointer;
      color: $dark-green;
      font-weight: bold;
      padding-top: 0.5rem;
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