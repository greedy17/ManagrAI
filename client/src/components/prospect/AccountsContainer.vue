<template>
  <div>
    <ComponentLoadingSVG v-if="accounts.refreshing" style="margin-top: 10vh;" />
    <div v-else-if="!accounts.list.length && isFilteringActive" class="lists-container-message">
      No Results!
    </div>
    <div v-else-if="!accounts.list.length" class="lists-container-message">
      No Accounts
    </div>
    <template v-else>
      <div class="accounts-container" ref="accountsContainer">
        <Account
          v-for="account in accounts.list"
          :key="account.id"
          :account="account"
          :leadFilters="leadFilters"
        />
      </div>
      <Pagination
        style="margin-top: 0.5rem; width: 80vw;"
        :collection="accounts"
        :model="'Account'"
        @start-loading="startPaginationLoading()"
      />
    </template>
  </div>
</template>

<script>
import Account from '@/components/prospect/Account'
import Pagination from '@/components/shared/Pagination'

import { paginationMixin } from '@/services/pagination'

export default {
  name: 'AccountsContainer',
  mixins: [paginationMixin],
  props: {
    accounts: {
      type: Object,
      required: true,
    },
    leadFilters: {
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

.lists-container-message {
  padding-top: 22vh;
  text-align: center;
  color: $gray;
  font-size: 1rem;
  font-weight: 600;
}
</style>
