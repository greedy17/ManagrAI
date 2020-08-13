<template>
  <div class="container">
    <div>{{ count === null ? 'N/A' : count }}</div>
    <div>{{ title }}</div>
    <div>Avg: {{ average === null ? 'N/A' : average }}</div>
  </div>
</template>

<script>
export default {
  name: 'StageDaysGraphic',
  props: ['count', 'title', 'average'],
  created() {},
  methods: {},
  watch: {},
  computed: {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/mixins/buttons';
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/mixins/inputs';
@import '@/styles/forms';

.container {
  border: 1px dashed black;
}
</style>
