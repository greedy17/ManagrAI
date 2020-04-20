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

.accounts-container {
  background-color: $white;
  padding-top: 1vh;
  padding-bottom: 1vh;
  border: 1px solid $soft-gray;
  width: 80vw;
}
</style>
