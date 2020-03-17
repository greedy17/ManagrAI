<template>
  <div class="list">
    <div class="list-header" @click="toggleLeads" :style="listHeaderBorder">
      <img class="icon" src="/list-header.svg" />
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
.list-header {
  display: flex;
  flex-flow: row;
  align-items: stretch;
  margin: 1vh 1%;
  padding-left: 1%;

  &:hover {
    cursor: pointer;
  }
}

.icon {
  height: 40px;
  width: 40px;
  display: block;
}

.list-title {
  align-self: center;
  width: 25%;
}
.list-length {
  align-self: center;
  margin-left: 10%;
  margin-right: auto;
}

.list-leads {
  margin-left: 1%;
  margin-right: 1%;
}
</style>
