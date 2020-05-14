<template>
  <div class="account">
    <PageLoadingSVG v-if="refreshing" />

    <div class="header" @click="toggleLeads" :class="{ open: showLeads, closed: !showLeads }">
      <img class="icon" src="@/assets/images/toc.svg" alt="icon" />
      <span class="account-title"> {{ account.name }} </span>
      <span class="leads-count">
        {{ account.leadCount }} {{ account.leadCount === 1 ? 'Lead' : 'Leads' }}</span
      >
    </div>
    <div class="leads-container" v-if="showLeads">
      <div v-if="accLeads.pagination.totalCount > 0" class="accLeads">
        <Lead v-for="lead in accLeads.list" :key="lead.id" :lead="lead" />
      </div>
      <div v-else class="no-items-message">
        No Leads for this account
      </div>
    </div>
  </div>
</template>

<script>
import Lead from '@/components/prospect/Lead'
import LeadModel from '@/services/leads'
import CollectionManager from '@/services/collectionManager'
import { debounce } from '@/services/utils'

export default {
  name: 'Account',
  props: {
    account: {
      type: Object,
      default: () => {},
    },
  },
  components: {
    Lead,
  },
  data() {
    return {
      showLeads: false,
      accLeads: CollectionManager.create({
        ModelClass: LeadModel,
        filters: {
          // for this filter by adding the (-) minus symbol to a filter you can exclude it from the filter
          byAccount: this.account.id,
        },
      }),
    }
  },
  created() {},
  methods: {
    async toggleLeads() {
      this.showLeads = !this.showLeads
      if (this.showLeads) {
        await this.accLeads.refresh()
      }
    },
  },
  computed: {
    refreshing() {
      return this.accLeads.refreshing
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.header {
  @include disable-text-select();
  @include pointer-on-hover();
  @include base-font-styles();
  display: flex;
  flex-flow: row;
  align-items: center;
  margin: 1vh 1%;
  padding-left: 1%;
  height: 3rem;
  font-size: 14px;
  line-height: 1.14;
  color: $main-font-gray;
}

.open {
  border: 2px solid $off-white;
}

.closed {
  border: 2px solid $white;
}

.icon {
  height: 1.625rem;
  width: 1.625rem;
  display: block;
}

.account-title {
  font-weight: bold;
  align-self: center;
  width: 25%;
  margin-left: 0.75rem;
}

.leads-count {
  align-self: center;
  margin-left: 20%;
  margin-right: auto;
}

.leads-container {
  margin-left: 2%;
  margin-right: 1%;
}

.no-items-message {
  font-weight: bold;
  align-self: center;
  width: 25%;
  margin-left: 0.75rem;
}
</style>
