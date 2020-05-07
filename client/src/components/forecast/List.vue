<template>
  <div class="list">
    <div class="list-header" @click="toggleLeads" :style="listHeaderBorder">
      <img class="icon" src="@/assets/images/toc.svg" alt="icon" />
      <span class="list-title"> {{ title }} </span>
      <span class="list-length"> {{ numOfLeads }} {{ numOfLeads === 1 ? 'Lead' : 'Leads' }}</span>
    </div>
    <div class="list-leads" v-if="showLeads">
      <Lead
        v-for="forecast in list.list"
        :key="forecast.id"
        :lead="forecast.leadRef"
        :leadForecast="forecast.forecast"
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
    list: {
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
      this.showLeads = !this.showLeads
    },
    loadMore() {
      alert('WIP')
    },
  },
  computed: {
    numOfLeads() {
      return this.list.pagination.totalCount
    },
    listHeaderBorder() {
      return {
        border: this.showLeads ? '2px solid #fafafa' : '2px solid white', // $off-white || $white
      }
    },
    moreToLoad() {
      return !!this.list.pagination.next
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

.icon {
  height: 1.625rem;
  width: 1.625rem;
  display: block;
}

.list-title {
  font-weight: bold;
  align-self: center;
  width: 25%;
  margin-left: 0.75rem;
}

.list-length {
  align-self: center;
  margin-left: 20%;
  margin-right: auto;
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
