<template>
  <div class="list">
    <div class="list-header" @click="toggleLeads" :class="{ open: showLeads, closed: !showLeads }">
      <img class="icon" src="@/assets/images/toc.svg" alt="icon" />
      <span class="list-title"> {{ title }} </span>
      <span class="list-length"> {{ numOfLeads }} {{ numOfLeads === 1 ? 'Lead' : 'Leads' }}</span>
      <span class="list-value">{{ totalValue | currency }}</span>
    </div>
    <div class="list-leads" v-if="showLeads">
      <Lead
        v-for="forecast in collection.list"
        :key="forecast.id"
        :forecast="forecast"
        :lead="forecast.leadRef"
        @delete-lead="deleteLead"
      />
      <button v-if="moreToLoad" class="load-more-button" @click="loadMore">
        Load More
      </button>
    </div>
  </div>
</template>

<script>
import Lead from '@/components/forecast/Lead'

export default {
  name: 'List',
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
  },
  data() {
    return {
      showLeads: false,
    }
  },
  methods: {
    toggleLeads() {
      if (this.numOfLeads > 0) {
        this.showLeads = !this.showLeads
      }
    },
    deleteLead(id) {
      // NOTE (Bruno 5-7-20): this is incomplete, as just deleting a Lead from a ForecastList is not enough,
      // it should also be added to another ForecastList, and that list's leadCount should also be updated
      this.collection.list = this.collection.list.filter(forecast => forecast.lead !== id)
      this.collection.pagination.totalCount -= 1
    },
    loadMore() {
      alert('WIP')
    },
  },
  computed: {
    numOfLeads() {
      return this.collection.pagination.totalCount
    },
    totalValue() {
      return this.collection.list.reduce((sum, e) => e.leadRef.amount + sum, 0)
    },
    moreToLoad() {
      return !!this.collection.pagination.next
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/buttons';
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
}

.load-more-button {
  @include primary-button();
  margin: 0.5rem auto;
}
</style>
