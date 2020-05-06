<template>
  <div class="list">
    <div class="list-header" @click="toggleLeads" :style="listHeaderBorder">
      <img class="icon" src="@/assets/images/toc.svg" alt="icon" />
      <span class="list-title"> {{ list.title }} </span>
      <span class="list-length"> {{ numOfLeads }} {{ numOfLeads === 1 ? 'Lead' : 'Leads' }}</span>
    </div>
    <div class="list-leads" v-if="showLeads">
      <ComponentLoadingSVG v-if="trueList.refreshing" />
      <Lead v-else v-for="lead in trueList.list" :key="lead.id" :lead="lead" />
    </div>
  </div>
</template>

<script>
import LeadModel from '@/services/leads'
import CollectionManager from '@/services/collectionManager'
import Lead from '@/components/leads-index/Lead'

export default {
  name: 'List',
  props: {
    list: {
      // the prop 'list' is a shell: it only includes id, title, and leadCount. It is used to retrieve the trueList
      type: Object,
      required: true,
    },
  },
  components: {
    Lead,
  },
  data() {
    return {
      showLeads: false,
      madeInitialRetrieval: false,
      trueList: CollectionManager.create({
        ModelClass: LeadModel,
        filters: { byList: this.list.id },
      }),
    }
  },
  methods: {
    toggleLeads() {
      if (!this.madeInitialRetrieval) {
        this.trueList.refresh().then(() => {
          this.madeInitialRetrieval = true
        })
      }
      this.showLeads = !this.showLeads
    },
  },
  computed: {
    numOfLeads() {
      return this.list.leadCount
    },
    listHeaderBorder() {
      return {
        border: this.showLeads ? '2px solid #fafafa' : '2px solid white', // $off-white || $white
      }
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
</style>
