<template>
  <div class="list">
    <div class="list-header" @click="toggleLeads" :style="listHeaderBorder">
      <img class="icon" src="@/assets/images/toc.svg" alt="content icon" />
      <span class="list-title"> {{ list.title }} </span>
      <span class="list-length"> {{ numOfLeads }} {{ numOfLeads === 1 ? 'Lead' : 'Leads' }}</span>
    </div>
    <div class="list-leads" v-if="showLeads">
      <Lead v-for="lead in list.leads" :key="lead.id" :lead="lead" />
    </div>
  </div>
</template>

<script>
import Lead from '@/components/leads-index/Lead'

export default {
  name: 'List',
  props: ['list'],
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
      return this.list.leads.length
    },
    listHeaderBorder() {
      return this.showLeads
        ? { borderWidth: '2px', borderStyle: 'solid', borderColor: '#fafafa' }
        : { borderWidth: '0 0 2px 0', borderStyle: 'solid', borderColor: '#fafafa' }
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
  display: flex;
  flex-flow: row;
  align-items: center;
  margin: 1vh 1%;
  padding-left: 1%;
  height: 49px;
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 14px;
  font-weight: normal;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.14;
  letter-spacing: normal;
  color: $main-font-gray;
}

.icon {
  height: 26px;
  width: 26px;
  display: block;
}

.list-title {
  font-weight: bold;
  align-self: center;
  width: 25%;
  margin-left: 11px;
}

.list-length {
  align-self: center;
  margin-left: 20%;
  margin-right: auto;
}

.list-leads {
  margin-left: 1%;
  margin-right: 1%;
}
</style>
