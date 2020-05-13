<template>
  <div class="organization-container">
    {{ activeTab }}
  </div>
</template>

<script>
export default {
  name: 'OrganizationContainer',
  props: {
    activeTab: {
      type: String,
      required: true,
      default: '',
    },
  },
  components: {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.organization-container {
  @include standard-border();
  background-color: $white;
  padding-top: 1vh;
  padding-bottom: 1vh;
  width: 80vw;
}
</style>
