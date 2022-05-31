<template>
  <div class="forecast">
    <header class="forecast-header">
      <div>
        <Multiselect
          v-model="currentForecast"
          openDirection="below"
          selectLabel="Enter"
          :options="forecastOptions"
        >
          <template slot="noResult">
            <p class="multi-slot">No results.</p>
          </template>
          <template slot="placeholder">
            <p class="slot-icon">
              <img src="@/assets/images/search.png" alt="" />
              Select Forecast
            </p>
          </template>
        </Multiselect>
      </div>

      <button>
        <img src="@/assets/images/settings.png" alt="" />
      </button>
    </header>

    <section>
      <div class="table">
        <div class="table-row"></div>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'Forecast',
  data() {
    return {
      currentForecast: null,
      forecastOptions: ['My forecast', 'Team Forecast'],
    }
  },
  components: { Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect') },
  watch: {},
  method: {},
  computed: {
    user() {
      return this.$store.state.user
    },
  },
  mounted() {
    console.log(this.user)
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
.forecast {
  margin-top: 4rem;
}
.table {
  display: table;
  overflow: scroll;
  width: 100vw;

  &-row {
    display: table-row;
    left: 0;
  }
}
.forecast-header {
  display: flex;
  align-items: center;
  justify-content: space-between;

  button {
    background-color: white;
    border: 1px solid $soft-gray;
    height: 2rem;
    width: 2.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 3px;
  }
  button > img {
    height: 1rem;
    filter: invert(70%);
  }
}
.multi-slot {
  display: flex;
  align-items: center;
  justify-content: center;
  color: $gray;
  font-size: 12px;
  width: 100%;
  padding: 0.5rem 0rem;
  margin: 0;
  cursor: text;
  &__more {
    background-color: white;
    color: $dark-green;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    border-top: 1px solid #e8e8e8;
    width: 100%;
    padding: 0.75rem 0rem;
    margin: 0;
    cursor: pointer;

    img {
      height: 0.8rem;
      margin-left: 0.25rem;
      filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
        brightness(93%) contrast(89%);
    }
  }
}
.slot-icon {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0;
  margin: 0;
  img {
    height: 1rem;
    margin-right: 0.25rem;
    filter: invert(70%);
  }
}
</style>