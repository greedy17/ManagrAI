<template>
  <div class="organization-container">
    {{ activeTab }}

    <OrganizationDetails :organization="data.list[0]" v-if="activeTab == 'details'" />
  </div>
</template>

<script>
import OrganizationDetails from './OrganizationDetails'

export default {
  name: 'OrganizationContainer',
  props: {
    activeTab: {
      type: String,
      required: true,
      default: '',
    },
    tabs: {
      type: Array,
      default: () => [],
    },
    data: {
      type: Object,
    },
  },
  components: { OrganizationDetails },
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
