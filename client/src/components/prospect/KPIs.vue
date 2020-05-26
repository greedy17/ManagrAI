<template>
  <div class="kpis">
    <div class="header section-shadow">
      KPIs
    </div>
  </div>
</template>

<script>
export default {
  name: 'KPIs',
  components: {},
  data() {
    return {}
  },
  methods: {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.kpis {
  @include standard-border();
  background-color: $white;

  display: flex;
  flex-flow: column;
}

.header {
  @include base-font-styles();
  color: $main-font-gray;
  line-height: 1.14;
  font-size: 1rem;
  font-weight: bold;
  height: 3rem;
  display: flex;
  flex-flow: column;
  justify-content: center;
  margin-bottom: 1rem;
  padding-left: 1rem;
}
</style>
