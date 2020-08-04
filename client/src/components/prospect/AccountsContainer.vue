<template>
  <div>
    <div class="accounts-container" ref="accountsContainer">
      <template v-if="accounts.length && isFilteringActive && zeroLeadsPresent">
        <br />
        <span class="no-items-message">
          Sorry! Your search did not return any results!
        </span>
        <br />
        <br />
      </template>
      <div v-if="accounts.length" class="accounts">
        <Account
          v-for="accountWithLeads in accounts"
          :key="accountWithLeads.id"
          :account="accountWithLeads.account"
          :collection="accountWithLeads.collection"
          :isFilteringActive="isFilteringActive"
        />
      </div>
      <span v-else class="no-items-message">
        No Accounts
      </span>
    </div>
    <Pagination
      v-if="!accountsCollection.refreshing && accounts.length"
      style="margin-top: 0.5rem; width: 80vw;"
      :collection="accountsCollection"
      :model="'Account'"
      :emit="true"
      @on-left-arrow-click="$emit('on-left-arrow-click')"
      @on-page-click="pageNumber => $emit('on-page-click', pageNumber)"
      @on-right-arrow-click="$emit('on-right-arrow-click')"
    />
  </div>
</template>

<script>
import Account from '@/components/prospect/Account'
import Pagination from '@/components/shared/Pagination'

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
    isFilteringActive: {
      type: Boolean,
      required: true,
    },
  },
  components: {
    Account,
    Pagination,
  },
  computed: {
    zeroLeadsPresent() {
      return !this.accounts.filter(a => a.collection.pagination.totalCount > 0).length
    },
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
  margin-left: 1rem;
}
</style>
