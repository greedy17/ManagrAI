<template>
  <div class="list">
    <div class="list-header" @click="toggleLeads" :style="listHeaderBorder">
      <img class="icon" src="@/assets/images/toc.svg" alt="icon" />
      <span class="list-title">{{ title }}</span>
      <span class="list-length"> {{ numOfLeads }} {{ numOfLeads === 1 ? 'Lead' : 'Leads' }}</span>
    </div>
    <div class="list-leads" v-if="showLeads">
      <Lead v-for="lead in collection.list" :key="lead.id" :lead="lead" />
    </div>
  </div>
</template>

<script>
import Lead from '@/components/leads-index/Lead'

export default {
  name: 'CustomList', // such as NoList and AllLeads
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
      this.showLeads = !this.showLeads
    },
  },
  computed: {
    numOfLeads() {
      return this.collection.pagination.totalCount
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
