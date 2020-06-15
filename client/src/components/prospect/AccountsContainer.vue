<template>
  <div class="accounts-container">
    <div v-if="accounts.length > 0" class="accounts">
      <Account
        v-for="accountWithLeads in accounts"
        :key="accountWithLeads.id"
        :account="accountWithLeads.account"
        :collection="accountWithLeads.collection"
      />
    </div>
    <span v-else class="no-items-message">
      No Accounts
    </span>
  </div>
</template>

<script>
import Account from '@/components/prospect/Account'

export default {
  name: 'AccountsContainer',
  props: {
    accounts: {
      type: Array,
      required: true,
    },
  },
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
.no-items-message {
  font-weight: bold;
  align-self: center;
  width: 25%;
  margin-left: 0.75rem;
}
</style>
