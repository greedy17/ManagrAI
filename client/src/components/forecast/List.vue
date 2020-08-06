<template>
  <div class="list">
    <div
      ref="listHeader"
      class="list-header"
      @click="toggleLeads"
      :class="{ open: showLeads, closed: !showLeads }"
    >
      <img class="icon" src="@/assets/images/toc.svg" alt="icon" />
      <span class="list-title"> {{ title }} </span>
      <span class="list-length">
        {{ numOfLeads }}
        {{ numOfLeads > 1 || numOfLeads === 0 ? 'Opportunities' : 'Opportunity' }}
      </span>
      <span class="list-value">{{ totalValue | currency }}</span>
    </div>

    <div class="list-leads" v-if="showLeads">
      <ComponentLoadingSVG v-if="collection.refreshing" style="margin: 1rem auto;" />
      <template v-else>
        <div :key="lead.id" class="list-leads__row" v-for="lead in collection.list">
          <LeadRow :key="lead.id" :lead="lead.leadRef">
            <template v-slot:left> </template>
            <template v-slot:center>
              <div class="lead-items">
                <span class="muted">
                  Expected Close By: <br />
                  {{ lead.expectedCloseDate | dateShort }}
                </span>
              </div>
            </template>
            <template v-slot:right> </template>
          </LeadRow>
        </div>
        <Pagination
          v-if="!collection.refreshing"
          style="margin-bottom: 1rem;"
          :collection="collection"
          @start-loading="startPaginationLoading($refs.listHeader)"
        />
      </template>
    </div>
  </div>
</template>

<script>
import Forecast from '@/services/forecasts'
import Lead from '@/components/forecast/Lead'
import LoadMoreButton from '@/components/shared/LoadMoreButton'
import LeadRow from '@/components/shared/LeadRow'
import Pagination from '@/components/shared/Pagination'
import { paginationMixin } from '@/services/pagination'

export default {
  name: 'List',
  mixins: [paginationMixin],
  props: {
    collection: {
      type: Object,
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
  },
  components: {
    Lead,
    LoadMoreButton,
    LeadRow,
    Pagination,
  },
  data() {
    return {
      showLeads: false,
      leadsList: this.collection.list ? this.collection.list : [],
    }
  },

  methods: {
    toggleLeads() {
      if (this.numOfLeads > 0) {
        this.showLeads = !this.showLeads
      }
    },
  },
  computed: {
    numOfLeads() {
      return this.collection.pagination.totalCount
    },
    totalValue() {
      return this.collection.list.reduce((sum, forecast) => {
        if (forecast.forecast === Forecast.CLOSED) {
          return forecast.leadRef.closingAmount + sum
        } else {
          return forecast.leadRef.amount + sum
        }
      }, 0)
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.list-header {
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

.lead-items {
  display: flex;
  align-items: center;
  > * {
    width: 150px;
  }
  .muted {
    font-size: 10px;
    color: black;
  }
}

.list-title {
  font-weight: bold;
  width: 20rem;
  max-width: 20rem;
  margin-left: 0.75rem;
}

.list-length {
  align-self: left;
  width: 25rem;
}

.list-leads {
  margin-left: 1%;
  margin-right: 1%;
  padding-top: 0.5rem;
  &__row {
    margin-top: 1rem;
  }
}
</style>
