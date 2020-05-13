<template>
  <div class="accounts-container">
    <div v-if="accounts.length > 0" class="accounts">
      <Account v-for="account in accounts" :key="account.id" :account="account" />
    </div>
    <div v-else class="placeholder-message">
      <h2>No Accounts</h2>
    </div>
  </div>
</template>

<script>
import Account from '@/components/prospect/Account'

export default {
  name: 'AccountsContainer',
  props: {
    accounts: {
      type: Array,
      default: () => [],
      required: true,
    },
  },
  components: {
    Account,
  },
  methods: {},
  computed: {},
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
