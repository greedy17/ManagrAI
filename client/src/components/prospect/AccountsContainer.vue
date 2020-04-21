<template>
  <div class="accounts-container">
    <Account v-for="account in accounts" :key="account.id" :account="account" />
  </div>
</template>

<script>
import Account from '@/components/prospect/Account'

export default {
  name: 'AccountsContainer',
  props: ['accounts'],
  components: {
    Account,
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.accounts-container {
  @include standard-border();
  background-color: $white;
  padding-top: 1vh;
  padding-bottom: 1vh;
  width: 80vw;
}
</style>
