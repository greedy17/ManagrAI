<template>
  <div class="account">
    <div
      ref="header"
      class="header"
      @click="toggleLeads"
      :class="{ open: showLeads, closed: !showLeads }"
    >
      <img class="icon" src="@/assets/images/toc.svg" alt="icon" />
      <span class="account-title">{{ account.name }}</span>
      <span class="leads-count">
        {{ account.leadCount }}
        {{ 'Opportunity' | pluralize(account.leadCount) }}
      </span>
    </div>
    <div class="leads-container" v-if="showLeads">
      <ComponentLoadingSVG v-if="leads.refreshing" style="margin: 1rem auto;" />
      <div v-else-if="leads.pagination.totalCount > 0" class="accLeads">
        <Lead v-for="lead in leads.list" :key="lead.id" :lead="lead" />
        <Pagination
          v-if="!leads.refreshing"
          style="margin-bottom: 1rem;"
          :collection="leads"
          @start-loading="startPaginationLoading($refs.header)"
        />
      </div>
      <div v-else class="no-items-message">No Opportunities for this account</div>
    </div>
  </div>
</template>

<script>
import Lead from '@/components/prospect/Lead'
import Pagination from '@/components/shared/Pagination'

import CollectionManager from '@/services/collectionManager'
import LeadModel from '@/services/leads'
import { paginationMixin } from '@/services/pagination'

export default {
  name: 'Account',
  mixins: [paginationMixin],
  props: {
    account: {
      type: Object,
      required: true,
    },
    leadFilters: {
      type: Object,
      required: true,
    },
  },
  components: {
    Lead,
    Pagination,
  },
  data() {
    return {
      showLeads: false,
      madeInitialRetrieval: false,
      leads: CollectionManager.create({
        ModelClass: LeadModel,
        filters: { byAccount: this.account.id, ...this.leadFilters },
      }),
    }
  },
  watch: {
    leadFilters: {
      deep: true,
      async handler() {
        this.madeInitialRetrieval = false
        this.showLeads = false
      },
    },
  },
  methods: {
    toggleLeads() {
      if (!this.madeInitialRetrieval) {
        this.leads.refresh().finally(() => {
          this.madeInitialRetrieval = true
        })
      }
      this.showLeads = !this.showLeads
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
  margin-left: 1%;
  margin-right: 1%;
  margin-top: 1rem;
}

.no-items-message {
  align-self: center;
  width: 25%;
  margin-left: 0.75rem;
  margin-bottom: 1rem;
}
</style>
