<template>
  <div class="forecast">
    <header>forecast forecast forecast</header>

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
    return {}
  },
  components: {},
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
</style>