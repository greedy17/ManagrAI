<template>
  <div class="accounts-container">
    <div v-if="accounts.length > 0" class="accounts">
      <Account
        v-for="accountWithLeads in accounts"
        :key="accountWithLeads.id"
        :account="accountWithLeads.account"
        :collection="accountWithLeads.collection"
        @load-more="$emit('load-more')"
      />
      <template v-if="!accountsCollection.refreshing && !!accountsCollection.pagination.next">
        <button
          v-if="!accountsCollection.loadingNextPage"
          class="load-more-button"
          @click.prevent="$emit('load-more')"
        >
          Load More
        </button>
        <ComponentLoadingSVG v-else :style="{ margin: '0.5rem auto' }" />
      </template>
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
    accountsCollection: {
      type: Object,
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
@import '@/styles/mixins/buttons';

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
.load-more-button {
  @include primary-button;
  margin: 0.5rem auto;
}
</style>
